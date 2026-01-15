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

def improve_bullet_with_llama(bullet: str, industry: str, lang: str):
    keywords, verbs = get_keywords_and_verbs(industry, lang)
    verbs_str = ", ".join(verbs)
    
    prompts = {
        "es": (f"Reescribe este punto de CV para que sea más impactante, usando verbos de acción fuertes "
               f"y sugiriendo un espacio para una métrica si falta. Usa tono profesional. "
               f"Solo devuelve la oración mejorada.\n\nIndustria: {industry}\n"
               f"Verbos recomendados: {verbs_str}\n\nOriginal: \"{bullet}\"\nMejorado:"),
        "en": (f"Rewrite this CV bullet point to be more impactful, using strong action verbs "
               f"and adding a placeholder for a metric if missing. Use professional tone. "
               f"Only return the improved sentence.\n\nIndustry: {industry}\n"
               f"Preferred verbs: {verbs_str}\n\nOriginal: \"{bullet}\"\nImproved:"),
        "de": (f"Schreiben Sie diesen CV-Aufzählungspunkt um, um ihn wirkungsvoller zu gestalten, "
               f"verwenden Sie starke Aktionsverben und fügen Sie einen Platzhalter für eine Metrik hinzu, falls diese fehlt. "
               f"Verwenden Sie einen professionellen Ton. Geben Sie nur den verbesserten Satz zurück.\n\n"
               f"Branche: {industry}\nEmpfohlene Verben: {verbs_str}\n\nOriginal: \"{bullet}\"\nVerbessert:"),
        "it": (f"Riscrivi questo punto del CV per renderlo più incisivo, usando verbi d'azione forti "
               f"e aggiungendo un segnaposto per una metrica se mancante. Usa un tono professionale. "
               f"Restituisci solo la frase migliorata.\n\nSettore: {industry}\n"
               f"Verbi consigliati: {verbs_str}\n\nOriginale: \"{bullet}\"\nMigliorato:")
    }
    
    prompt = prompts.get(lang, prompts["en"])

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
    
    # Términos de búsqueda para secciones en múltiples idiomas
    terms_map = {
        "experience": {
            "en": ["experience", "work history", "professional experience", "employment"],
            "es": ["experiencia", "historial laboral", "experiencia profesional"],
            "de": ["berufserfahrung", "werdegang", "arbeitserfahrung"],
            "it": ["esperienza", "esperienze professionali", "storia lavorativa"]
        },
        "education": {
            "en": ["education", "academic", "studies"],
            "es": ["educación", "formación", "estudios", "academia"],
            "de": ["ausbildung", "studium", "bildung"],
            "it": ["istruzione", "formazione", "studi"]
        },
        "certifications": {
            "en": ["certifications", "courses", "awards"],
            "es": ["certificaciones", "cursos", "premios", "diplomas"],
            "de": ["zertifizierungen", "kurse", "auszeichnungen"],
            "it": ["certificazioni", "corsi", "premi"]
        },
        "skills": {
            "en": ["skills", "competencies", "expertise", "technologies"],
            "es": ["habilidades", "competencias", "conocimientos", "tecnologías"],
            "de": ["kenntnisse", "fertigkeiten", "kompetenzen", "it-kenntnisse"],
            "it": ["competenze", "abilità", "conoscenze", "tecnologie"]
        },
        "summary": {
            "en": ["summary", "profile", "about me", "objective"],
            "es": ["resumen", "perfil", "sobre mí", "objetivo"],
            "de": ["zusammenfassung", "profil", "über mich"],
            "it": ["riepilogo", "profilo", "su di me", "obiettivo"]
        }
    }
    
    # Obtener términos para el idioma actual o inglés por defecto
    current_terms = {sec: langs.get(lang, langs["en"]) for sec, langs in terms_map.items()}
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip: continue
        
        line_lower = line_strip.lower().rstrip(":")
        
        found_section = False
        for sec, keywords in current_terms.items():
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
    
    # Conectores de lugar en varios idiomas
    connectors = {
        "en": ["at", "in", "|"],
        "es": ["en", "en", "|"],
        "de": ["bei", "in", "|"],
        "it": ["presso", "a", "|"]
    }
    conn_list = connectors.get(lang, connectors["en"])
    conn_regex = "|".join([re.escape(c) for c in conn_list])
    
    for line in experience_lines:
        # Intentar detectar una nueva posición: Cargo [conector] Empresa (Fecha)
        match = re.search(rf"(.+?)(?:\s+(?:{conn_regex})\s+)(.+?)(?:\s+[\(\[|]\s*(.+?)\s*[\)\]|]|$)", line, re.IGNORECASE)
        
        if match:
            title, company, dates = match.groups()
            current_job = {
                "title": title.strip(),
                "company": company.strip(),
                "dates": dates.strip() if dates else "Present",
                "bullets": []
            }
            jobs.append(current_job)
        elif line.startswith(("-", "•", "*")) and current_job is not None:
            clean_bullet = re.sub(r"^[-•*]\s*", "", line).strip()
            improved = improve_bullet_with_llama(clean_bullet, industry, lang)
            current_job["bullets"].append(improved)
        elif current_job is not None and len(line) > 10:
            improved = improve_bullet_with_llama(line, industry, lang)
            current_job["bullets"].append(improved)
            
    return jobs

def generate_html_cv(data):
    lang = data.get("lang", "en")
    
    # Traducciones de encabezados
    headers = {
        "es": {"exp": "Experiencia Profesional", "edu": "Educación", "cert": "Certificaciones", "skills": "Habilidades Técnicas", "sum": "Resumen Profesional", "no_exp": "No se detectó experiencia detallada."},
        "en": {"exp": "Professional Experience", "edu": "Education", "cert": "Certifications", "skills": "Technical Skills", "sum": "Professional Summary", "no_exp": "No detailed experience detected."},
        "de": {"exp": "Berufserfahrung", "edu": "Ausbildung", "cert": "Zertifizierungen", "skills": "Technische Fähigkeiten", "sum": "Zusammenfassung", "no_exp": "Keine detaillierte Erfahrung gefunden."},
        "it": {"exp": "Esperienza Professionale", "edu": "Istruzione", "cert": "Certificazioni", "skills": "Competenze Tecniche", "sum": "Profilo Professionale", "no_exp": "Nessuna esperienza dettagliata rilevata."}
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
