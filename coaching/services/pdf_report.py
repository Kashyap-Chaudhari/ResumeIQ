from django.template.loader import render_to_string

def generate_html_report(resume, match_analysis=None, readiness=None):
    """
    Renders clean, styled printable HTML report for export/download.
    """
    context = {
        'resume': resume,
        'match_analysis': match_analysis,
        'readiness': readiness,
    }
    return render_to_string('coaching/pdf_report_template.html', context)
