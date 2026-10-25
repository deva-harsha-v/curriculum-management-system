import os
import logging
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

from accounts.models import Profile
from curriculum.models import CurriculumVersion, AuditLog, log_action
from .generator import generate_curriculum_pdf

logger = logging.getLogger(__name__)


def _get_profile(request):
    try:
        return request.user.profile
    except Profile.DoesNotExist:
        return None


# ─────────────────────────────────────────────
# PDF Preview (inline in browser)
# ─────────────────────────────────────────────

@login_required
def pdf_preview(request, version_pk):
    """
    HOD-only: renders PDF inline in an iframe for preview before finalising.
    Faculty can view preview of published versions only.
    """
    profile = _get_profile(request)
    if not profile:
        return HttpResponseForbidden("No profile found.")

    version = get_object_or_404(CurriculumVersion, pk=version_pk)

    # Department isolation
    if not profile.is_admin and version.department != profile.department:
        return HttpResponseForbidden("You cannot access this department's curriculum.")

    # Faculty can only preview published versions
    if profile.is_faculty and version.status != CurriculumVersion.STATUS_PUBLISHED:
        return HttpResponseForbidden("Only HOD can preview draft curriculum.")

    return render(request, 'pdf_generator/preview.html', {
        'version': version,
        'profile': profile,
        'download_url': f'/pdf/download/{version_pk}/',
        'generate_url': f'/pdf/generate/{version_pk}/',
    })


# ─────────────────────────────────────────────
# Generate PDF (HOD only)
# ─────────────────────────────────────────────

@login_required
def pdf_generate(request, version_pk):
    """
    HOD-only: generates the PDF, saves to media/pdfs/, logs the action.
    On GET: shows confirmation page.
    On POST: generates and redirects to preview/download.
    """
    profile = _get_profile(request)
    if not profile or not (profile.is_hod or profile.is_admin):
        return HttpResponseForbidden("Only HOD can generate the official PDF.")

    version = get_object_or_404(CurriculumVersion, pk=version_pk)

    if not profile.is_admin and version.department != profile.department:
        return HttpResponseForbidden("You cannot access this department's curriculum.")

    if request.method == 'POST':
        try:
            # Build output path
            pdf_dir = Path(settings.PDF_OUTPUT_DIR)
            pdf_dir.mkdir(parents=True, exist_ok=True)

            safe_name = (
                f"{version.department.code}_{version.regulation}"
                f"_{version.academic_year.replace('-', '_')}.pdf"
            )
            output_path = pdf_dir / safe_name

            generate_curriculum_pdf(version, output_path=str(output_path))

            # Log the action
            log_action(
                user=request.user,
                department=version.department,
                action=AuditLog.ACTION_GENERATE_PDF,
                model_name='CurriculumVersion',
                record_id=version.pk,
                record_label=str(version),
                description=f"PDF generated: {safe_name}",
                curriculum_version=version,
            )

            messages.success(
                request,
                f"PDF generated successfully: {safe_name}"
            )
            return redirect('pdf_generator:pdf_download', version_pk=version_pk)

        except Exception as e:
            logger.exception("PDF generation failed for version %s", version_pk)
            messages.error(request, f"PDF generation failed: {str(e)}")
            return redirect('curriculum:version_detail', pk=version_pk)

    # GET — show confirmation
    return render(request, 'pdf_generator/generate_confirm.html', {
        'version': version,
        'profile': profile,
    })


# ─────────────────────────────────────────────
# Download PDF
# ─────────────────────────────────────────────

@login_required
def pdf_download(request, version_pk):
    """
    Streams the generated PDF as a download.
    HOD: can download any version of their dept.
    Faculty: can download published versions only.
    """
    profile = _get_profile(request)
    if not profile:
        return HttpResponseForbidden("No profile found.")

    version = get_object_or_404(CurriculumVersion, pk=version_pk)

    if not profile.is_admin and version.department != profile.department:
        return HttpResponseForbidden("Access denied.")

    if profile.is_faculty and version.status != CurriculumVersion.STATUS_PUBLISHED:
        return HttpResponseForbidden("Only published curriculum can be downloaded by faculty.")

    # Check if pre-generated file exists
    pdf_dir = Path(settings.PDF_OUTPUT_DIR)
    safe_name = (
        f"{version.department.code}_{version.regulation}"
        f"_{version.academic_year.replace('-', '_')}.pdf"
    )
    output_path = pdf_dir / safe_name

    if output_path.exists():
        with open(output_path, 'rb') as f:
            pdf_bytes = f.read()
    else:
        # Generate on the fly
        try:
            buf = generate_curriculum_pdf(version)
            pdf_bytes = buf.read()
        except Exception as e:
            logger.exception("Could not generate PDF on the fly for version %s", version_pk)
            messages.error(request, f"Could not generate PDF: {str(e)}")
            return redirect('curriculum:version_detail', pk=version_pk)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{safe_name}"'
    response['Content-Length'] = len(pdf_bytes)
    return response


# ─────────────────────────────────────────────
# Inline PDF stream (for iframe preview)
# ─────────────────────────────────────────────

@login_required
def pdf_stream(request, version_pk):
    """
    Streams PDF inline (for embedding in iframe on preview page).
    """
    profile = _get_profile(request)
    if not profile:
        return HttpResponseForbidden()

    version = get_object_or_404(CurriculumVersion, pk=version_pk)

    if not profile.is_admin and version.department != profile.department:
        return HttpResponseForbidden()

    if profile.is_faculty and version.status != CurriculumVersion.STATUS_PUBLISHED:
        return HttpResponseForbidden()

    pdf_dir = Path(settings.PDF_OUTPUT_DIR)
    safe_name = (
        f"{version.department.code}_{version.regulation}"
        f"_{version.academic_year.replace('-', '_')}.pdf"
    )
    output_path = pdf_dir / safe_name

    if output_path.exists():
        with open(output_path, 'rb') as f:
            pdf_bytes = f.read()
    else:
        try:
            buf = generate_curriculum_pdf(version)
            pdf_bytes = buf.read()
        except Exception as e:
            return HttpResponse(
                f"<p>PDF not yet generated. <a href='/pdf/generate/{version_pk}/'>Generate now</a></p>",
                content_type='text/html'
            )

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{safe_name}"'
    return response