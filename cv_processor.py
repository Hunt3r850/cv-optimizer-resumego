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

with open("industry_keywords.json", encoding="utf-8") as f:
    INDUSTRY_DB = json.load(f)

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        if lang in MODELS:
            return lang
        return "en"
    except:
        return "en"

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
            if ent.label_ in ("ORG", "PRODUCT", "MISC", "I-ORG", "I-MISC"):
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
        lang_data = data.get(lang, data["en"])
        keywords = lang_data["keywords"]
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
            timeout=90
        )
        if response.ok:
            return response.json().get("response", "").strip()
    except:
        pass
    return ""

def clean_json_response(response: str):
    """
    Limpia la respuesta de la IA para extraer un objeto JSON válido.
    """
    try:
        # Buscar el primer '{' y el último '}'
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = response[start:end]
            # Eliminar posibles comentarios o texto extra dentro del bloque
            return json.loads(json_str)
    except Exception as e:
        print(f"Error limpiando JSON: {e}")
    return None

def ai_parse_cv(cv_text: str, lang: str):
    """
    Usa Llama 3 para estructurar el CV en un formato JSON limpio con un prompt ultra-estricto.
    """
    prompt = f"""
    TASK: Convert the following CV text into a valid JSON object.
    LANGUAGE: {lang}
    RULES:
    1. Output ONLY the JSON object. No preamble, no explanation.
    2. Use the exact keys provided below.
    3. Rewrite experience bullets to be impactful in {lang} using strong action verbs.
    4. If a field is missing, use an empty string or empty list.

    JSON STRUCTURE:
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

    CV TEXT TO PROCESS:
    {cv_text}
    """
    
    response = call_llama(prompt, temperature=0.1)
    data = clean_json_response(response)
    
    # Si falla el primer intento, probar con un prompt de reparación
    if not data:
        repair_prompt = f"Fix this broken JSON and return ONLY the valid JSON object:\n{response}"
        response = call_llama(repair_prompt, temperature=0.0)
        data = clean_json_response(response)
        
    return data

def generate_html_cv(data):
    lang = data.get("lang", "en")
    
    # Traducciones de encabezados
    headers = {
        "es": {"exp": "Experiencia Profesional", "edu": "Educación", "cert": "Certificaciones", "skills": "Habilidades Técnicas", "sum": "Resumen Profesional", "no_exp": "No se detectó experiencia detallada."},
        "en": {"exp": "Professional Experience", "edu": "Education", "cert": "Certifications", "skills": "Technical Skills", "sum": "Professional Summary", "no_exp": "No detailed experience detected."},
        "de": {"exp": "Berufserfahrung", "edu": "Ausbildung", "cert": "Zertifizierungen", "skills": "Technische Fähigkeiten", "sum": "Zusammenfassung", "no_exp": "Keine detaillierte Erfahrung gefunden."},
        "it": {"exp": "Esperienza Professionale", "edu": "Istruzione", "cert": "Certificazioni", "skills": "Competenze Tecniche", "sum": "Profilo Professionale", "no_exp": "Nessuna experiencia dettagliata rilevata."}
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
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 850px; margin: 40px auto; padding: 0 40px; background-color: #fff; }}
            header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; }}
            h1 {{ font-size: 28pt; margin-bottom: 5px; color: #2c3e50; text-transform: uppercase; letter-spacing: 2px; }}
            .contact-info {{ font-size: 10pt; color: #7f8c8d; }}
            h2 {{ font-size: 16pt; text-transform: uppercase; border-bottom: 2px solid #bdc3c7; margin-top: 30px; margin-bottom: 15px; color: #2c3e50; padding-bottom: 5px; }}
            h3 {{ font-size: 13pt; margin-top: 15px; margin-bottom: 5px; color: #34495e; }}
            .job-header {{ display: flex; justify-content: space-between; font-weight: bold; color: #2c3e50; }}
            .job-details {{ font-style: italic; margin-bottom: 8px; color: #7f8c8d; }}
            ul {{ margin-top: 8px; padding-left: 25px; }}
            li {{ margin-bottom: 6px; }}
            .summary-text {{ text-align: justify; font-style: italic; }}
            .skills-container {{ display: flex; flex-wrap: wrap; gap: 10px; }}
            .skill-tag {{ background: #ecf0f1; padding: 4px 12px; border-radius: 15px; font-size: 9pt; border: 1px solid #dcdde1; }}
            @media print {{ body {{ margin: 0; padding: 20px; }} .skill-tag {{ border: 1px solid #ccc; }} }}
        </style>
    </head>
    <body>
        <header>
            <h1>{{{{ name }}}}</h1>
            <div class="contact-info">
                {{{{ contact_info }}}}
            </div>
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
                    <span>{{{{ job.dates }}}}</span>
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
    </body>
    </html>
    """
    from jinja2 import Template
    template = Template(template_html)
    return template.render(**data)
