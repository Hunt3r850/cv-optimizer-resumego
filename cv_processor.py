import os
import json
import re
import requests
from langdetect import detect
import spacy

# Cargar modelos de spaCy
try:
    nlp_en = spacy.load("en_core_web_sm")
    nlp_es = spacy.load("es_core_news_sm")
except:
    # Fallback si no están instalados (aunque setup.sh debería encargarse)
    nlp_en = None
    nlp_es = None

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
    skills = set()
    if nlp:
        doc = nlp(cv_text)
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT", "MISC"):
                skills.add(ent.text)
    
    keywords, _ = get_keywords_and_verbs(industry, lang)
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", cv_text, re.IGNORECASE):
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
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        response = requests.post(
            ollama_url,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.5, "num_predict": 100}
            },
            timeout=30
        )
        if response.ok:
            return response.json().get("response", bullet).strip()
        else:
            return bullet
    except:
        return bullet

def parse_cv_text(cv_text: str, lang: str):
    sections = {
        "contact": [],
        "summary": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "skills": []
    }
    
    current = "contact"
    lines = cv_text.splitlines()
    
    # Términos de búsqueda para secciones
    terms = {
        "experience": ["experience", "experiencia", "work history", "historial laboral"],
        "education": ["education", "educación", "formación", "estudios"],
        "certifications": ["certifications", "certificaciones", "cursos", "formación adicional"],
        "skills": ["skills", "habilidades", "competencias", "conocimientos"],
        "summary": ["summary", "resumen", "perfil", "sobre mí", "objective"]
    }
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip: continue
        
        line_lower = line_strip.lower().rstrip(":")
        
        found_section = False
        for sec, keywords in terms.items():
            if any(kw == line_lower or line_lower.startswith(kw + " ") for kw in keywords):
                current = sec
                found_section = True
                break
        
        if not found_section:
            sections[current].append(line_strip)
            
    return sections

def process_experience(experience_lines, industry: str, lang: str):
    jobs = []
    current_job = None
    
    # Regex para detectar Título, Empresa y Fechas
    # Formato común: Cargo en Empresa (Fecha) o Cargo | Empresa | Fecha
    for line in experience_lines:
        # Intentar detectar una nueva posición
        match = re.search(r"(.+?)(?:\s+(?:en|at|\|)\s+)(.+?)(?:\s+[\(\[|]\s*(.+?)\s*[\)\]|]|$)", line, re.IGNORECASE)
        
        if match:
            title, company, dates = match.groups()
            current_job = {
                "title": title.strip(),
                "company": company.strip(),
                "dates": dates.strip() if dates else "Presente",
                "bullets": []
            }
            jobs.append(current_job)
        elif line.startswith(("-", "•", "*")) and current_job is not None:
            clean_bullet = re.sub(r"^[-•*]\s*", "", line).strip()
            improved = improve_bullet_with_llama(clean_bullet, industry, lang)
            current_job["bullets"].append(improved)
        elif current_job is not None and len(line) > 10:
            # Si no empieza con viñeta pero parece una descripción
            improved = improve_bullet_with_llama(line, industry, lang)
            current_job["bullets"].append(improved)
            
    return jobs

def generate_html_cv(data):
    """
    Genera el HTML del CV basado en un diccionario de datos estructurado.
    """
    lang = data.get("lang", "es")
    
    template_html = """
    <!DOCTYPE html>
    <html lang="{{ lang }}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ name }} - CV</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 850px; margin: 40px auto; padding: 0 40px; background-color: #fff; }
            header { text-align: center; margin-bottom: 30px; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; }
            h1 { font-size: 28pt; margin-bottom: 5px; color: #2c3e50; text-transform: uppercase; letter-spacing: 2px; }
            .contact-info { font-size: 10pt; color: #7f8c8d; }
            h2 { font-size: 16pt; text-transform: uppercase; border-bottom: 2px solid #bdc3c7; margin-top: 30px; margin-bottom: 15px; color: #2c3e50; padding-bottom: 5px; }
            h3 { font-size: 13pt; margin-top: 15px; margin-bottom: 5px; color: #34495e; }
            .job-header { display: flex; justify-content: space-between; font-weight: bold; color: #2c3e50; }
            .job-details { font-style: italic; margin-bottom: 8px; color: #7f8c8d; }
            ul { margin-top: 8px; padding-left: 25px; }
            li { margin-bottom: 6px; }
            .summary-text { text-align: justify; font-style: italic; }
            .skills-container { display: flex; flex-wrap: wrap; gap: 10px; }
            .skill-tag { background: #ecf0f1; padding: 4px 12px; border-radius: 15px; font-size: 9pt; border: 1px solid #dcdde1; }
            @media print { body { margin: 0; padding: 20px; } .skill-tag { border: 1px solid #ccc; } }
        </style>
    </head>
    <body>
        <header>
            <h1>{{ name }}</h1>
            <div class="contact-info">
                {{ contact_info }}
            </div>
        </header>

        {% if summary %}
        <section>
            <h2>{{ "Resumen Profesional" if lang == "es" else "Professional Summary" }}</h2>
            <p class="summary-text">{{ summary }}</p>
        </section>
        {% endif %}

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
            {% else %}
            <p>{{ "No se detectó experiencia detallada." if lang == "es" else "No detailed experience detected." }}</p>
            {% endfor %}
        </section>

        {% if education %}
        <section>
            <h2>{{ "Educación" if lang == "es" else "Education" }}</h2>
            <p>{{ education }}</p>
        </section>
        {% endif %}

        {% if certifications %}
        <section>
            <h2>{{ "Certificaciones" if lang == "es" else "Certifications" }}</h2>
            <ul>
                {% for cert in certifications %}
                <li>{{ cert }}</li>
                {% endfor %}
            </ul>
        </section>
        {% endif %}

        <section>
            <h2>{{ "Habilidades Técnicas" if lang == "es" else "Technical Skills" }}</h2>
            <div class="skills-container">
                {% for skill in skills %}
                <span class="skill-tag">{{ skill }}</span>
                {% endfor %}
            </div>
        </section>
    </body>
    </html>
    """
    from jinja2 import Template
    template = Template(template_html)
    return template.render(**data)
