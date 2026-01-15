#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando configuración local de CV Optimizer...${NC}"

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor, instálalo antes de continuar."
    exit 1
fi

# 2. Crear entorno virtual
echo -e "${BLUE}📦 Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
echo -e "${BLUE}📥 Instalando dependencias de Python...${NC}"
pip install --upgrade pip setuptools wheel
# Intentar instalar spacy con binarios precompilados para evitar errores de compilación en Python 3.13
pip install "spacy>=3.7.5" --only-binary=:all: || pip install "spacy>=3.7.5"
pip install -r requirements.txt

# 4. Descargar modelos de spaCy
echo -e "${BLUE}🧠 Descargando modelos de procesamiento de lenguaje (spaCy)...${NC}"
python3 -m spacy download es_core_news_sm
python3 -m spacy download en_core_web_sm
python3 -m spacy download de_core_news_sm
python3 -m spacy download it_core_news_sm

# 5. Verificar Ollama
echo -e "${BLUE}🦙 Verificando Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${GREEN}💡 Ollama no detectado en el PATH. Asegúrate de tenerlo instalado (https://ollama.com/)${NC}"
else
    echo -e "${GREEN}✅ Ollama detectado. Asegurando que Llama 3 esté disponible...${NC}"
    ollama pull llama3
fi

echo -e "${GREEN}✅ Configuración completada con éxito.${NC}"
echo -e "${BLUE}Para iniciar la aplicación, ejecuta:${NC}"
echo -e "source venv/bin/activate"
echo -e "streamlit run app.py"
