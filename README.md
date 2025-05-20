# Bitbucket SBOM Generator

Questo strumento genera Software Bill of Materials (SBOM) per i repository Bitbucket utilizzando Syft.

## Caratteristiche

- Analisi automatica di tutti i repository in un workspace Bitbucket
- Generazione di SBOM in formato CycloneDX JSON
- Generazione opzionale di file NOTICE.txt
- Supporto per vari linguaggi di programmazione e framework
- Integrazione con Docker per una facile distribuzione
- Formattazione automatica dei file JSON per una migliore leggibilità
- Esecuzione in container Docker per isolamento e portabilità

## Perché CycloneDX?

CycloneDX è stato scelto come formato SBOM per diversi motivi:
- È uno standard OWASP riconosciuto
- Supporta un'ampia gamma di linguaggi e package manager
- Fornisce un formato JSON ben strutturato e facilmente processabile
- Include informazioni dettagliate su licenze e vulnerabilità
- È supportato da molti strumenti di sicurezza e compliance

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

- Docker e Docker Compose
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

### Con Docker (Raccomandato)

1. Costruisci l'immagine Docker:
   ```bash
   docker compose build
   ```

2. Esegui il generatore:
   ```bash
   docker compose run --rm sbom-generator
   ```

### Con Python (Sviluppo)

1. Crea un ambiente virtuale:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oppure
   .\venv\Scripts\activate  # Windows
   ```

2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

3. Installa Syft:
   ```bash
   curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
   ```

4. Esegui lo script:
   ```bash
   python bitbucket_sbom_generator.py
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

### Esempio di struttura SBOM:
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "metadata": {
    "timestamp": "2024-02-20T12:00:00Z",
    "tools": [
      {
        "vendor": "Anchore",
        "name": "Syft",
        "version": "1.0.0"
      }
    ]
  },
  "components": [
    {
      "type": "library",
      "name": "package-name",
      "version": "1.0.0",
      "purl": "pkg:npm/package-name@1.0.0",
      "licenses": [
        {
          "name": "MIT"
        }
      ]
    }
  ]
}
```

### Spiegazione dei campi principali:
- `bomFormat`: Indica il formato del file (CycloneDX)
- `specVersion`: Versione della specifica CycloneDX utilizzata
- `metadata`: Informazioni sulla generazione del SBOM
  - `timestamp`: Data e ora di generazione
  - `tools`: Strumenti utilizzati per la generazione
- `components`: Lista dei componenti rilevati
  - `type`: Tipo di componente (library, application, framework, etc.)
  - `name`: Nome del componente
  - `version`: Versione del componente
  - `purl`: Package URL univoco del componente
  - `licenses`: Informazioni sulle licenze

## Formato NOTICE

Il file NOTICE generato include:

- Data e ora di generazione
- Nome del repository
- Lista dei componenti di terze parti
- Informazioni sulle licenze
- Package URL per ogni componente

### Esempio di struttura NOTICE:
```
NOTICE for repository-name
================================================================================

Generated on: 2024-02-20 12:00:00

This file contains attributions and license information for third-party software used in this project.

Third-party Components:
--------------------------------------------------------------------------------

License: MIT
----------------------------------------
- package-name 1.0.0
  Source: pkg:npm/package-name@1.0.0

License: Apache-2.0
----------------------------------------
- another-package 2.0.0
  Source: pkg:npm/another-package@2.0.0
```

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
- Il generatore rileva automaticamente i linguaggi principali nel repository e usa i cataloger Syft appropriati
- Se non vengono rilevati linguaggi principali, viene eseguita un'analisi generica
- I file JSON vengono formattati automaticamente per una migliore leggibilità

## Licenza

MIT 