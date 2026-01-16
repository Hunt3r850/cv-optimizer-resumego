import streamlit as st
from cv_processor import (
    detect_language,
    ai_parse_cv,
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

st.set_page_config(page_title="Optimizador de CV IA - ATS Master", layout="wide")

st.title("🤖 Optimizador de CV con IA (ATS Master v1.5)")
st.markdown("""
Esta versión utiliza **Parsing Inteligente con Llama 3** para garantizar que tu CV se extraiga correctamente sin importar el idioma o formato.
- **IA-Powered Parsing:** Llama 3 identifica secciones, cargos y logros de forma contextual.
- **Multilingüe Real:** Optimización nativa en Español, Inglés, Alemán e Italiano.
- **Formato ATS Premium:** Estructura semántica de alta compatibilidad.
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
        "Selecciona tu industria:",
        options=["Auto-detectar"] + [i.capitalize() for i in INDUSTRIES]
    )

uploaded_file = st.file_uploader("📂 Sube tu CV en PDF", type=["pdf"])
cv_text = ""

if uploaded_file is not None:
    with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
        cv_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    cv_text = st.text_area("Texto extraído del PDF:", value=cv_text, height=250)
else:
    cv_text = st.text_area("O pega tu CV en texto plano aquí:", height=250)

if st.button("🚀 Optimizar con IA"):
    if not cv_text.strip():
        st.error("Por favor, ingresa texto o sube un PDF.")
    else:
        with st.spinner(f"La IA está analizando y reestructurando tu CV en {LANGUAGES[selected_lang]}..."):
            try:
                # 1. Detección de industria si es necesario
                if selected_industry == "Auto-detectar":
                    industry = detect_industry(cv_text, selected_lang)
                else:
                    industry = selected_industry.lower()
                
                # 2. Parsing Inteligente con Llama 3
                cv_data = ai_parse_cv(cv_text, selected_lang)
                
                if cv_data:
                    # Asegurar que el idioma esté en los datos
                    cv_data["lang"] = selected_lang
                    
                    # 3. Generar HTML
                    html_cv = generate_html_cv(cv_data)
                    
                    st.success(f"✅ CV optimizado con éxito con IA en {LANGUAGES[selected_lang]}")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.info(f"**Idioma:** {LANGUAGES[selected_lang]}")
                        st.info(f"**Industria:** {industry.upper()}")
                        st.download_button(
                            label=f"📥 Descargar CV {selected_lang.upper()} (HTML)",
                            data=html_cv,
                            file_name=f"cv_optimizado_{selected_lang}.html",
                            mime="text/html"
                        )
                        
                        with st.expander("Ver JSON extraído por IA"):
                            st.json(cv_data)
                    
                    with col2:
                        st.markdown("### Vista Previa")
                        st.components.v1.html(html_cv, height=800, scrolling=True)
                else:
                    st.error("La IA no pudo estructurar el CV correctamente. Intenta con un texto más claro.")

            except Exception as e:
                st.error(f"Error durante el procesamiento: {str(e)}")
                st.exception(e)
