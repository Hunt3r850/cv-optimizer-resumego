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

st.set_page_config(page_title="Optimizador de CV - Resumego Style", layout="wide")
st.title("✨ Optimizador de CV (Resumego Style)")
st.markdown("""
Copia tu CV o **súbelo en PDF**. El sistema:
- Detecta idioma (es/en)
- Identifica tu industria
- Mejora puntos con **Llama 3 local**
- Genera CV **compatible con ATS**
""")

uploaded_file = st.file_uploader("📂 Sube tu CV en PDF", type=["pdf"])
cv_text = ""

if uploaded_file is not None:
    with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
        cv_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    cv_text = st.text_area("Texto extraído (edita si es necesario):", value=cv_text, height=200)
else:
    cv_text = st.text_area("O pega tu CV en texto plano:", height=200)

if st.button("🚀 Optimizar CV"):
    if not cv_text.strip():
        st.error("Por favor, ingresa texto o sube un PDF.")
    else:
        with st.spinner("Procesando... (esto puede tardar unos segundos con Llama 3)"):
            try:
                lang = detect_language(cv_text)
                auto_industry = detect_industry(cv_text, lang)
                industry = auto_industry if auto_industry in INDUSTRIES else "tech"

                st.info(f"Idioma: {'Español' if lang == 'es' else 'English'} | Industria detectada: {industry}")

                sections = parse_cv_text(cv_text, lang)
                experience = process_experience(sections.get("experience", []), industry, lang)
                education = " ".join(sections.get("education", ["No especificado"]))
                all_text = " ".join(sections.get("experience", []) + sections.get("skills", []))
                skills = extract_skills(all_text, industry, lang)
                if not skills:
                    skills = ["No detectadas"]

                html_cv = generate_html_cv(
                    name="Tu Nombre",
                    experience=experience,
                    education=education,
                    skills=", ".join(skills),
                    lang=lang
                )

                st.success("✅ CV optimizado con éxito")
                st.download_button(
                    label="📥 Descargar CV mejorado (HTML)",
                    data=html_cv,
                    file_name="cv_optimizado.html",
                    mime="text/html"
                )
                st.components.v1.html(html_cv, height=600, scrolling=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.code(str(e))