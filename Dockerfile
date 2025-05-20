FROM python:3.12-slim

# Installa Git e Syft
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installa Syft (ultima versione)
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Crea e imposta la directory di lavoro
WORKDIR /app

# Copia i file del progetto
COPY requirements.txt .
COPY bitbucket_sbom_generator.py .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Crea la directory per l'output
RUN mkdir /output

# Imposta le variabili d'ambiente
ENV PYTHONUNBUFFERED=1

# Comando di default
CMD ["python", "bitbucket_sbom_generator.py"] 