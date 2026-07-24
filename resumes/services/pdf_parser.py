import re
import pdfplumber
import PyPDF2

def extract_text_from_pdf(file_input):
    """
    Extract text from PDF file or file-like object using pdfplumber with PyPDF2 fallback.
    """
    extracted_text = ""
    try:
        with pdfplumber.open(file_input) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except Exception:
        # Fallback to PyPDF2
        try:
            if hasattr(file_input, 'seek'):
                file_input.seek(0)
            reader = PyPDF2.PdfReader(file_input)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        except Exception:
            extracted_text = ""

    return clean_text(extracted_text)

def clean_text(text):
    if not text:
        return ""
    # Normalize whitespaces and linebreaks
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def parse_resume_sections(text):
    """
    Categorize text into key resume sections using heading detection regex.
    """
    sections = {
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'projects': '',
        'certifications': ''
    }

    if not text:
        return sections

    lines = text.split('\n')
    current_section = 'summary'
    section_buffers = {k: [] for k in sections.keys()}

    # Keywords for detecting section headers
    header_patterns = {
        'summary': r'^(summary|profile|about me|objective|professional summary)',
        'experience': r'^(experience|work experience|employment|work history|professional experience)',
        'education': r'^(education|academic background|qualifications|academic history)',
        'skills': r'^(skills|technical skills|technologies|core competencies|skills & tools)',
        'projects': r'^(projects|key projects|personal projects|portfolio)',
        'certifications': r'^(certifications|licenses|courses|certificates|achievements)'
    }

    for line in lines:
        clean_line = line.strip().lower()
        matched = False

        for sec_name, pattern in header_patterns.items():
            if re.search(pattern, clean_line, re.IGNORECASE) and len(clean_line) < 40:
                current_section = sec_name
                matched = True
                break

        if not matched:
            section_buffers[current_section].append(line)

    for sec_name in sections:
        sections[sec_name] = '\n'.join(section_buffers[sec_name]).strip()

    return sections
