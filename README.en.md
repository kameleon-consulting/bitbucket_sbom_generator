# Bitbucket SBOM Generator

This tool generates Software Bill of Materials (SBOM) for Bitbucket repositories using Syft.

## Features

- Automatic analysis of all repositories in a Bitbucket workspace
- SBOM generation in CycloneDX JSON format
- Optional NOTICE.txt file generation
- Support for various programming languages and frameworks
- Docker integration for easy distribution
- Automatic JSON file formatting for better readability
- Containerized execution for isolation and portability

## Why CycloneDX?

CycloneDX was chosen as the SBOM format for several reasons:
- It's a recognized OWASP standard
- Supports a wide range of languages and package managers
- Provides a well-structured and easily processable JSON format
- Includes detailed information about licenses and vulnerabilities
- Is supported by many security and compliance tools

## Supported Languages and Frameworks

The tool supports analysis of the following languages and frameworks:

### JavaScript/TypeScript
- Generic JavaScript/TypeScript projects
- Supported frameworks:
  - Angular (detected from angular.json)
  - React (detected from package.json or presence of react/react-dom)
  - Vue.js (detected from vue.config.js, .vue files or package.json)
- Supported package managers:
  - npm (package.json)
  - Yarn (yarn.lock)
  - pnpm (pnpm-lock.yaml)

### C/C++
- Generic C/C++ projects
- Supported build systems:
  - CMake (CMakeLists.txt)
  - Make (Makefile)
- Supported files:
  - `.c`, `.cpp` (source files)
  - `.h`, `.hpp` (header files)

### Other Languages
- .NET (C#, F#, VB.NET)
- Python
- Java
- Ruby
- Go
- PHP

## Requirements

- Docker and Docker Compose
- Bitbucket access with App Password
- Configured Bitbucket workspace

## Configuration

1. Create a `.env` file in the project directory with the following variables:
   ```
   BITBUCKET_USERNAME=your_username
   BITBUCKET_APP_PASSWORD=your_app_password
   BITBUCKET_WORKSPACE=your_workspace
   GENERATE_NOTICE=true|false|only
   ```

2. Ensure your Bitbucket App Password has the following permissions:
   - Repository Read

## Usage

### With Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker compose build
   ```

2. Run the generator:
   ```bash
   docker compose run --rm sbom-generator
   ```

### With Python (Development)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Syft:
   ```bash
   curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
   ```

4. Run the script:
   ```bash
   python bitbucket_sbom_generator.py
   ```

## Output

### SBOM (CycloneDX JSON)
The SBOM file is generated in the `output` directory with the name `sbom_[repository_name]_[timestamp].json`.

### NOTICE.txt
If enabled, a NOTICE.txt file is generated in the `output` directory with the name `NOTICE_[repository_name]_[timestamp].txt`.

## SBOM Format

The generated SBOM file follows the CycloneDX JSON format and includes:

- Repository metadata
- Components and dependencies
- Licenses
- Version information
- PURL (Package URL) for each component

### Example SBOM structure:
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

### Main fields explanation:
- `bomFormat`: Indicates the file format (CycloneDX)
- `specVersion`: CycloneDX specification version used
- `metadata`: Information about SBOM generation
  - `timestamp`: Generation date and time
  - `tools`: Tools used for generation
- `components`: List of detected components
  - `type`: Component type (library, application, framework, etc.)
  - `name`: Component name
  - `version`: Component version
  - `purl`: Unique Package URL for the component
  - `licenses`: License information

## NOTICE Format

The generated NOTICE file includes:

- Generation date and time
- Repository name
- List of third-party components
- License information
- Package URL for each component

### Example NOTICE structure:
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

## Environment Variables

- `BITBUCKET_USERNAME`: Bitbucket username
- `BITBUCKET_APP_PASSWORD`: Bitbucket App Password
- `BITBUCKET_WORKSPACE`: Bitbucket workspace name
- `GENERATE_NOTICE`: NOTICE file generation mode
  - `true`: Generate both SBOM and NOTICE
  - `false`: Generate only SBOM
  - `only`: Generate only NOTICE (requires existing SBOM)

## Notes

- SBOM and NOTICE files are generated in the `output` directory
- Files are named with timestamps to avoid overwriting
- If an error occurs on a repository, the script continues with the next one
- The generator automatically detects main languages in the repository and uses appropriate Syft catalogers
- If no main languages are detected, a generic analysis is performed
- JSON files are automatically formatted for better readability

## License

MIT 