# Bitbucket SBOM Generator

Questo strumento genera Software Bill of Materials (SBOM) per i repository Bitbucket utilizzando Syft.

## Caratteristiche

- Analisi automatica di tutti i repository in un workspace Bitbucket
- Generazione di SBOM in formato CycloneDX JSON
- Generazione opzionale di file NOTICE.txt
- Supporto per vari linguaggi di programmazione e framework
- Integrazione con Docker per una facile distribuzione

## Linguaggi e Framework Supportati

Lo strumento supporta l'analisi dei seguenti linguaggi e framework:

### JavaScript/TypeScript
- Progetti JavaScript/TypeScript generici
- Framework supportati:
  - Angular (rilevato da angular.json)
  - React (rilevato da package.json o presenza di react/react-dom)
  - Vue.js (rilevato da vue.config.js, file .vue o package.json)
- Package Manager supportati:
  - npm (package.json)
  - Yarn (yarn.lock)
  - pnpm (pnpm-lock.yaml)

### C/C++
- Progetti C/C++ generici
- Build system supportati:
  - CMake (CMakeLists.txt)
  - Make (Makefile)
- File supportati:
  - `.c`, `.cpp` (file sorgente)
  - `.h`, `.hpp` (file header)

### Altri Linguaggi
- .NET (C#, F#, VB.NET)
- Python
- Java
- Ruby
- Go
- PHP

## Requisiti

- Docker
- Accesso a Bitbucket con App Password
- Workspace Bitbucket configurato

## Configurazione

1. Crea un file `.env` nella directory del progetto con le seguenti variabili:
   ```
   BITBUCKET_USERNAME=your_username
   BITBUCKET_APP_PASSWORD=your_app_password
   BITBUCKET_WORKSPACE=your_workspace
   GENERATE_NOTICE=true|false|only
   ```

2. Assicurati che l'App Password di Bitbucket abbia i seguenti permessi:
   - Repository Read
   - Repository Write

## Utilizzo

1. Costruisci l'immagine Docker:
   ```bash
   docker compose build
   ```

2. Esegui il generatore:
   ```bash
   docker compose run --rm sbom-generator
   ```

## Output

### SBOM (CycloneDX JSON)
Il file SBOM viene generato nella directory `output` con il nome `sbom_[repository_name]_[timestamp].json`.

### NOTICE.txt
Se abilitato, viene generato un file NOTICE.txt nella directory `output` con il nome `NOTICE_[repository_name]_[timestamp].txt`.

## Formato SBOM

Il file SBOM generato segue il formato CycloneDX JSON e include:

- Metadati del repository
- Componenti e dipendenze
- Licenze
- Informazioni di versione
- PURL (Package URL) per ogni componente

## Formato NOTICE

Il file NOTICE generato include:

- Data e ora di generazione
- Nome del repository
- Lista dei componenti di terze parti
- Informazioni sulle licenze
- Package URL per ogni componente

## Variabili d'Ambiente

- `BITBUCKET_USERNAME`: Username Bitbucket
- `BITBUCKET_APP_PASSWORD`: App Password Bitbucket
- `BITBUCKET_WORKSPACE`: Nome del workspace Bitbucket
- `GENERATE_NOTICE`: Modalità di generazione del file NOTICE
  - `true`: Genera sia SBOM che NOTICE
  - `false`: Genera solo SBOM
  - `only`: Genera solo NOTICE (richiede un SBOM esistente)

## Note

- I file SBOM e NOTICE vengono generati nella directory `output`
- I file vengono nominati con timestamp per evitare sovrascritture
- In caso di errore su un repository, lo script continua con il successivo

## Licenza

MIT 