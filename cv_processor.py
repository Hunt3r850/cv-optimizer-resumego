import json
import re
import requests
from langdetect import detect
import spacy

nlp_en = spacy.load("en_core_web_sm")
nlp_es = spacy.load("es_core_news_sm")

with open("industry_keywords.json", encoding="utf-8") as f:
    INDUSTRY_DB = json.load(f)

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        return "es" if lang == "es" else "en"
    except:
        return "en"

def get_nlp_model(lang: str):
    return nlp_es if lang == "es" else nlp_en

def get_keywords_and_verbs(industry: str, lang: str):
    industry_data = INDUSTRY_DB.get(industry, INDUSTRY_DB["tech"])
    lang_data = industry_data.get(lang, industry_data["en"])
    return lang_data["keywords"], lang_data["action_verbs"]

def extract_skills(cv_text: str, industry: str, lang: str):
    nlp = get_nlp_model(lang)
    doc = nlp(cv_text)
    skills = set()
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "MISC"):
            skills.add(ent.text)
    keywords, _ = get_keywords_and_verbs(industry, lang)
    for kw in keywords:
        if kw.lower() in cv_text.lower():
            skills.add(kw)
    return list(skills)

def detect_industry(cv_text: str, lang: str) -> str:
    cv_lower = cv_text.lower()
    scores = {industry: 0 for industry in INDUSTRY_DB}
    for industry, data in INDUSTRY_DB.items():
        keywords = data.get(lang, data["en"])["keywords"]
        for kw in keywords:
            if kw.lower() in cv_lower:
                scores[industry] += 1
    return max(scores, key=scores.get) if any(v > 0 for v in scores.values()) else "tech"

def improve_bullet_with_llama(bullet: str, industry: str, lang: str):
    keywords, verbs = get_keywords_and_verbs(industry, lang)
    verbs_str = ", ".join(verbs)
    if lang == "es":
        prompt = (
            f"Reescribe este punto de CV para que sea más impactante, usando verbos de acción fuertes "
            f"y sugiriendo un espacio para una métrica si falta. Usa tono profesional. "
            f"Solo devuelve la oración mejorada.\n\n"
            f"Industria: {industry}\n"
            f"Verbos recomendados: {verbs_str}\n\n"
            f"Original: \"{bullet}\"\nMejorado:"
        )
    else:
        prompt = (
            f"Rewrite this CV bullet point to be more impactful, using strong action verbs "
            f"and adding a placeholder for a metric if missing. Use professional tone. "
            f"Only return the improved sentence.\n\n"
            f"Industry: {industry}\n"
            f"Preferred verbs: {verbs_str}\n\n"
            f"Original: \"{bullet}\"\nImproved:"
        )

    try:
        response = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.5, "num_predict": 60}
            },
            timeout=30
        )
        if response.ok:
            return response.json().get("response", bullet).strip()
        else:
            return bullet + " [⚠️ Llama no respondió]"
    except Exception as e:
        return bullet + f" [⚠️ Error: {str(e)}]"

def parse_cv_text(cv_text: str, lang: str):
    sections = {}
    current = None
    lines = cv_text.splitlines()
    exp_terms = ["experience", "experiencia", "work experience", "experiencia laboral"]
    edu_terms = ["education", "educación", "formación"]
    skill_terms = ["skills", "habilidades", "competencias"]
    for line in lines:
        line = line.strip()
        if not line: continue
        line_lower = line.lower().rstrip(":")
        if any(term in line_lower for term in exp_terms):
            current = "experience"
            sections[current] = []
        elif any(term in line_lower for term in edu_terms):
            current = "education"
            sections[current] = []
        elif any(term in line_lower for term in skill_terms):
            current = "skills"
            sections[current] = []
        else:
            if current and current in sections:
                sections[current].append(line)
    return sections

def process_experience(experience_lines, industry: str, lang: str):
    jobs = []
    current_job = None
    for line in experience_lines:
        if re.search(r"(en|at).+\(.+\)", line, re.IGNORECASE):
            if " en " in line:
                match = re.match(r"(.+?) en ([^(]+) \(([^)]+)\)", line)
            elif " at " in line:
                match = re.match(r"(.+?) at ([^(]+) \(([^)]+)\)", line)
            else:
                match = None
            if match:
                title, company, dates = match.groups()
                current_job = {
                    "title": title.strip(),
                    "company": company.strip(),
                    "dates": dates.strip(),
                    "bullets": []
                }
                jobs.append(current_job)
        elif line.startswith(("-", "•")) and current_job is not None:
            clean_bullet = line[1:].strip()
            improved = improve_bullet_with_llama(clean_bullet, industry, lang)
            current_job["bullets"].append(improved)
    return jobs

def generate_html_cv(name, experience, education, skills, lang="en"):
    template_html = """
    <!DOCTYPE html>
    <html lang="{{ lang }}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ name }} - CV</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; padding: 0 20px; }
            h1 { font-size: 24pt; margin-bottom: 5px; color: #000; text-align: center; text-transform: uppercase; }
            h2 { font-size: 14pt; text-transform: uppercase; border-bottom: 2px solid #333; margin-top: 25px; margin-bottom: 10px; color: #000; }
            h3 { font-size: 12pt; margin-top: 15px; margin-bottom: 5px; }
            .job-header { display: flex; justify-content: space-between; font-weight: bold; }
            .job-details { font-style: italic; margin-bottom: 8px; }
            ul { margin-top: 5px; padding-left: 20px; }
            li { margin-bottom: 5px; }
        </style>
    </head>
    <body>
        <header>
            <h1>{{ name }}</h1>
        </header>

        <section>
            <h2>{{ "Experiencia Profesional" if lang == "es" else "Professional Experience" }}</h2>
            {% for job in experience %}
            <div class="experience-item">
                <div class="job-header">
                    <span>{{ job.title }}</span>
                    <span>{{ job.dates }}</span>
                </div>
                <div class="job-details">{{ job.company }}</div>
                <ul>
                    {% for b in job.bullets %}
                    <li>{{ b }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </section>

        <section>
            <h2>{{ "Educación" if lang == "es" else "Education" }}</h2>
            <p>{{ education }}</p>
        </section>

        <section>
            <h2>{{ "Habilidades" if lang == "es" else "Skills" }}</h2>
            <p>{{ skills }}</p>
        </section>
    </body>
    </html>
    """
    from jinja2 import Template
    template = Template(template_html)
    return template.render(
        name=name,
        experience=experience,
        education=education,
        skills=skills,
        lang=lang
    )