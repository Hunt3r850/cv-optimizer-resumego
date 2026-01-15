import streamlit as st
from cv_processor import (
    detect_language,
    parse_cv_text,
    extract_skills,
    process_experience,
    generate_html_cv,
    detect_industry
)
import pdfplumber
from io import BytesIO

INDUSTRIES = ["tech", "finance", "healthcare", "hr", "engineering"]
LANGUAGES = {
    "es": "Español 🇪🇸",
    "en": "English 🇺🇸",
    "de": "Deutsch 🇩🇪",
    "it": "Italiano 🇮🇹"
}

st.set_page_config(page_title="Optimizador de CV Multilingüe - ATS Master", layout="wide")

st.title("🌍 Optimizador de CV Multilingüe (ATS Master)")
st.markdown("""
Optimiza tu CV para sistemas ATS en múltiples idiomas utilizando **Llama 3** y **NLP avanzado**.
- **Multilingüe:** Soporte completo para Español, Inglés, Alemán e Italiano.
- **Estructura Semántica:** Genera HTML optimizado para reclutadores y algoritmos.
- **Mejora de Contenido:** Reescribe tus logros con verbos de acción potentes en el idioma elegido.
""")

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    selected_lang = st.selectbox(
        "Selecciona el idioma del CV:",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=0
    )
    
    selected_industry = st.selectbox(
        "Selecciona tu industria (o deja que el sistema la detecte):",
        options=["Auto-detectar"] + [i.capitalize() for i in INDUSTRIES]
    )

uploaded_file = st.file_uploader("📂 Sube tu CV en PDF", type=["pdf"])
cv_text = ""

if uploaded_file is not None:
    with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
        cv_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    cv_text = st.text_area("Texto extraído (puedes corregir errores de lectura aquí):", value=cv_text, height=250)
else:
    cv_text = st.text_area("O pega tu CV en texto plano aquí:", height=250)

if st.button("🚀 Optimizar y Generar CV ATS"):
    if not cv_text.strip():
        st.error("Por favor, ingresa texto o sube un PDF.")
    else:
        with st.spinner(f"Analizando y optimizando en {LANGUAGES[selected_lang]} con Llama 3..."):
            try:
                # 1. Análisis básico
                lang = selected_lang
                
                if selected_industry == "Auto-detectar":
                    auto_industry = detect_industry(cv_text, lang)
                    industry = auto_industry if auto_industry in INDUSTRIES else "tech"
                else:
                    industry = selected_industry.lower()
                
                # 2. Parsing de secciones
                sections = parse_cv_text(cv_text, lang)
                
                # 3. Procesamiento de datos
                name = sections.get("contact", ["Tu Nombre"])[0] if sections.get("contact") else "Tu Nombre"
                contact_info = " | ".join(sections.get("contact", [])[1:4]) if len(sections.get("contact", [])) > 1 else "Ciudad, País | Email | LinkedIn"
                
                summary = " ".join(sections.get("summary", []))
                if not summary and sections.get("contact"):
                    # Fallback para resumen si no hay encabezado claro
                    summary = " ".join(sections.get("contact", [])[4:8])
                
                experience = process_experience(sections.get("experience", []), industry, lang)
                education = " ".join(sections.get("education", ["No especificado"]))
                certifications = sections.get("certifications", [])
                
                skills = extract_skills(cv_text, industry, lang)
                
                # 4. Preparar datos para la plantilla
                cv_data = {
                    "name": name,
                    "contact_info": contact_info,
                    "summary": summary,
                    "experience": experience,
                    "education": education,
                    "certifications": certifications,
                    "skills": skills,
                    "lang": lang
                }
                
                # 5. Generar HTML
                html_cv = generate_html_cv(cv_data)
                
                st.success(f"✅ CV optimizado con éxito en {LANGUAGES[lang]}")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.info(f"**Idioma:** {LANGUAGES[lang]}")
                    st.info(f"**Industria:** {industry.upper()}")
                    st.download_button(
                        label=f"📥 Descargar CV {lang.upper()} (HTML)",
                        data=html_cv,
                        file_name=f"cv_optimizado_{lang}.html",
                        mime="text/html"
                    )
                    
                    with st.expander("Ver detalles técnicos"):
                        st.write(f"Secciones detectadas: {list(sections.keys())}")
                        st.write(f"Habilidades extraídas: {len(skills)}")
                
                with col2:
                    st.markdown("### Vista Previa")
                    st.components.v1.html(html_cv, height=800, scrolling=True)

            except Exception as e:
                st.error(f"Error durante el procesamiento: {str(e)}")
                st.exception(e)
