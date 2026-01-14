# Registro de Cambios (CHANGELOG) - CV Optimizer

Todas las actualizaciones notables de este proyecto se detallan a continuación.

## [1.3.0] - 2026-01-09

### ✨ Mejoras y Nuevas Funcionalidades
- **Parsing Estructurado Completo:** Nueva lógica de extracción que captura información de contacto, resumen profesional y certificaciones.
- **Plantilla Profesional Premium:** Rediseño total del HTML con una estética moderna y profesional, manteniendo la compatibilidad 100% con ATS.
- **Mejora en la Interfaz:** Interfaz de Streamlit actualizada para mostrar una vista previa más amplia y detalles de la industria.

## [1.2.0] - 2026-01-09

### ✨ Mejoras y Nuevas Funcionalidades
- **Nueva Plantilla ATS-Friendly:** Se ha integrado una estructura HTML optimizada para sistemas de seguimiento de candidatos, mejorando la jerarquía semántica y la legibilidad por máquinas.
- **Soporte de Ejecución Nativa:** Se ha adaptado el proyecto para funcionar localmente sin necesidad de Docker, facilitando el desarrollo y las pruebas rápidas.
- **Detección Dinámica de Ollama:** El procesador ahora detecta automáticamente si Ollama se ejecuta en `localhost` o dentro de una red Docker.
- **Script de Configuración Automática (`setup.sh`):** Nuevo script que automatiza la creación del entorno virtual, instalación de dependencias y descarga de modelos de spaCy y Ollama.

### 🐛 Correcciones de Errores
- **Solución a Error de Instalación de spaCy:** Se ha corregido el fallo de compilación en Python 3.13 forzando el uso de binarios precompilados en el script de instalación.
- **Optimización de Dependencias:** Actualización de `requirements.txt` para asegurar compatibilidad con las versiones más recientes de las librerías de NLP.

### 📝 Documentación
- **README Renovado:** Instrucciones completas para ejecución nativa y Docker, descripción de arquitectura y guía de uso.
- **Informe de Optimización:** Se ha incluido un análisis técnico detallado sobre cómo mejorar el parsing de CVs mediante LLMs.

## [1.0.0] - 2026-01-06
- Versión inicial del proyecto con soporte para Streamlit, spaCy y Llama 3.
- Funcionalidad básica de extracción de PDF y optimización de puntos de experiencia.
- Soporte inicial para Docker y Docker Compose.
