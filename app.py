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

st.set_page_config(page_title="Optimizador de CV - ATS Master", layout="wide")

st.title("✨ Optimizador de CV (ATS Master)")
st.markdown("""
Esta herramienta utiliza **Llama 3** y **NLP avanzado** para transformar tu CV en una versión optimizada para sistemas ATS.
- **Estructura Semántica:** Genera HTML que los reclutadores y algoritmos adoran.
- **Mejora de Contenido:** Reescribe tus logros para que sean más impactantes.
- **Detección Automática:** Identifica tu industria y habilidades clave.
""")

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
        with st.spinner("Analizando y optimizando con Llama 3..."):
            try:
                # 1. Análisis básico
                lang = detect_language(cv_text)
                auto_industry = detect_industry(cv_text, lang)
                industry = auto_industry if auto_industry in INDUSTRIES else "tech"
                
                # 2. Parsing de secciones
                sections = parse_cv_text(cv_text, lang)
                
                # 3. Procesamiento de datos
                name = sections.get("contact", ["Tu Nombre"])[0] if sections.get("contact") else "Tu Nombre"
                contact_info = " | ".join(sections.get("contact", [])[1:4]) if len(sections.get("contact", [])) > 1 else "Ciudad, País | Email | LinkedIn"
                
                summary = " ".join(sections.get("summary", []))
                if not summary and sections.get("contact"):
                    # A veces el resumen se queda en la sección de contacto si no hay encabezado
                    summary = " ".join(sections.get("contact", [])[4:8])
                
                experience = process_experience(sections.get("experience", []), industry, lang)
                education = " ".join(sections.get("education", ["No especificado"]))
                certifications = sections.get("certifications", [])
                
                all_text_for_skills = cv_text
                skills = extract_skills(all_text_for_skills, industry, lang)
                
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
                
                st.success("✅ CV optimizado con éxito")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.info(f"**Idioma:** {'Español' if lang == 'es' else 'English'}")
                    st.info(f"**Industria detectada:** {industry.upper()}")
                    st.download_button(
                        label="📥 Descargar CV ATS (HTML)",
                        data=html_cv,
                        file_name="cv_optimizado_ats.html",
                        mime="text/html"
                    )
                
                with col2:
                    st.markdown("### Vista Previa")
                    st.components.v1.html(html_cv, height=800, scrolling=True)

            except Exception as e:
                st.error(f"Error durante el procesamiento: {str(e)}")
                st.exception(e)
