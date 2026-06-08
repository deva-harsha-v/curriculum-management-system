"""
PDF Generator for NIT AP Curriculum Documents
Generates a complete curriculum PDF matching the official university format.

Sections generated:
  1.  Cover Page
  2.  Institute Vision & Mission
  3.  Department Vision & Mission
  4.  Graduate Attributes
  5.  PEO Table
  6.  Mission → PEO Mapping Table
  7.  PEO → GA Mapping Table
  8.  Program Outcomes Table
  9.  PO → PEO Mapping Table
  10. Curricular Components (Credit Summary)
  11. Scheme of Instruction (all semesters)
  12. Pre-requisite Chart (Graphviz)
  13. Detailed Syllabus (per course)
"""

import os
import io
from pathlib import Path
from django.conf import settings

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas

from .styles import (
    get_styles, CONTENT_WIDTH, LEFT_MARGIN, RIGHT_MARGIN,
    TOP_MARGIN, BOTTOM_MARGIN, PAGE_WIDTH, PAGE_HEIGHT,
    TABLE_HEADER, base_table_style, header_table_style,
    mapping_table_style, semester_table_style,
    course_header_style, peo_table_style, po_table_style,
)


# ─────────────────────────────────────────────
# Page number canvas
# ─────────────────────────────────────────────

class _NumberedCanvas(rl_canvas.Canvas):
    """Adds page numbers to every page."""
    def __init__(self, *args, **kwargs):
        rl_canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(num_pages)
            rl_canvas.Canvas.showPage(self)
        rl_canvas.Canvas.save(self)

    def _draw_page_number(self, page_count):
        page_num = self._saved_page_states.index(dict(self.__dict__)) + 1
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#666666'))
        self.drawCentredString(
            PAGE_WIDTH / 2,
            BOTTOM_MARGIN / 2,
            f"Page {page_num} of {page_count}"
        )


def _on_first_page(canvas, doc):
    pass


def _on_later_pages(canvas, doc):
    pass


# ─────────────────────────────────────────────
# Main Generator
# ─────────────────────────────────────────────

class CurriculumPDFGenerator:
    def __init__(self, curriculum_version):
        self.version = curriculum_version
        self.styles = get_styles()
        self.story = []

    def generate(self, output_path=None):
        """
        Generate PDF and write to output_path.
        If output_path is None, returns BytesIO buffer.
        """
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            buf = output_path
        else:
            buf = io.BytesIO()

        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
            title=f"Curriculum – {self.version}",
            author=self.version.institute_name,
        )

        self._build_story()

        doc.build(
            self.story,
            onFirstPage=_on_first_page,
            onLaterPages=_on_later_pages,
            canvasmaker=_NumberedCanvas,
        )

        if not output_path:
            buf.seek(0)
            return buf

        return output_path

    # ─────────────────────────────────────────
    def _build_story(self):
        s = self.story
        v = self.version

        self._add_cover_page()
        s.append(PageBreak())

        self._add_vision_mission()
        s.append(PageBreak())

        self._add_graduate_attributes()
        s.append(PageBreak())

        self._add_peo_section()
        s.append(PageBreak())

        self._add_peo_ga_mapping()
        s.append(PageBreak())

        self._add_program_outcomes()
        s.append(PageBreak())

        self._add_po_peo_mapping()
        s.append(PageBreak())

        self._add_credit_summary()
        s.append(PageBreak())

        self._add_scheme_of_instruction()
        s.append(PageBreak())

        self._add_prereq_chart()
        s.append(PageBreak())

        self._add_detailed_syllabus()

    # ─────────────────────────────────────────
    # 1. Cover Page
    # ─────────────────────────────────────────
    def _add_cover_page(self):
        s = self.story
        v = self.version

        s.append(Spacer(1, 5 * cm))

        s.append(Paragraph(v.institute_name.upper(), self.styles['cover_institute']))

        s.append(Spacer(1, 4 * cm))

        s.append(Paragraph("SCHEME OF INSTRUCTION AND SYLLABI", self.styles['cover_title']))
        s.append(Paragraph("FOR B.TECH PROGRAM", self.styles['cover_title']))

        s.append(Spacer(1, 1.5 * cm))

        s.append(Paragraph(f"Effective from {v.academic_year}", self.styles['cover_subtitle']))

        s.append(Spacer(1, 1.5 * cm))

        dept_label = f"DEPARTMENT OF {v.department.name.upper()}"
        s.append(Paragraph(dept_label, self.styles['cover_dept']))

        if v.regulation:
            s.append(Spacer(1, 0.5 * cm))
            s.append(Paragraph(f"Regulation: {v.regulation}", self.styles['cover_subtitle']))

    # ─────────────────────────────────────────
    # 2 & 3. Vision & Mission
    # ─────────────────────────────────────────
    def _add_vision_mission(self):
        s = self.story
        v = self.version

        # Institute section
        s.append(Paragraph(
            v.institute_name.upper(),
            self.styles['subsection_heading']
        ))

        s.append(Paragraph("VISION", self.styles['subsection_heading']))
        if v.institute_vision:
            s.append(Paragraph(v.institute_vision, self.styles['body']))

        s.append(Spacer(1, 0.3 * cm))
        s.append(Paragraph("MISSION", self.styles['subsection_heading']))

        missions = v.institute_mission if isinstance(v.institute_mission, list) else []
        for mission in missions:
            s.append(Paragraph(f"• {mission}", self.styles['bullet']))

        s.append(Spacer(1, 0.8 * cm))

        # Department section
        dept_label = f"DEPARTMENT OF {v.department.name.upper()}"
        s.append(Paragraph(dept_label, self.styles['subsection_heading']))

        s.append(Paragraph("VISION", self.styles['subsection_heading']))
        if v.dept_vision:
            s.append(Paragraph(v.dept_vision, self.styles['body']))

        s.append(Spacer(1, 0.3 * cm))
        s.append(Paragraph("MISSION", self.styles['subsection_heading']))

        dept_missions = v.dept_mission if isinstance(v.dept_mission, list) else []
        for mission in dept_missions:
            s.append(Paragraph(f"• {mission}", self.styles['bullet']))

    # ─────────────────────────────────────────
    # 4. Graduate Attributes
    # ─────────────────────────────────────────
    def _add_graduate_attributes(self):
        s = self.story
        v = self.version

        s.append(Paragraph("GRADUATE ATTRIBUTES", self.styles['left_heading']))

        if v.ga_intro:
            s.append(Paragraph(v.ga_intro, self.styles['body']))
        s.append(Spacer(1, 0.3 * cm))

        gas = v.graduate_attributes.order_by('number')
        for ga in gas:
            text = f"{ga.number}.\u2003<b>{ga.title}:</b> {ga.description}"
            s.append(Paragraph(text, self.styles['numbered_item']))

    # ─────────────────────────────────────────
    # 5. PEO Section
    # ─────────────────────────────────────────
    def _add_peo_section(self):
        s = self.story
        v = self.version

        dept_line = f"DEPARTMENT OF {v.department.name.upper()}"
        degree_line = f"{v.department.degree.upper()} IN {v.department.name.upper()}"
        s.append(Paragraph(dept_line, self.styles['subsection_heading']))
        s.append(Paragraph(degree_line, self.styles['subsection_heading']))
        s.append(Paragraph("PROGRAM EDUCATIONAL OBJECTIVES", self.styles['subsection_heading']))

        peos = v.peos.order_by('number')

        if not peos.exists():
            s.append(Paragraph("No PEOs defined.", self.styles['body']))
        else:
            col_widths = [1.2 * cm, CONTENT_WIDTH - 1.2 * cm]
            data = []
            for peo in peos:
                label = Paragraph(f"<b>PEO{peo.number}.</b>", self.styles['cell_bold_center'])
                desc = Paragraph(peo.description, self.styles['cell'])
                data.append([label, desc])

            tbl = Table(data, colWidths=col_widths, repeatRows=0)
            tbl.setStyle(TableStyle(peo_table_style()))
            s.append(tbl)

        s.append(Spacer(1, 0.6 * cm))

        # Mission → PEO mapping table
        self._add_mission_peo_table()

    def _add_mission_peo_table(self):
        s = self.story
        v = self.version

        mappings = v.mission_peo_mappings.order_by('mission_order')
        peos = v.peos.order_by('number')

        if not mappings.exists() or not peos.exists():
            return

        s.append(Paragraph(
            "Mapping of Mission statements with program educational objectives",
            self.styles['subsection_heading']
        ))

        peo_numbers = [p.number for p in peos]
        header = [Paragraph("<b>Mission Statement</b>", self.styles['cell_bold'])]
        for n in peo_numbers:
            header.append(Paragraph(f"<b>PEO{n}</b>", self.styles['cell_bold_center']))

        data = [header]
        mission_col_w = CONTENT_WIDTH * 0.55
        peo_col_w = (CONTENT_WIDTH - mission_col_w) / max(len(peo_numbers), 1)
        col_widths = [mission_col_w] + [peo_col_w] * len(peo_numbers)

        for m in mappings:
            row = [Paragraph(m.mission_statement, self.styles['cell'])]
            for n in peo_numbers:
                val = m.mappings.get(str(n), '') if isinstance(m.mappings, dict) else ''
                row.append(Paragraph(str(val) if val else '', self.styles['cell_center']))
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle(header_table_style()))
        s.append(tbl)

    # ─────────────────────────────────────────
    # 6. PEO → GA Mapping
    # ─────────────────────────────────────────
    def _add_peo_ga_mapping(self):
        s = self.story
        v = self.version

        peos = v.peos.order_by('number')
        gas = v.graduate_attributes.order_by('number')

        if not peos.exists() or not gas.exists():
            return

        s.append(Paragraph(
            "Mapping of program educational objectives with graduate attributes",
            self.styles['subsection_heading']
        ))

        ga_numbers = [ga.number for ga in gas]
        header = [Paragraph("<b>PEO</b>", self.styles['cell_bold_center'])]
        for n in ga_numbers:
            header.append(Paragraph(f"<b>GA{n}</b>", self.styles['cell_bold_center']))

        data = [header]

        peo_col_w = 1.2 * cm
        ga_col_w = (CONTENT_WIDTH - peo_col_w) / max(len(ga_numbers), 1)
        col_widths = [peo_col_w] + [ga_col_w] * len(ga_numbers)

        mapping_cache = {
            m.peo_id: m.mappings
            for m in v.peo_ga_mappings.select_related('peo').all()
        }

        for peo in peos:
            row = [Paragraph(f"<b>PEO{peo.number}</b>", self.styles['cell_bold_center'])]
            mmap = mapping_cache.get(peo.pk, {}) or {}
            for n in ga_numbers:
                val = mmap.get(str(n), '-')
                row.append(Paragraph(str(val) if val else '-', self.styles['cell_center']))
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle(mapping_table_style(len(data), len(col_widths))))
        s.append(tbl)

    # ─────────────────────────────────────────
    # 7. Program Outcomes
    # ─────────────────────────────────────────
    def _add_program_outcomes(self):
        s = self.story
        v = self.version

        pos = v.program_outcomes.order_by('number')

        if not pos.exists():
            return

        s.append(Paragraph(
            "<b>PROGRAM OUTCOMES:</b> At the end of the program the student will be able to:",
            self.styles['left_heading']
        ))

        col_widths = [1.2 * cm, CONTENT_WIDTH - 1.2 * cm]
        data = []
        for po in pos:
            label = Paragraph(f"<b>PO{po.number}</b>", self.styles['cell_bold_center'])
            desc = Paragraph(po.description, self.styles['cell'])
            data.append([label, desc])

        tbl = Table(data, colWidths=col_widths)
        tbl.setStyle(TableStyle(po_table_style()))
        s.append(tbl)

    # ─────────────────────────────────────────
    # 8. PO → PEO Mapping
    # ─────────────────────────────────────────
    def _add_po_peo_mapping(self):
        s = self.story
        v = self.version

        pos = v.program_outcomes.order_by('number')
        peos = v.peos.order_by('number')

        if not pos.exists() or not peos.exists():
            return

        s.append(Paragraph(
            "Mapping of program outcomes with program educational objectives",
            self.styles['subsection_heading']
        ))

        peo_numbers = [p.number for p in peos]
        header = [Paragraph("<b>PO</b>", self.styles['cell_bold_center'])]
        for n in peo_numbers:
            header.append(Paragraph(f"<b>PEO{n}</b>", self.styles['cell_bold_center']))

        data = [header]

        po_col_w = 1.2 * cm
        peo_col_w = (CONTENT_WIDTH - po_col_w) / max(len(peo_numbers), 1)
        col_widths = [po_col_w] + [peo_col_w] * len(peo_numbers)

        mapping_cache = {
            m.program_outcome_id: m.mappings
            for m in v.po_peo_mappings.select_related('program_outcome').all()
        }

        for po in pos:
            row = [Paragraph(f"<b>{po.number}</b>", self.styles['cell_bold_center'])]
            mmap = mapping_cache.get(po.pk, {}) or {}
            for n in peo_numbers:
                val = mmap.get(str(n), '')
                row.append(Paragraph(str(val) if val else '', self.styles['cell_center']))
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle(mapping_table_style(len(data), len(col_widths))))
        s.append(tbl)

    # ─────────────────────────────────────────
    # 9. Curricular Components / Credit Summary
    # ─────────────────────────────────────────
    def _add_credit_summary(self):
        s = self.story
        v = self.version

        categories = v.course_categories.order_by('display_order')
        if not categories.exists():
            return

        s.append(Paragraph("CURRICULAR COMPONENTS", self.styles['section_heading']))
        degree_line = f"Degree Requirements for {v.department.degree} in {v.department.name}"
        s.append(Paragraph(degree_line, self.styles['subsection_heading']))

        col_widths = [CONTENT_WIDTH * 0.55, CONTENT_WIDTH * 0.22, CONTENT_WIDTH * 0.23]

        header = [
            Paragraph("<b>Category of Courses</b>", self.styles['cell_bold_center']),
            Paragraph("<b>Credits Offered</b>", self.styles['cell_bold_center']),
            Paragraph("<b>Min. credits to be earned</b>", self.styles['cell_bold_center']),
        ]
        data = [header]

        total_offered = 0
        total_min = 0
        for cat in categories:
            row = [
                Paragraph(f"{cat.name}  ({cat.code})", self.styles['cell']),
                Paragraph(str(cat.credits_offered).zfill(2), self.styles['cell_center']),
                Paragraph(str(cat.min_credits).zfill(2), self.styles['cell_center']),
            ]
            data.append(row)
            total_offered += cat.credits_offered
            total_min += cat.min_credits

        data.append([
            Paragraph("<b>Total</b>", self.styles['cell_bold_center']),
            Paragraph(f"<b>{total_offered}</b>", self.styles['cell_bold_center']),
            Paragraph(f"<b>{total_min}</b>", self.styles['cell_bold_center']),
        ])

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        style = header_table_style()
        style += [
            ('BACKGROUND', (0, -1), (-1, -1), TABLE_HEADER),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]
        tbl.setStyle(TableStyle(style))
        s.append(tbl)

    # ─────────────────────────────────────────
    # 10. Scheme of Instruction
    # ─────────────────────────────────────────
    def _add_scheme_of_instruction(self):
        s = self.story
        v = self.version

        s.append(Paragraph("SCHEME OF INSTRUCTION", self.styles['section_heading']))

        degree_label = f"{v.department.degree} ({v.department.name}) Course Structure"
        s.append(Paragraph(degree_label, self.styles['subsection_heading']))

        semesters = v.semesters.order_by('year', 'semester').prefetch_related(
            'courses__category'
        )

        for sem in semesters:
            sem_label = f"B.Tech {sem.get_year_display()} - {sem.get_semester_display()}"
            s.append(Spacer(1, 0.4 * cm))
            s.append(Paragraph(sem_label, self.styles['subsection_heading']))

            courses = sem.courses.order_by('display_order', 'code')
            if not courses.exists():
                s.append(Paragraph("No courses added.", self.styles['body']))
                continue

            col_widths = [
                0.8 * cm,   # S.No
                2.0 * cm,   # Course Code
                CONTENT_WIDTH - 0.8 - 2.0 - 1.0 - 1.0 - 1.0 - 1.8 - 1.8,  # Title
                1.0 * cm,   # L
                1.0 * cm,   # T
                1.0 * cm,   # P
                1.8 * cm,   # Credits
                1.8 * cm,   # Cat. Code
            ]
            col_widths[3] = CONTENT_WIDTH - sum(col_widths[:3]) - sum(col_widths[4:])

            header_row = [
                Paragraph("<b>S. No.</b>", self.styles['cell_bold_center']),
                Paragraph("<b>Course Code</b>", self.styles['cell_bold_center']),
                Paragraph("<b>Course Title</b>", self.styles['cell_bold_center']),
                Paragraph("<b>L</b>", self.styles['cell_bold_center']),
                Paragraph("<b>T</b>", self.styles['cell_bold_center']),
                Paragraph("<b>P</b>", self.styles['cell_bold_center']),
                Paragraph("<b>Credits</b>", self.styles['cell_bold_center']),
                Paragraph("<b>Cat. Code</b>", self.styles['cell_bold_center']),
            ]

            data = [header_row]
            total_l = total_t = total_p = total_credits = 0

            for idx, course in enumerate(courses, start=1):
                cat_code = course.category.code if course.category else ''
                data.append([
                    Paragraph(str(idx), self.styles['cell_center']),
                    Paragraph(course.code, self.styles['cell_center']),
                    Paragraph(course.title, self.styles['cell']),
                    Paragraph(str(course.lectures), self.styles['cell_center']),
                    Paragraph(str(course.tutorials), self.styles['cell_center']),
                    Paragraph(str(course.practicals), self.styles['cell_center']),
                    Paragraph(str(course.credits), self.styles['cell_center']),
                    Paragraph(cat_code, self.styles['cell_center']),
                ])
                total_l += course.lectures
                total_t += course.tutorials
                total_p += course.practicals
                total_credits += course.credits

            data.append([
                Paragraph('', self.styles['cell']),
                Paragraph('', self.styles['cell']),
                Paragraph("<b>TOTAL</b>", self.styles['cell_bold_center']),
                Paragraph(f"<b>{total_l}</b>", self.styles['cell_bold_center']),
                Paragraph(f"<b>{total_t}</b>", self.styles['cell_bold_center']),
                Paragraph(f"<b>{total_p}</b>", self.styles['cell_bold_center']),
                Paragraph(f"<b>{total_credits}</b>", self.styles['cell_bold_center']),
                Paragraph('', self.styles['cell']),
            ])

            tbl = Table(data, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(TableStyle(semester_table_style()))
            s.append(tbl)

            if sem.year != 4 or sem.semester != 2:
                s.append(PageBreak())

    # ─────────────────────────────────────────
    # 11. Pre-requisite Chart
    # ─────────────────────────────────────────
    def _add_prereq_chart(self):
        s = self.story
        v = self.version

        s.append(Paragraph(f"{v.department.degree.upper()} IN {v.department.name.upper()}", self.styles['section_heading']))
        s.append(Paragraph("PRE-REQUISITE CHART", self.styles['section_heading']))

        # Try Graphviz
        chart_path = None
        try:
            from .prereq_chart import generate_prereq_chart
            chart_path = generate_prereq_chart(v)
        except Exception:
            pass

        if chart_path and os.path.exists(chart_path):
            available_height = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN - 3 * cm
            img = Image(chart_path, width=CONTENT_WIDTH, height=available_height)
            img.hAlign = 'CENTER'
            s.append(img)
        else:
            # Fallback: text-based dependency table
            s.append(Spacer(1, 0.5 * cm))
            s.append(Paragraph(
                "Note: Install Graphviz to generate the visual prerequisite chart.",
                self.styles['body_center']
            ))
            self._add_prereq_table_fallback()

    def _add_prereq_table_fallback(self):
        """Text table fallback when Graphviz is not available."""
        s = self.story
        v = self.version

        from curriculum.models import Course
        courses = Course.objects.filter(
            semester__curriculum_version=v
        ).prefetch_related('prerequisites').order_by('semester__year', 'semester__semester', 'code')

        courses_with_prereqs = [c for c in courses if c.prerequisites.exists()]
        if not courses_with_prereqs:
            s.append(Paragraph("No prerequisites defined.", self.styles['body_center']))
            return

        col_widths = [CONTENT_WIDTH * 0.35, CONTENT_WIDTH * 0.65]
        data = [
            [Paragraph("<b>Course</b>", self.styles['cell_bold_center']),
             Paragraph("<b>Prerequisites</b>", self.styles['cell_bold_center'])],
        ]
        for course in courses_with_prereqs:
            prereq_list = ', '.join(p.code for p in course.prerequisites.all())
            data.append([
                Paragraph(f"{course.code} – {course.title}", self.styles['cell']),
                Paragraph(prereq_list, self.styles['cell']),
            ])

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle(header_table_style()))
        s.append(tbl)

    # ─────────────────────────────────────────
    # 12. Detailed Syllabus
    # ─────────────────────────────────────────
    def _add_detailed_syllabus(self):
        s = self.story
        v = self.version

        s.append(Paragraph("DETAILED SYLLABUS", self.styles['section_heading']))
        s.append(Spacer(1, 0.3 * cm))

        semesters = v.semesters.order_by('year', 'semester').prefetch_related(
            'courses__category',
            'courses__course_outcomes__po_mappings',
            'courses__references',
            'courses__prerequisites',
        )

        first_course = True
        for sem in semesters:
            courses = sem.courses.order_by('display_order', 'code')
            for course in courses:
                if not first_course:
                    s.append(PageBreak())
                first_course = False
                self._add_course_syllabus(course, v)

    def _add_course_syllabus(self, course, version):
        s = self.story

        # ── Course header table ────────────────
        cat_code = course.category.code if course.category else ''
        ltp = f"{course.lectures} – {course.tutorials} – {course.practicals}"
        credits_str = str(course.credits)

        header_data = [[
            Paragraph(f"<b>{course.code}</b>", self.styles['cell_bold_center']),
            Paragraph(f"<b>{course.title.upper()}</b>", self.styles['cell_bold_center']),
            Paragraph(f"<b>{cat_code}</b>", self.styles['cell_bold_center']),
            Paragraph(f"<b>{ltp}</b>", self.styles['cell_bold_center']),
            Paragraph(f"<b>{credits_str} Credits</b>", self.styles['cell_bold_center']),
        ]]
        header_col_widths = [
            1.6 * cm,
            CONTENT_WIDTH - 1.6 - 1.4 - 2.0 - 2.2,
            1.4 * cm,
            2.0 * cm,
            2.2 * cm,
        ]
        hdr_tbl = Table(header_data, colWidths=header_col_widths)
        hdr_tbl.setStyle(TableStyle(course_header_style()))
        s.append(hdr_tbl)
        s.append(Spacer(1, 0.2 * cm))

        # ── Pre-requisites ─────────────────────
        prereqs = course.prerequisites.all()
        prereq_text = ", ".join(p.code for p in prereqs) if prereqs else "None"
        s.append(Paragraph(
            f"<b>Pre-requisites:</b> {prereq_text}",
            self.styles['body_left']
        ))
        s.append(Spacer(1, 0.2 * cm))

        # ── Course Outcomes table ──────────────
        cos = course.course_outcomes.order_by('number')
        if cos.exists():
            s.append(Paragraph(
                "<b>Course Outcomes:</b> At the end of the course, the student will be able to:",
                self.styles['body_left']
            ))
            s.append(Spacer(1, 0.1 * cm))

            co_data = []
            for co in cos:
                co_data.append([
                    Paragraph(f"<b>CO{co.number}</b>", self.styles['cell_bold_center']),
                    Paragraph(co.description, self.styles['cell']),
                ])
            co_tbl = Table(
                co_data,
                colWidths=[1.2 * cm, CONTENT_WIDTH - 1.2 * cm]
            )
            co_tbl.setStyle(TableStyle(base_table_style()))
            s.append(co_tbl)
            s.append(Spacer(1, 0.3 * cm))

        # ── CO-PO Mapping Table ────────────────
        self._add_copo_table(course, version)

        # ── Detailed Syllabus text ─────────────
        if course.syllabus_text.strip():
            s.append(Paragraph("<b>Detailed Syllabus:</b>", self.styles['left_heading']))
            paragraphs = course.syllabus_text.strip().split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para:
                    s.append(Paragraph(para.replace('\n', ' '), self.styles['syllabus']))

        # ── References ────────────────────────
        refs = course.references.order_by('number')
        if refs.exists():
            s.append(Spacer(1, 0.2 * cm))
            s.append(Paragraph("<b>Reading:</b>", self.styles['left_heading']))
            for ref in refs:
                s.append(Paragraph(
                    f"{ref.number}.\u2003{ref.citation}",
                    self.styles['numbered_item']
                ))

    def _add_copo_table(self, course, version):
        s = self.story

        cos = course.course_outcomes.order_by('number')
        pos = version.program_outcomes.order_by('number')

        if not cos.exists() or not pos.exists():
            return

        s.append(Paragraph(
            "<b>Mapping of course outcomes with program outcomes</b>",
            self.styles['subsection_heading']
        ))

        po_numbers = [po.number for po in pos]

        header = [Paragraph("<b>Course Outcomes</b>", self.styles['cell_bold_center'])]
        for n in po_numbers:
            header.append(Paragraph(f"<b>PO{n}</b>", self.styles['cell_small']))

        data = [header]

        co_col_w = 2.2 * cm
        po_col_w = (CONTENT_WIDTH - co_col_w) / max(len(po_numbers), 1)
        col_widths = [co_col_w] + [po_col_w] * len(po_numbers)

        mapping_cache = {}
        for co in cos:
            try:
                mapping_cache[co.pk] = co.po_mappings.first().mappings if co.po_mappings.exists() else {}
            except Exception:
                mapping_cache[co.pk] = {}

        for co in cos:
            row = [Paragraph(f"<b>CO{co.number}</b>", self.styles['cell_bold_center'])]
            mmap = mapping_cache.get(co.pk, {}) or {}
            for n in po_numbers:
                val = mmap.get(str(n), '')
                row.append(Paragraph(str(val) if val else '', self.styles['cell_small']))
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle(mapping_table_style(len(data), len(col_widths))))
        s.append(tbl)
        s.append(Spacer(1, 0.3 * cm))


# ─────────────────────────────────────────────
# Public interface
# ─────────────────────────────────────────────

def generate_curriculum_pdf(curriculum_version, output_path=None):
    """
    Main entry point.
    Returns BytesIO if output_path is None, else writes to file and returns path.
    """
    gen = CurriculumPDFGenerator(curriculum_version)
    return gen.generate(output_path=output_path)