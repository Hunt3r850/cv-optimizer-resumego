# Registro de Cambios (CHANGELOG) - CV Optimizer

Todas las actualizaciones notables de este proyecto se detallan a continuación.

## [2.0.2] - 2026-01-09
### ✨ Mejoras y Nuevas Funcionalidades
- **Galería de Ejemplos Completa:** Se han añadido 12 ejemplos reales (3 plantillas x 4 idiomas) en la carpeta `/examples` para demostrar la versatilidad del sistema.
- **Sincronización de Documentación:** README.md actualizado con enlaces directos a la galería de ejemplos.

## [2.0.0] - 2026-01-09
### ✨ Mejoras y Nuevas Funcionalidades
- **Sistema de Plantillas Dinámicas:** Ahora puedes elegir entre tres diseños profesionales:
  - **Modern:** Diseño colorido y dinámico con fuentes modernas.
  - **Executive:** Estilo clásico y serio, ideal para perfiles senior.
  - **Minimalist:** Limpio, directo y extremadamente legible para ATS.
- **Parsing JSON de Nivel Industrial:** Reingeniería total del motor de extracción para evitar errores de formato.
- **Sistema de Auto-Reparación de Datos:** Si la IA genera un formato incorrecto, el sistema lo detecta y lo corrige automáticamente en tiempo real.
- **Interfaz Renovada:** Selector de plantillas en la barra lateral y vista previa mejorada.

## [1.5.1] - 2026-01-09
### 🐛 Correcciones y Robustez
- **Parsing JSON Ultra-Robusto:** Se ha implementado un sistema de limpieza y validación de JSON para evitar errores cuando la IA incluye texto extra o comentarios.
- **Prompt Estricto:** Refinamiento de las instrucciones a Llama 3 para forzar una salida de datos pura y estructurada.
- **Sistema de Auto-Reparación:** Si el primer intento de parsing falla, el sistema intenta reparar el objeto JSON automáticamente.

## [1.5.0] - 2026-01-09
### ✨ Mejoras y Nuevas Funcionalidades
- **AI-Powered Parsing (Llama 3):** Se ha sustituido el parsing basado en reglas por una extracción contextual inteligente. Llama 3 ahora identifica secciones, cargos y logros de forma dinámica.
- **Estructuración JSON:** Los datos se procesan ahora en formato JSON estructurado, garantizando que ninguna sección (como contacto o certificaciones) se pierda.
- **Optimización Multilingüe Superior:** La IA ahora reescribe los logros directamente en el idioma objetivo, manteniendo la coherencia gramatical y profesional en EN, ES, DE e IT.

## [1.4.0] - 2026-01-09
### ✨ Mejoras y Nuevas Funcionalidades
- **Soporte Multilingüe Completo:** Ahora puedes optimizar CVs en **Español, Inglés, Alemán e Italiano**.
- **Selector de Idioma:** Nueva interfaz que permite elegir el idioma de salida y la industria.
- **Modelos NLP Específicos:** Integración de modelos de spaCy para cada idioma, mejorando drásticamente la precisión de la extracción.
- **Prompts Adaptativos:** Llama 3 ahora recibe instrucciones en el idioma nativo del CV para una optimización más natural.

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
