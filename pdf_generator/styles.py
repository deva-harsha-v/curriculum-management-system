from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import cm, mm
from reportlab.lib.pagesizes import A4

# ─────────────────────────────────────────────
# Page Dimensions
# ─────────────────────────────────────────────

PAGE_WIDTH, PAGE_HEIGHT = A4           # 595.27 x 841.89 points
LEFT_MARGIN   = 2.5 * cm
RIGHT_MARGIN  = 2.5 * cm
TOP_MARGIN    = 2.5 * cm
BOTTOM_MARGIN = 2.5 * cm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN   # ~490 pts

# ─────────────────────────────────────────────
# Color Palette  (matching the reference PDF)
# ─────────────────────────────────────────────

BLACK        = colors.black
WHITE        = colors.white
LIGHT_GREY   = colors.HexColor('#F2F2F2')
MID_GREY     = colors.HexColor('#D0D0D0')
DARK_GREY    = colors.HexColor('#404040')
TABLE_HEADER = colors.HexColor('#D9D9D9')   # light grey header rows
TABLE_ALT    = colors.HexColor('#F7F7F7')   # alternating row tint

# ─────────────────────────────────────────────
# Paragraph Styles
# ─────────────────────────────────────────────

def get_styles():
    base = getSampleStyleSheet()

    styles = {}

    # ── Cover page ──────────────────────────────
    styles['cover_institute'] = ParagraphStyle(
        'cover_institute',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=BLACK,
    )
    styles['cover_title'] = ParagraphStyle(
        'cover_title',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=BLACK,
    )
    styles['cover_subtitle'] = ParagraphStyle(
        'cover_subtitle',
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=BLACK,
    )
    styles['cover_dept'] = ParagraphStyle(
        'cover_dept',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=4,
        textColor=BLACK,
    )

    # ── Section headings ────────────────────────
    styles['section_heading'] = ParagraphStyle(
        'section_heading',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=8,
        textColor=BLACK,
        underlineWidth=0.5,
        underlineOffset=-2,
    )
    styles['subsection_heading'] = ParagraphStyle(
        'subsection_heading',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=6,
        textColor=BLACK,
    )
    styles['left_heading'] = ParagraphStyle(
        'left_heading',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=4,
        textColor=BLACK,
    )

    # ── Body text ───────────────────────────────
    styles['body'] = ParagraphStyle(
        'body',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceBefore=2,
        spaceAfter=4,
        textColor=BLACK,
    )
    styles['body_center'] = ParagraphStyle(
        'body_center',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=4,
        textColor=BLACK,
    )
    styles['body_bold'] = ParagraphStyle(
        'body_bold',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceBefore=2,
        spaceAfter=4,
        textColor=BLACK,
    )
    styles['body_left'] = ParagraphStyle(
        'body_left',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=4,
        textColor=BLACK,
    )

    # ── Table cell styles ───────────────────────
    styles['cell'] = ParagraphStyle(
        'cell',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=BLACK,
    )
    styles['cell_center'] = ParagraphStyle(
        'cell_center',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=BLACK,
    )
    styles['cell_bold'] = ParagraphStyle(
        'cell_bold',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=BLACK,
    )
    styles['cell_bold_center'] = ParagraphStyle(
        'cell_bold_center',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=BLACK,
    )
    styles['cell_small'] = ParagraphStyle(
        'cell_small',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        textColor=BLACK,
    )

    # ── List / bullet items ──────────────────────
    styles['bullet'] = ParagraphStyle(
        'bullet',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        leftIndent=20,
        firstLineIndent=0,
        spaceBefore=2,
        spaceAfter=4,
        bulletIndent=8,
        alignment=TA_JUSTIFY,
        textColor=BLACK,
    )
    styles['numbered_item'] = ParagraphStyle(
        'numbered_item',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        leftIndent=24,
        firstLineIndent=-14,
        spaceBefore=2,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        textColor=BLACK,
    )

    # ── Syllabus text ────────────────────────────
    styles['syllabus'] = ParagraphStyle(
        'syllabus',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceBefore=2,
        spaceAfter=6,
        textColor=BLACK,
    )

    # ── Page footer ──────────────────────────────
    styles['footer'] = ParagraphStyle(
        'footer',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=DARK_GREY,
    )

    return styles


# ─────────────────────────────────────────────
# Reusable Table Styles
# ─────────────────────────────────────────────

def base_table_style():
    """Standard bordered table style used throughout."""
    return [
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME',    (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',  (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]


def header_table_style():
    """Table style with a grey first row (header)."""
    style = base_table_style()
    style += [
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',       (0, 0), (-1, 0), 'CENTER'),
    ]
    return style


def mapping_table_style(num_rows, num_cols):
    """Style for CO-PO / PEO-GA / PO-PEO mapping tables."""
    style = base_table_style()
    style += [
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('BACKGROUND',  (0, 0), (0, -1), TABLE_HEADER),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE',    (0, 0), (-1, -1), 8),
    ]
    return style


def semester_table_style():
    """Style for scheme-of-instruction semester tables."""
    style = base_table_style()
    style += [
        ('BACKGROUND',  (0, 0), (-1, 0), TABLE_HEADER),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',       (0, 0), (0, -1), 'CENTER'),   # S.No column
        ('ALIGN',       (2, 0), (2, -1), 'CENTER'),   # Course Code
        ('ALIGN',       (4, 0), (-1, -1), 'CENTER'),  # L T P Credits Cat
        ('FONTNAME',    (0, -1), (-1, -1), 'Helvetica-Bold'),  # TOTAL row
        ('BACKGROUND',  (0, -1), (-1, -1), TABLE_HEADER),
    ]
    return style


def course_header_style():
    """Style for the top header table of each course in detailed syllabus."""
    return [
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME',    (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('ALIGN',       (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',  (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]


def peo_table_style():
    """Style for PEO list table."""
    style = base_table_style()
    style += [
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN',       (0, 0), (0, -1), 'CENTER'),
        ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
    ]
    return style


def po_table_style():
    """Style for Program Outcomes table."""
    style = base_table_style()
    style += [
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN',       (0, 0), (0, -1), 'LEFT'),
        ('VALIGN',      (0, 0), (-1, -1), 'TOP'),
    ]
    return style