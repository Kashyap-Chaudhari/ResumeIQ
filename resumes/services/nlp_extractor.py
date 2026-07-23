import re

# Comprehensive Tech & Soft Skill Dictionary (250+ terms)
SKILL_DICTIONARY = [
    # Languages
    'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'ruby', 'php', 'golang', 'rust', 'kotlin', 'swift', 'scala', 'r', 'sql', 'html', 'css', 'bash', 'shell', 'powershell',
    
    # Web Frameworks
    'django', 'flask', 'fastapi', 'express', 'express.js', 'node.js', 'nodejs', 'react', 'react.js', 'vue', 'vue.js', 'angular', 'next.js', 'nuxt.js', 'svelte', 'bootstrap', 'tailwind', 'tailwindcss', 'spring boot', 'laravel', 'asp.net', 'graphql', 'rest api', 'microservices',
    
    # Databases & Caching
    'postgresql', 'postgres', 'mysql', 'sqlite', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'elasticsearch', 'oracle', 'mssql', 'neo4j', 'firebase', 'supabase',
    
    # DevOps & Cloud
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'github actions', 'gitlab ci', 'circleci', 'nginx', 'apache', 'linux', 'unix', 'ci/cd', 'helm', 'cloudformation',
    
    # Data & AI / ML
    'pandas', 'numpy', 'scipy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'opencv', 'spacy', 'nltk', 'spark', 'pyspark', 'hadoop', 'tableau', 'power bi', 'airflow', 'dbt', 'langchain', 'llm', 'nlp', 'computer vision', 'data engineering',
    
    # Testing & Tools
    'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'pytest', 'unittest', 'jest', 'cypress', 'selenium', 'postman', 'docker compose', 'swagger',
    
    # Soft Skills & Concepts
    'agile', 'scrum', 'system design', 'object-oriented programming', 'oop', 'data structures', 'algorithms', 'problem solving', 'team leadership', 'code review', 'ci/cd pipelines'
]

ACTION_VERBS = [
    'architected', 'spearheaded', 'engineered', 'optimized', 'scaled', 'automated',
    'built', 'designed', 'developed', 'deployed', 'implemented', 'integrated',
    'lead', 'managed', 'migrated', 'reduced', 'increased', 'generated', 'streamlined',
    'transformed', 'championed', 'established', 'revamped', 'refactored'
]

def extract_skills_from_text(text):
    """
    Extract skills present in text using boundary-matching regex.
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = set()

    for skill in SKILL_DICTIONARY:
        # Regex boundary check to avoid partial word match (e.g. 'c' matching 'cat')
        pattern = r'(?<![a-zA-Z0-9#\+\-\.])' + re.escape(skill) + r'(?![a-zA-Z0-9#\+\-\.])'
        if re.search(pattern, text_lower):
            # Display format capitalization
            found_skills.add(format_skill_name(skill))

    return sorted(list(found_skills))

def extract_action_verbs(text):
    """
    Find action verbs present in resume text.
    """
    if not text:
        return []
    text_lower = text.lower()
    found_verbs = []
    for verb in ACTION_VERBS:
        if re.search(r'\b' + re.escape(verb) + r'\b', text_lower):
            found_verbs.append(verb)
    return found_verbs

def extract_metrics_count(text):
    """
    Count instances of quantifiable metrics (percentages, dollar amounts, numbers).
    """
    if not text:
        return 0
    # Patterns for %, $, numbers, multiplier (3x, 10k+)
    metric_pattern = r'(\d+%\s*|\$\d+|\b\d+k\b|\b\d+x\b|\b\d+\s*users\b|\b\d+\s*percent\b|\b\d+\s*ms\b)'
    matches = re.findall(metric_pattern, text.lower())
    return len(matches)

def format_skill_name(skill):
    mappings = {
        'python': 'Python', 'javascript': 'JavaScript', 'typescript': 'TypeScript',
        'java': 'Java', 'c++': 'C++', 'c#': 'C#', 'html': 'HTML5', 'css': 'CSS3',
        'django': 'Django', 'flask': 'Flask', 'fastapi': 'FastAPI', 'react': 'React',
        'vue': 'Vue.js', 'angular': 'Angular', 'next.js': 'Next.js', 'node.js': 'Node.js',
        'nodejs': 'Node.js', 'bootstrap': 'Bootstrap', 'tailwind': 'Tailwind CSS',
        'postgresql': 'PostgreSQL', 'mysql': 'MySQL', 'mongodb': 'MongoDB', 'redis': 'Redis',
        'aws': 'AWS', 'azure': 'Azure', 'gcp': 'GCP', 'docker': 'Docker', 'kubernetes': 'Kubernetes',
        'git': 'Git', 'jira': 'Jira', 'pandas': 'Pandas', 'numpy': 'NumPy',
        'scikit-learn': 'scikit-learn', 'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch',
        'rest api': 'REST API', 'graphql': 'GraphQL', 'ci/cd': 'CI/CD'
    }
    return mappings.get(skill.lower(), skill.title())
