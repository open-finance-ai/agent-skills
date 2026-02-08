#!/usr/bin/env python3
"""
סקריפט ליצירת דוח ניתוח חשבון בנק - PDF בעברית
שימוש: הסקריפט מקבל dict של נתוני הניתוח ומייצר PDF מקצועי.

דרישות:
  pip install reportlab matplotlib python-bidi --break-system-packages
"""

import os
import json
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# --- Hebrew Bidi support ---
try:
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False

def heb(text):
    """Apply bidi algorithm for correct Hebrew display in PDF.
    NOTE: Do NOT use arabic_reshaper for Hebrew - it corrupts the glyphs.
    Hebrew only needs bidi reordering, not glyph shaping."""
    if not text or not HAS_BIDI:
        return str(text)
    try:
        return get_display(str(text))
    except:
        return str(text)


# --- Font setup ---
FONT_REGULAR = None
FONT_BOLD = None

def setup_fonts():
    """Register Hebrew-supporting fonts."""
    global FONT_REGULAR, FONT_BOLD

    # FreeSans has excellent Hebrew support
    candidates = [
        ('/usr/share/fonts/truetype/freefont/FreeSans.ttf',
         '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ]

    for regular_path, bold_path in candidates:
        if os.path.exists(regular_path) and os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont('HebFont', regular_path))
            pdfmetrics.registerFont(TTFont('HebFontBold', bold_path))
            FONT_REGULAR = 'HebFont'
            FONT_BOLD = 'HebFontBold'
            return

    # Last resort
    FONT_REGULAR = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'


# --- Color scheme ---
C = {
    'primary':    colors.HexColor('#1a56db'),
    'success':    colors.HexColor('#059669'),
    'danger':     colors.HexColor('#dc2626'),
    'warning':    colors.HexColor('#d97706'),
    'info':       colors.HexColor('#2563eb'),
    'light_bg':   colors.HexColor('#f3f4f6'),
    'white':      colors.white,
    'text':       colors.HexColor('#1f2937'),
    'text_light': colors.HexColor('#6b7280'),
    'border':     colors.HexColor('#e5e7eb'),
}

CHART_COLORS = [
    '#1a56db', '#059669', '#d97706', '#dc2626', '#7c3aed',
    '#0891b2', '#be185d', '#4338ca', '#b45309', '#0d9488',
    '#6d28d9', '#c026d3', '#ea580c', '#2563eb', '#16a34a',
]


# --- Styles ---
def create_styles():
    styles = getSampleStyleSheet()

    def add(name, **kw):
        kw.setdefault('fontName', FONT_REGULAR)
        kw.setdefault('textColor', C['text'])
        styles.add(ParagraphStyle(name, **kw))

    add('HTitle',   fontName=FONT_BOLD, fontSize=28, leading=34, alignment=TA_CENTER,
        textColor=C['primary'], spaceAfter=6*mm)
    add('HH1',      fontName=FONT_BOLD, fontSize=18, leading=24, alignment=TA_RIGHT,
        textColor=C['primary'], spaceAfter=4*mm, spaceBefore=8*mm)
    add('HH2',      fontName=FONT_BOLD, fontSize=14, leading=18, alignment=TA_RIGHT,
        spaceAfter=3*mm, spaceBefore=5*mm)
    add('HBody',    fontSize=11, leading=16, alignment=TA_RIGHT, spaceAfter=2*mm)
    add('HCenter',  fontSize=11, leading=16, alignment=TA_CENTER, spaceAfter=2*mm)
    add('HSmall',   fontSize=9, leading=12, alignment=TA_RIGHT,
        textColor=C['text_light'], spaceAfter=1*mm)
    add('HDisclaim', fontSize=8, leading=11, alignment=TA_CENTER,
        textColor=C['text_light'], spaceBefore=5*mm)

    return styles


SCORE_LABELS = {
    'excellent': "מצוין - ניהול פיננסי חכם",
    'good':     "טוב - יש מקום לשיפור קל",
    'average':  "בינוני - מומלץ לשים לב להוצאות",
    'poor':     "דורש שיפור - יש אתגרים פיננסיים",
    'critical': "קריטי - מומלץ לפנות לייעוץ מקצועי",
}


# --- Matplotlib charts ---
def _setup_mpl():
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False


def create_pie_chart(categories, amounts):
    _setup_mpl()
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    sorted_data = sorted(zip(amounts, categories), reverse=True)
    amounts_s = [d[0] for d in sorted_data]
    cats_s = [heb(d[1]) for d in sorted_data]
    clrs = CHART_COLORS[:len(categories)]

    wedges, _, autotexts = ax.pie(
        amounts_s, labels=None, colors=clrs,
        autopct='%1.0f%%', startangle=90,
        pctdistance=0.8, textprops={'fontsize': 9}
    )
    ax.legend(wedges, cats_s, loc='center left', bbox_to_anchor=(-0.35, 0.5),
              fontsize=8, frameon=False)
    ax.set_title(heb("פילוח הוצאות"), fontsize=14, fontweight='bold', pad=10)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


def create_trend_chart(months, incomes, expenses):
    _setup_mpl()
    fig, ax = plt.subplots(1, 1, figsize=(7, 3.5))
    x = range(len(months))

    ax.plot(x, incomes, color='#059669', marker='o', linewidth=2, markersize=5,
            label=heb('הכנסות'))
    ax.plot(x, expenses, color='#dc2626', marker='s', linewidth=2, markersize=5,
            label=heb('הוצאות'))
    ax.fill_between(x, incomes, expenses, alpha=0.1,
                    where=[i > e for i, e in zip(incomes, expenses)], color='#059669')
    ax.fill_between(x, incomes, expenses, alpha=0.1,
                    where=[i <= e for i, e in zip(incomes, expenses)], color='#dc2626')

    ax.set_xticks(x)
    ax.set_xticklabels([heb(m) for m in months], fontsize=8, rotation=45)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_title(heb("מגמות חודשיות"), fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


def create_forecast_chart(months_actual, balances_actual, months_forecast, balances_forecast):
    _setup_mpl()
    fig, ax = plt.subplots(1, 1, figsize=(7, 3.5))

    all_months = months_actual + months_forecast
    x_actual = range(len(months_actual))
    x_forecast = range(len(months_actual) - 1, len(all_months))

    ax.plot(x_actual, balances_actual, color='#1a56db', marker='o', linewidth=2,
            label=heb('בפועל'))
    forecast_line = [balances_actual[-1]] + balances_forecast
    ax.plot(x_forecast, forecast_line, color='#1a56db', marker='s', linewidth=2,
            linestyle='--', alpha=0.6, label=heb('תחזית'))

    if any(b < 0 for b in balances_forecast):
        ax.axhline(y=0, color='#dc2626', linestyle=':', alpha=0.5)

    ax.set_xticks(range(len(all_months)))
    ax.set_xticklabels([heb(m) for m in all_months], fontsize=8, rotation=45)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.set_title(heb("תחזית תזרים מזומנים"), fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


def create_health_gauge(score):
    import numpy as np
    _setup_mpl()
    fig, ax = plt.subplots(1, 1, figsize=(4, 2.5))

    theta = np.linspace(np.pi, 0, 100)
    r_outer, r_inner = 1.0, 0.6

    segments = [
        (0, 20, '#dc2626'), (20, 40, '#ea580c'), (40, 60, '#d97706'),
        (60, 80, '#2563eb'), (80, 100, '#059669'),
    ]
    for start, end, color in segments:
        t = theta[start:end]
        xo = np.cos(t) * r_outer
        yo = np.sin(t) * r_outer
        xi = np.cos(t[::-1]) * r_inner
        yi = np.sin(t[::-1]) * r_inner
        ax.fill(np.concatenate([xo, xi]), np.concatenate([yo, yi]), color=color, alpha=0.3)

    needle_angle = np.pi * (1 - score / 100)
    ax.plot([0, np.cos(needle_angle)*0.85], [0, np.sin(needle_angle)*0.85],
            color='#1f2937', linewidth=3, solid_capstyle='round')
    ax.plot(0, 0, 'o', color='#1f2937', markersize=8)

    ax.text(0, -0.15, f'{score}', fontsize=32, fontweight='bold', ha='center', va='center')
    ax.text(0, -0.35, heb('מתוך 100'), fontsize=10, ha='center', va='center', color='#6b7280')

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.5, 1.15)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(heb("ציון בריאות פיננסית"), fontsize=14, fontweight='bold', pad=5)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


# --- Table helper ---
def styled_table(data, col_widths=None, header=True):
    rtl_data = [row[::-1] for row in data]
    if col_widths:
        col_widths = col_widths[::-1]

    table = Table(rtl_data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ('ALIGN',          (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME',       (0,0), (-1,-1), FONT_REGULAR),
        ('FONTSIZE',       (0,0), (-1,-1), 9),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 6),
        ('TOPPADDING',     (0,0), (-1,-1), 6),
        ('LEFTPADDING',    (0,0), (-1,-1), 8),
        ('RIGHTPADDING',   (0,0), (-1,-1), 8),
        ('GRID',           (0,0), (-1,-1), 0.5, C['border']),
    ]
    if header:
        cmds += [
            ('BACKGROUND', (0,0), (-1,0), C['primary']),
            ('TEXTCOLOR',  (0,0), (-1,0), C['white']),
            ('FONTNAME',   (0,0), (-1,0), FONT_BOLD),
            ('FONTSIZE',   (0,0), (-1,0), 10),
        ]
    for i in range(1 if header else 0, len(rtl_data)):
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0,i), (-1,i), C['light_bg']))

    table.setStyle(TableStyle(cmds))
    return table


# ============================================================
# Main report generator
# ============================================================
def generate_report(analysis_data, output_path):
    """
    Generate the full PDF report.

    analysis_data: dict with keys:
        user_name, period, sources, summary, categories, trends,
        recurring, anomalies, savings_potential, forecast,
        health_score, key_insights
    """
    setup_fonts()
    styles = create_styles()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )

    story = []
    d = analysis_data

    # ===== Cover page =====
    story.append(Spacer(1, 40*mm))
    story.append(Paragraph(heb("דוח ניתוח פיננסי"), styles['HTitle']))
    story.append(Spacer(1, 5*mm))

    if d.get('user_name'):
        story.append(Paragraph(heb(d['user_name']), styles['HCenter']))

    period = d.get('period', {})
    story.append(Paragraph(heb(f"תקופה: {period.get('from','')} - {period.get('to','')}"),
                           styles['HCenter']))
    sources = ", ".join(d.get('sources', []))
    if sources:
        story.append(Paragraph(heb(f"מקורות: {sources}"), styles['HCenter']))

    story.append(Spacer(1, 5*mm))
    today = datetime.now().strftime('%d/%m/%Y')
    story.append(Paragraph(heb(f"הופק בתאריך: {today}"), styles['HSmall']))
    story.append(Paragraph(heb("הופק באמצעות Open Finance AI"), styles['HSmall']))
    story.append(PageBreak())

    # ===== Executive summary =====
    story.append(Paragraph(heb("תקציר מנהלים"), styles['HH1']))
    for insight in d.get('key_insights', []):
        story.append(Paragraph(heb(f"- {insight}"), styles['HBody']))
    story.append(Spacer(1, 5*mm))

    # ===== Financial summary KPIs =====
    story.append(Paragraph(heb("סיכום פיננסי"), styles['HH1']))
    s = d.get('summary', {})

    kpi_data = [
        [heb("טרנזקציות"), heb("חיסכון חודשי"),
         heb("הוצאות"), heb("הכנסות")],
        [
            str(s.get('total_transactions', 0)),
            f"{s.get('avg_monthly_saving', 0):,.0f}",
            f"{s.get('total_expenses', 0):,.0f}",
            f"{s.get('total_income', 0):,.0f}",
        ],
    ]
    kpi = Table(kpi_data, colWidths=[doc.width/4]*4)
    kpi.setStyle(TableStyle([
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME',     (0,0), (-1,0), FONT_REGULAR),
        ('FONTNAME',     (0,1), (-1,1), FONT_BOLD),
        ('FONTSIZE',     (0,0), (-1,0), 9),
        ('TEXTCOLOR',    (0,0), (-1,0), C['text_light']),
        ('FONTSIZE',     (0,1), (-1,1), 16),
        ('TEXTCOLOR',    (0,1), (-1,1), C['primary']),
        ('TOPPADDING',   (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0), (-1,-1), 8),
        ('BACKGROUND',   (0,0), (-1,-1), C['light_bg']),
        ('BOX',          (0,0), (-1,-1), 1, C['border']),
        ('LINEBELOW',    (0,0), (-1,0), 0.5, C['border']),
    ]))
    story.append(kpi)

    if s.get('expense_ratio'):
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph(
            heb(f"יחס הוצאות/הכנסות: {s['expense_ratio']:.0f}%"), styles['HBody']))
    story.append(PageBreak())

    # ===== Expense categories =====
    cats = d.get('categories', {})
    if cats.get('labels'):
        story.append(Paragraph(heb("פילוח הוצאות לפי קטגוריות"), styles['HH1']))

        pie_buf = create_pie_chart(cats['labels'], cats['amounts'])
        story.append(Image(pie_buf, width=160*mm, height=110*mm))
        story.append(Spacer(1, 3*mm))

        header_row = [heb("אחוז"), heb("סכום"), heb("קטגוריה")]
        rows = [header_row]
        for lbl, amt, pct in sorted(
                zip(cats['labels'], cats['amounts'], cats['percentages']),
                key=lambda x: x[1], reverse=True):
            rows.append([f"{pct:.1f}%", f"{amt:,.0f}", heb(lbl)])
        story.append(styled_table(rows, col_widths=[30*mm, 40*mm, 60*mm]))
        story.append(PageBreak())

    # ===== Monthly trends =====
    trends = d.get('trends', {})
    if trends.get('months'):
        story.append(Paragraph(heb("מגמות חודשיות"), styles['HH1']))
        trend_buf = create_trend_chart(trends['months'], trends['incomes'], trends['expenses'])
        story.append(Image(trend_buf, width=170*mm, height=90*mm))
        story.append(Spacer(1, 3*mm))

        header_row = [heb("חיסכון"), heb("הוצאות"), heb("הכנסות"), heb("חודש")]
        rows = [header_row]
        savings = trends.get('savings', [0]*len(trends['months']))
        for i, month in enumerate(trends['months']):
            rows.append([
                f"{savings[i]:,.0f}",
                f"{trends['expenses'][i]:,.0f}",
                f"{trends['incomes'][i]:,.0f}",
                heb(month),
            ])
        story.append(styled_table(rows, col_widths=[35*mm]*4))
        story.append(PageBreak())

    # ===== Recurring payments =====
    recurring = d.get('recurring', [])
    if recurring:
        story.append(Paragraph(heb("הוראות קבע ומנויים"), styles['HH1']))
        total_m = sum(r['monthly'] for r in recurring)
        total_y = sum(r['yearly'] for r in recurring)
        story.append(Paragraph(
            heb(f"סה\"כ: {total_m:,.0f} לחודש | {total_y:,.0f} לשנה"), styles['HBody']))

        header_row = [heb("סוג"), heb("שנתי"), heb("חודשי"), heb("שם")]
        rows = [header_row]
        for r in sorted(recurring, key=lambda x: x['yearly'], reverse=True):
            rows.append([heb(r['type']), f"{r['yearly']:,.0f}",
                         f"{r['monthly']:,.0f}", heb(r['name'])])
        story.append(styled_table(rows, col_widths=[30*mm, 35*mm, 35*mm, 50*mm]))
        story.append(PageBreak())

    # ===== Anomalies =====
    anomalies = d.get('anomalies', [])
    if anomalies:
        story.append(Paragraph(heb("הוצאות חריגות"), styles['HH1']))
        story.append(Paragraph(
            heb("הוצאות שחרגו משמעותית מהדפוס הרגיל:"), styles['HBody']))

        header_row = [heb("רמה"), heb("סכום"), heb("תיאור"), heb("תאריך")]
        rows = [header_row]
        for a in anomalies:
            sev = heb("חריגה גבוהה") if a['severity'] == 'high' else heb("חריגה בינונית")
            rows.append([sev, f"{abs(a['amount']):,.0f}",
                         heb(a['description'][:30]), a['date']])
        story.append(styled_table(rows, col_widths=[30*mm, 30*mm, 50*mm, 30*mm]))

    # ===== Savings potential =====
    savings_p = d.get('savings_potential', [])
    if savings_p:
        story.append(Spacer(1, 5*mm))
        story.append(Paragraph(heb("פוטנציאל חיסכון"), styles['HH1']))
        tm = sum(s['monthly_saving'] for s in savings_p)
        ty = sum(s['yearly_saving'] for s in savings_p)
        story.append(Paragraph(
            heb(f"פוטנציאל כולל: {tm:,.0f} לחודש | {ty:,.0f} לשנה"), styles['HBody']))

        header_row = [heb("שנתי"), heb("חודשי"), heb("הזדמנות")]
        rows = [header_row]
        for sv in sorted(savings_p, key=lambda x: x['yearly_saving'], reverse=True):
            rows.append([f"{sv['yearly_saving']:,.0f}", f"{sv['monthly_saving']:,.0f}",
                         heb(sv['description'][:40])])
        story.append(styled_table(rows, col_widths=[35*mm, 35*mm, 70*mm]))
        story.append(PageBreak())

    # ===== Cash flow forecast =====
    forecast = d.get('forecast', {})
    if forecast.get('months_actual'):
        story.append(Paragraph(heb("תחזית תזרים מזומנים"), styles['HH1']))
        fc_buf = create_forecast_chart(
            forecast['months_actual'], forecast['balances_actual'],
            forecast['months_forecast'], forecast['balances_forecast'])
        story.append(Image(fc_buf, width=170*mm, height=90*mm))
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph(
            heb("* התחזית מבוססת על נתוני עבר ואינה מביאה בחשבון שינויים עתידיים."),
            styles['HSmall']))

    # ===== Health score =====
    health = d.get('health_score', {})
    if health.get('total') is not None:
        story.append(Spacer(1, 5*mm))
        story.append(Paragraph(heb("ציון בריאות פיננסית"), styles['HH1']))

        gauge_buf = create_health_gauge(health['total'])
        story.append(Image(gauge_buf, width=100*mm, height=65*mm))
        story.append(Spacer(1, 3*mm))

        score = health['total']
        if score >= 80:
            level, clr = SCORE_LABELS['excellent'], '#059669'
        elif score >= 60:
            level, clr = SCORE_LABELS['good'], '#2563eb'
        elif score >= 40:
            level, clr = SCORE_LABELS['average'], '#d97706'
        elif score >= 20:
            level, clr = SCORE_LABELS['poor'], '#ea580c'
        else:
            level, clr = SCORE_LABELS['critical'], '#dc2626'

        story.append(Paragraph(
            f'<font color="{clr}">{heb(level)}</font>', styles['HCenter']))

        if health.get('components'):
            header_row = [heb("ציון"), heb("מקסימום"), heb("תיאור"), heb("רכיב")]
            rows = [header_row]
            for comp in health['components']:
                rows.append([
                    str(comp['score']), str(comp['max']),
                    heb(comp.get('description', '')[:30]), heb(comp['name'])])
            story.append(Spacer(1, 3*mm))
            story.append(styled_table(rows, col_widths=[20*mm, 25*mm, 55*mm, 40*mm]))

        if health.get('recommendations'):
            story.append(Spacer(1, 5*mm))
            story.append(Paragraph(heb("המלצות מותאמות אישית:"), styles['HH2']))
            for i, rec in enumerate(health['recommendations'], 1):
                story.append(Paragraph(heb(f"{i}. {rec}"), styles['HBody']))

    # ===== Disclaimer =====
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(
        heb("הערה חשובה: דוח זה נוצר באופן אוטומטי ואינו מהווה ייעוץ פיננסי מקצועי. "
            "לקבלת החלטות פיננסיות משמעותיות מומלץ להתייעץ עם יועץ פיננסי מוסמך."),
        styles['HDisclaim']))
    story.append(Paragraph(
        heb("Powered by Open Finance | open-finance.ai"),
        styles['HDisclaim']))

    doc.build(story)
    return output_path


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python generate_report.py <analysis_data.json> <output.pdf>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Report generated: {generate_report(data, sys.argv[2])}")
