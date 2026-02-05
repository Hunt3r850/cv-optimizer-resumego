import os
import json
import re
import requests
from langdetect import detect
import spacy

# Cargar modelos de spaCy para múltiples idiomas
MODELS = {
    "en": "en_core_web_sm",
    "es": "es_core_news_sm",
    "de": "de_core_news_sm",
    "it": "it_core_news_sm"
}

LOADED_MODELS = {}

def get_nlp_model(lang: str):
    if lang not in LOADED_MODELS:
        model_name = MODELS.get(lang, MODELS["en"])
        try:
            LOADED_MODELS[lang] = spacy.load(model_name)
        except:
            LOADED_MODELS[lang] = None
    return LOADED_MODELS[lang]

# Intentar cargar industry_keywords.json
try:
    with open("industry_keywords.json", encoding="utf-8") as f:
        INDUSTRY_DB = json.load(f)
except FileNotFoundError:
    INDUSTRY_DB = {}

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        if lang in MODELS:
            return lang
        return "en"
    except:
        return "en"

def detect_industry(cv_text: str, lang: str) -> str:
    cv_lower = cv_text.lower()
    scores = {industry: 0 for industry in INDUSTRY_DB}
    for industry, data in INDUSTRY_DB.items():
        lang_data = data.get(lang, data.get("en", {}))
        keywords = lang_data.get("keywords", [])
        for kw in keywords:
            if kw.lower() in cv_lower:
                scores[industry] += 1
    return max(scores, key=scores.get) if any(v > 0 for v in scores.values()) else "tech"

def call_llama(prompt: str, temperature=0.1):
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        response = requests.post(
            ollama_url,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=120
        )
        if response.ok:
            return response.json().get("response", "").strip()
    except:
        pass
    return ""

def clean_json_response(response: str):
    if not response:
        return None
    try:
        # Buscar el primer '{' y el último '}'
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = response[start:end]
            # Eliminar comentarios de estilo JS si existen
            json_str = re.sub(r'//.*?\n', '\n', json_str)
            return json.loads(json_str)
    except Exception as e:
        print(f"Error cleaning JSON: {e}")
    return None

def ai_parse_cv(cv_text: str, lang: str):
    prompt = f"""
    SYSTEM: You are a professional CV parser. Your task is to extract information from CV text and return it in VALID JSON format.
    LANGUAGE: {lang}
    
    INSTRUCTIONS:
    1. Return ONLY the JSON object.
    2. Do not include any text before or after the JSON.
    3. Ensure all quotes are properly escaped.
    4. Rewrite experience bullets to be highly professional and impactful in {lang}.
    
    JSON SCHEMA:
    {{
        "name": "Full Name",
        "contact_info": "Email | Phone | Location | LinkedIn",
        "summary": "Professional summary",
        "experience": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "dates": "Dates",
                "bullets": ["Achievement 1", "Achievement 2"]
            }}
        ],
        "education": "Degree and University",
        "certifications": ["Cert 1", "Cert 2"],
        "skills": ["Skill 1", "Skill 2"]
    }}

    CV TEXT:
    {cv_text}
    """
    
    response = call_llama(prompt, temperature=0.1)
    data = clean_json_response(response)
    
    if not data:
        repair_prompt = f"The following text should be a JSON object but it's malformed. Fix it and return ONLY the valid JSON:\n{response}"
        response = call_llama(repair_prompt, temperature=0.0)
        data = clean_json_response(response)
        
    return data

def get_template_styles(template_name="Modern"):
    styles = {
        "Modern": """
            body { font-family: 'Inter', 'Segoe UI', sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 850px; margin: 40px auto; padding: 0 40px; background-color: #f8f9fa; }
            .cv-container { background: white; padding: 50px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-radius: 8px; }
            header { border-bottom: 4px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }
            h1 { font-size: 32pt; margin: 0; color: #2c3e50; letter-spacing: -1px; }
            .contact-info { font-size: 10pt; color: #7f8c8d; margin-top: 10px; }
            h2 { font-size: 16pt; text-transform: uppercase; color: #3498db; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
            .job-header { display: flex; justify-content: space-between; font-weight: 700; color: #2c3e50; }
            .job-details { color: #3498db; font-weight: 500; margin-bottom: 10px; }
            .skill-tag { background: #e1f5fe; color: #0288d1; padding: 5px 12px; border-radius: 4px; font-size: 9pt; display: inline-block; margin: 3px; font-weight: 600; }
        """,
        "Executive": """
            body { font-family: 'Georgia', serif; line-height: 1.5; color: #222; max-width: 850px; margin: 40px auto; padding: 0 40px; background-color: #fff; }
            .cv-container { border: 1px solid #eee; padding: 60px; }
            header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px; }
            h1 { font-size: 26pt; margin: 0; text-transform: uppercase; font-weight: normal; }
            .contact-info { font-size: 10pt; font-style: italic; margin-top: 10px; }
            h2 { font-size: 14pt; text-transform: uppercase; border-bottom: 1px solid #000; margin-top: 30px; padding-bottom: 2px; }
            .job-header { display: flex; justify-content: space-between; font-weight: bold; }
            .job-details { font-weight: bold; margin-bottom: 5px; }
            ul { list-style-type: square; }
            .skill-tag { border: 1px solid #444; padding: 2px 8px; margin: 2px; display: inline-block; font-size: 9pt; }
        """,
        "Minimalist": """
            body { font-family: 'Helvetica', sans-serif; line-height: 1.4; color: #444; max-width: 800px; margin: 40px auto; padding: 0 20px; }
            header { margin-bottom: 40px; }
            h1 { font-size: 24pt; font-weight: 300; margin: 0; color: #000; }
            .contact-info { font-size: 9pt; color: #999; text-transform: uppercase; letter-spacing: 1px; }
            h2 { font-size: 12pt; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; color: #000; margin-top: 40px; border-left: 3px solid #000; padding-left: 15px; }
            .experience-item { margin-bottom: 25px; }
            .job-header { font-weight: 600; color: #000; }
            .job-dates { color: #999; font-size: 9pt; }
            .skill-tag { margin-right: 15px; font-weight: 500; color: #666; }
        """
    }
    return styles.get(template_name, styles["Modern"])

def generate_html_cv(data, template_name="Modern"):
    lang = data.get("lang", "en")
    css = get_template_styles(template_name)
    headers = {
        "es": {"exp": "Experiencia Profesional", "edu": "Educación", "cert": "Certificaciones", "skills": "Habilidades Técnicas", "sum": "Resumen Profesional", "no_exp": "No se detectó experiencia detallada."},
        "en": {"exp": "Professional Experience", "edu": "Education", "cert": "Certifications", "skills": "Technical Skills", "sum": "Professional Summary", "no_exp": "No detailed experience detected."},
        "de": {"exp": "Berufserfahrung", "edu": "Ausbildung", "cert": "Zertifizierungen", "skills": "Technische Fähigkeiten", "sum": "Zusammenfassung", "no_exp": "Keine detaillierte Erfahrung gefunden."},
        "it": {"exp": "Esperienza Professionale", "edu": "Istruzione", "cert": "Certificazioni", "skills": "Competenze Tecniche", "sum": "Profilo Professionale", "no_exp": "Nessuna experiencia detallata rilevata."}
    }
    t = headers.get(lang, headers["en"])
    template_html = f"""
    <!DOCTYPE html>
    <html lang="{{{{ lang }}}}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{{{ name }}}} - CV</title>
        <style>
            {css}
            @media print {{ body {{ background: white; margin: 0; padding: 0; }} .cv-container {{ box-shadow: none; border: none; padding: 0; }} }}
        </style>
    </head>
    <body>
        <div class="cv-container">
            <header>
                <h1>{{{{ name }}}}</h1>
                <div class="contact-info">{{{{ contact_info }}}}</div>
            </header>
            {{% if summary %}}
            <section>
                <h2>{t['sum']}</h2>
                <p class="summary-text">{{{{ summary }}}}</p>
            </section>
            {{% endif %}}
            <section>
                <h2>{t['exp']}</h2>
                {{% for job in experience %}}
                <div class="experience-item">
                    <div class="job-header">
                        <span>{{{{ job.title }}}}</span>
                        <span class="job-dates">{{{{ job.dates }}}}</span>
                    </div>
                    <div class="job-details">{{{{ job.company }}}}</div>
                    <ul>
                        {{% for b in job.bullets %}}
                        <li>{{{{ b }}}}</li>
                        {{% endfor %}}
                    </ul>
                </div>
                {{% else %}}
                <p>{t['no_exp']}</p>
                {{% endfor %}}
            </section>
            {{% if education %}}
            <section>
                <h2>{t['edu']}</h2>
                <p>{{{{ education }}}}</p>
            </section>
            {{% endif %}}
            {{% if certifications %}}
            <section>
                <h2>{t['cert']}</h2>
                <ul>
                    {{% for cert in certifications %}}
                    <li>{{{{ cert }}}}</li>
                    {{% endfor %}}
                </ul>
            </section>
            {{% endif %}}
            <section>
                <h2>{t['skills']}</h2>
                <div class="skills-container">
                    {{% for skill in skills %}}
                    <span class="skill-tag">{{{{ skill }}}}</span>
                    {{% endfor %}}
                </div>
            </section>
        </div>
    </body>
    </html>
    """
    from jinja2 import Template
    template = Template(template_html)
    return template.render(**data)
