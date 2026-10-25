import os
import logging
from pathlib import Path
from django.conf import settings
from curriculum.models import Course

logger = logging.getLogger(__name__)


def generate_prereq_chart(curriculum_version):
    """
    Generates a directed prerequisite dependency graph for a curriculum version using Graphviz.
    Returns the absolute path to the rendered image, or None if:
    - There are no prerequisites defined
    - Graphviz is not installed or the dot executable is unavailable
    - Any rendering error occurs (graceful fallback)
    """
    try:
        courses = Course.objects.filter(
            semester__curriculum_version=curriculum_version
        ).prefetch_related('prerequisites', 'semester').order_by('semester__year', 'semester__semester', 'code')

        # Check if there are any prerequisite dependencies defined
        has_prereqs = any(course.prerequisites.exists() for course in courses)
        if not has_prereqs:
            logger.info("No course prerequisites found for version %s; skipping visual chart.", curriculum_version)
            return None

        try:
            import graphviz
        except ImportError:
            logger.warning("Graphviz Python package is not available. Using fallback table.")
            return None

        # Build Graphviz Digraph
        dot = graphviz.Digraph(
            name=f"prereq_{curriculum_version.pk}",
            format='png',
            comment=f"Prerequisites for {curriculum_version}"
        )
        dot.attr(rankdir='LR', size='10,6', ratio='compress', dpi='180')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='#e8f0fb', color='#003366', fontname='Helvetica', fontsize='9')
        dot.attr('edge', color='#4a5568', arrowhead='vee', arrowsize='0.8')

        semesters = curriculum_version.semesters.order_by('year', 'semester')
        for sem in semesters:
            sem_courses = [c for c in courses if c.semester_id == sem.id]
            if sem_courses:
                with dot.subgraph(name=f"cluster_sem_{sem.id}") as sub:
                    sub.attr(label=f"Year {sem.year} - Sem {sem.semester}", color='#cbd5e1', style='dashed', fontname='Helvetica-Bold', fontsize='9')
                    for c in sem_courses:
                        label = f"{c.code}\n({c.credits} cr)"
                        sub.node(c.code, label=label)

        # Add directed edges: Prerequisite -> Course
        for course in courses:
            for prereq in course.prerequisites.all():
                dot.edge(prereq.code, course.code)

        chart_dir = Path(settings.PREREQ_CHART_DIR)
        chart_dir.mkdir(parents=True, exist_ok=True)

        chart_base = chart_dir / f"prereq_{curriculum_version.pk}"
        rendered_path = dot.render(
            filename=str(chart_base),
            cleanup=True
        )

        if os.path.exists(rendered_path):
            return str(rendered_path)

        return None

    except Exception as e:
        logger.warning("Graphviz chart generation encountered an error: %s. Using fallback table.", e)
        return None
