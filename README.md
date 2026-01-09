# 🚀 CV Optimizer (Estilo Resumego)

Optimiza tu currículum vitae (CV) con Inteligencia Artificial local (Llama 3) para maximizar su impacto y compatibilidad con los Sistemas de Seguimiento de Candidatos (ATS).

## 🌟 Características Principales

Este proyecto ofrece una solución completa para el procesamiento y la mejora de CVs, construida sobre una pila tecnológica moderna y localizable:

*   **Soporte Multilingüe:** Procesa CVs en **español e inglés**.
*   **Extracción Flexible:** Permite subir el CV en formato **PDF** o pegar el texto plano directamente.
*   **Detección de Industria:** Identifica automáticamente la industria del candidato para aplicar optimizaciones contextuales.
*   **Optimización con LLM Local:** Utiliza **Llama 3** a través de **Ollama** para reescribir y mejorar los puntos de experiencia, transformándolos en logros cuantificables.
*   **Salida ATS-Friendly:** Genera un CV optimizado en formato **HTML limpio**, diseñado para ser fácilmente parseado por los sistemas ATS.
*   **Despliegue Sencillo:** Listo para ser ejecutado con **Docker** y `docker-compose`, incluyendo el servicio de Ollama.

## 🧠 Funcionamiento de la Optimización

El proceso de optimización se centra en tres etapas clave para asegurar un CV de alto impacto:

1.  **Extracción y Segmentación:** Se extrae el texto del PDF (o se usa el texto pegado) y se segmenta en secciones clave (Experiencia, Educación, Habilidades).
2.  **Análisis Contextual:**
    *   Se detecta el idioma principal del CV.
    *   Se analiza el contenido para determinar la **industria** (e.g., Tech, Finance, HR) mediante un sistema de palabras clave.
3.  **Mejora de Logros (Llama 3):**
    *   Cada punto de la sección de Experiencia es enviado a Llama 3 con un *prompt* de ingeniería específico.
    *   El modelo reescribe el punto, enfocándose en el uso de **verbos de acción fuertes** y sugiriendo la inclusión de **métricas y resultados cuantificables** (el lenguaje que buscan los ATS).
4.  **Generación Final:** El contenido mejorado se integra en una plantilla HTML simple y estructurada, ideal para ser leído por humanos y máquinas (ATS).

## ▶️ Guía de Inicio Rápido (Recomendado)

La forma más sencilla de poner en marcha el CV Optimizer es utilizando Docker Compose, ya que gestiona automáticamente la aplicación Streamlit y el servidor de Ollama.

### 1. Requisitos Previos

Asegúrate de tener instalado:
*   **Docker** y **Docker Compose** (o Docker Desktop).

### 2. Descarga del Modelo Llama 3

Antes de ejecutar el contenedor, debes asegurarte de que el modelo `llama3` esté disponible en tu instancia de Ollama.

```bash
# Si tienes Ollama instalado localmente
ollama pull llama3
```

### 3. Ejecución con Docker Compose

Desde el directorio raíz del proyecto, ejecuta:

```bash
docker-compose up --build
```

Esto iniciará dos servicios: `ollama` y `cv-optimizer`.

### 4. Acceso a la Aplicación

Una vez que ambos servicios estén activos, accede a la aplicación Streamlit en tu navegador:

```
http://localhost:8501
```

## ⚙️ Instalación Local (Avanzado)

Si prefieres ejecutar la aplicación directamente en tu entorno Python:

### 1. Requisitos

*   Python 3.10+
*   Un servidor **Ollama** ejecutándose localmente en `http://localhost:11434` con el modelo `llama3` descargado.

### 2. Configuración del Entorno

```bash
# Crear y activar un entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos de spaCy
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm
```

### 3. Ejecución de la Aplicación

```bash
streamlit run app.py
```

## 🛠️ Estructura del Proyecto

| Archivo | Descripción |
| :--- | :--- |
| `app.py` | Aplicación principal Streamlit. Maneja la interfaz de usuario, la carga de archivos y la visualización de resultados. |
| `cv_processor.py` | Lógica central de procesamiento. Contiene funciones para la detección de idioma, parsing de secciones, extracción de habilidades y la comunicación con Llama 3. |
| `industry_keywords.json` | Base de datos de palabras clave y verbos de acción para la detección de industria y la optimización de *prompts*. |
| `requirements.txt` | Dependencias de Python necesarias (`streamlit`, `spacy`, `pdfplumber`, `requests`, etc.). |
| `Dockerfile` | Instrucciones para construir la imagen Docker de la aplicación. |
| `docker-compose.yml` | Configuración para ejecutar la aplicación junto con el servicio de Ollama. |

## 📜 Historial de Cambios

Para ver el detalle de todas las actualizaciones y mejoras, consulta el archivo [CHANGELOG.md](CHANGELOG.md).

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
