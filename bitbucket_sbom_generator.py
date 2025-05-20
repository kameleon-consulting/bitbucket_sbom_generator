import os
import sys
import json
import requests
import subprocess
import tempfile
import shutil
from datetime import datetime
from dotenv import load_dotenv
import urllib.parse

class BitbucketSBOMGenerator:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('BITBUCKET_USERNAME')
        self.app_password = os.getenv('BITBUCKET_APP_PASSWORD')
        self.workspace = os.getenv('BITBUCKET_WORKSPACE')
        self.output_dir = '/output'  # Directory di output nel container Docker
        
        # Configurazione generazione file
        notice_mode = os.getenv('GENERATE_NOTICE', 'true').lower()
        self.generate_sbom = notice_mode != 'only'  # Genera SBOM se non è 'only'
        self.generate_notice = notice_mode in ['true', 'only']  # Genera NOTICE se 'true' o 'only'

        if not all([self.username, self.app_password, self.workspace]):
            print("Errore: Configura le variabili d'ambiente BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD e BITBUCKET_WORKSPACE")
            sys.exit(1)

        print(f"Workspace: {self.workspace}")
        print(f"Username: {self.username}")
        print(f"App Password: {'*' * len(self.app_password)}")
        print(f"Generate SBOM: {self.generate_sbom}")
        print(f"Generate NOTICE: {self.generate_notice}")

    def get_repositories(self):
        url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}"
        response = requests.get(url, auth=(self.username, self.app_password))
        
        print(f"URL API: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text: {response.text[:500]}...")  # Mostra solo i primi 500 caratteri
        
        if response.status_code == 200:
            return response.json().get('values', [])
        else:
            raise Exception(f"Errore API: {response.status_code} - {response.text}")

    def format_json_file(self, file_path):
        """Formatta un file JSON per migliorare la leggibilità."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, sort_keys=True)
            
            print(f"\nFile SBOM formattato: {file_path}")
        except Exception as e:
            print(f"\nErrore durante la formattazione del file JSON {file_path}: {str(e)}")

    def detect_main_language_catalogers(self, repo_dir):
        """Rileva i linguaggi principali e restituisce i Syft cataloger appropriati."""
        catalogers = []
        
        # Rilevamento progetti JavaScript/TypeScript
        js_files = subprocess.run(['find', repo_dir, '-name', '*.js', '-o', '-name', '*.ts', '-o', '-name', '*.jsx', '-o', '-name', '*.tsx'], capture_output=True, text=True).stdout.strip()
        if js_files:
            catalogers.append('javascript')
            print("Rilevati file JavaScript/TypeScript")
        
        # Rilevamento package manager e framework
        if subprocess.run(['find', repo_dir, '-name', 'package.json'], capture_output=True, text=True).stdout.strip():
            catalogers.append('npm')
            print("Rilevato package.json (npm/yarn/pnpm)")
            
            # Verifica se è un progetto Angular
            if subprocess.run(['find', repo_dir, '-name', 'angular.json'], capture_output=True, text=True).stdout.strip():
                print("Rilevato progetto Angular")
            
            # Verifica se è un progetto React
            if subprocess.run(['find', repo_dir, '-name', 'react', '-o', '-name', 'react-dom'], capture_output=True, text=True).stdout.strip() or \
               subprocess.run(['grep', '-l', '"react"', os.path.join(repo_dir, 'package.json')], capture_output=True, text=True).stdout.strip():
                print("Rilevato progetto React")
            
            # Verifica se è un progetto Vue
            if subprocess.run(['find', repo_dir, '-name', 'vue.config.js', '-o', '-name', '*.vue'], capture_output=True, text=True).stdout.strip() or \
               subprocess.run(['grep', '-l', '"vue"', os.path.join(repo_dir, 'package.json')], capture_output=True, text=True).stdout.strip():
                print("Rilevato progetto Vue.js")
        
        # Rilevamento yarn
        if subprocess.run(['find', repo_dir, '-name', 'yarn.lock'], capture_output=True, text=True).stdout.strip():
            print("Rilevato yarn.lock (Yarn package manager)")
        
        # Rilevamento pnpm
        if subprocess.run(['find', repo_dir, '-name', 'pnpm-lock.yaml'], capture_output=True, text=True).stdout.strip():
            print("Rilevato pnpm-lock.yaml (pnpm package manager)")
        
        # Rilevamento C/C++
        c_files = subprocess.run(['find', repo_dir, '-name', '*.c', '-o', '-name', '*.cpp', '-o', '-name', '*.h', '-o', '-name', '*.hpp', '-o', '-name', 'CMakeLists.txt', '-o', '-name', 'Makefile'], capture_output=True, text=True).stdout.strip()
        if c_files:
            catalogers.append('c')
            print("Rilevati file C/C++")
            if subprocess.run(['find', repo_dir, '-name', 'CMakeLists.txt'], capture_output=True, text=True).stdout.strip():
                print("Rilevato progetto CMake")
            if subprocess.run(['find', repo_dir, '-name', 'Makefile'], capture_output=True, text=True).stdout.strip():
                print("Rilevato progetto Make")
        
        # Altri linguaggi
        if subprocess.run(['find', repo_dir, '-name', '*.csproj', '-o', '-name', '*.sln'], capture_output=True, text=True).stdout.strip():
            catalogers.append('dotnet')
        if subprocess.run(['find', repo_dir, '-name', 'requirements.txt'], capture_output=True, text=True).stdout.strip():
            catalogers.append('python')
        if subprocess.run(['find', repo_dir, '-name', 'pom.xml'], capture_output=True, text=True).stdout.strip():
            catalogers.append('java')
        if subprocess.run(['find', repo_dir, '-name', 'Gemfile'], capture_output=True, text=True).stdout.strip():
            catalogers.append('ruby')
        if subprocess.run(['find', repo_dir, '-name', 'go.mod'], capture_output=True, text=True).stdout.strip():
            catalogers.append('go')
        if subprocess.run(['find', repo_dir, '-name', 'composer.json'], capture_output=True, text=True).stdout.strip():
            catalogers.append('php')
        
        return catalogers

    def generate_notice_file(self, repository_name: str, sbom_file: str) -> str:
        """Genera un file NOTICE.txt basato sul contenuto del file SBOM."""
        try:
            # Genera il nome del file NOTICE con data e ora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            notice_file = f"/output/NOTICE_{repository_name}_{timestamp}.txt"
            
            # Leggi il file SBOM
            with open(sbom_file, 'r') as f:
                sbom_data = json.load(f)
            
            # Prepara il contenuto del file NOTICE
            notice_content = []
            notice_content.append("NOTICE FILE")
            notice_content.append("=" * 80)
            notice_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            notice_content.append(f"Repository: {repository_name}")
            notice_content.append("=" * 80)
            notice_content.append("\nThis file contains information about the third-party components used in this project.")
            notice_content.append("The following components and their licenses are included:\n")
            
            # Estrai le informazioni sui componenti
            if 'components' in sbom_data:
                for component in sbom_data['components']:
                    notice_content.append("-" * 80)
                    if 'name' in component:
                        notice_content.append(f"Component: {component['name']}")
                    if 'version' in component:
                        notice_content.append(f"Version: {component['version']}")
                    if 'licenses' in component and component['licenses']:
                        for license_info in component['licenses']:
                            if 'license' in license_info and 'id' in license_info['license']:
                                notice_content.append(f"License: {license_info['license']['id']}")
                    if 'purl' in component:
                        notice_content.append(f"Package URL: {component['purl']}")
                    notice_content.append("")
            
            # Scrivi il file NOTICE
            with open(notice_file, 'w') as f:
                f.write('\n'.join(notice_content))
            
            print(f"\nFile NOTICE generato: {notice_file}")
            return notice_file
            
        except Exception as e:
            print(f"Errore nella generazione del file NOTICE: {str(e)}")
            return None

    def find_latest_sbom(self, repo_name):
        """Trova l'ultimo file SBOM per il repository specificato."""
        try:
            files = [f for f in os.listdir(self.output_dir) if f.startswith(f'sbom_{repo_name}_') and f.endswith('.json')]
            if not files:
                return None
            return os.path.join(self.output_dir, sorted(files)[-1])
        except Exception as e:
            print(f"Errore nel trovare l'ultimo SBOM: {str(e)}")
            return None

    def process_repository(self, repo):
        repo_name = repo['name']
        # Costruisci l'URL di clone con credenziali (URL-encoded e senza slash finale dopo .git)
        clone_links = repo['links']['clone']
        https_link = next((l['href'] for l in clone_links if l['name'] == 'https'), None)
        if https_link:
            print(f"\nURL originale: {https_link}")
            # Rimuovi la slash finale solo se segue '.git'
            if https_link.endswith('.git/'):
                https_link = https_link[:-1]
                print(f"URL dopo rimozione slash: {https_link}")
            
            # Rimuovi l'username dall'URL se presente
            if '@' in https_link:
                protocol, rest = https_link.split('://', 1)
                _, rest = rest.split('@', 1)
                https_link = f"{protocol}://{rest}"
                print(f"URL dopo rimozione username: {https_link}")
            
            # URL-encode username e password
            username_enc = urllib.parse.quote(self.username)
            password_enc = urllib.parse.quote(self.app_password)
            protocol, rest = https_link.split('://', 1)
            clone_url = f"{protocol}://{username_enc}:{password_enc}@{rest}"
            print(f"URL finale con credenziali: {clone_url}")
        else:
            clone_url = repo['links']['clone'][0]['href']
        
        print("\n" + "="*80)
        print(f"Elaborazione repository: {repo_name}")
        print("="*80)

        # Se dobbiamo generare solo il NOTICE, verifichiamo se esiste un SBOM
        if not self.generate_sbom and self.generate_notice:
            latest_sbom = self.find_latest_sbom(repo_name)
            if latest_sbom:
                print(f"\nTrovato SBOM esistente: {latest_sbom}")
                self.generate_notice_file(repo_name, latest_sbom)
                return
            else:
                print(f"\nNessun SBOM trovato per {repo_name}. Generazione SBOM richiesta.")
                self.generate_sbom = True

        # Crea una directory temporanea per il clone
        temp_dir = tempfile.mkdtemp()
        try:
            if self.generate_sbom:
                print(f"Clonazione repository {repo_name} in {temp_dir}")
                subprocess.run(['git', 'clone', clone_url, temp_dir], check=True)
                
                # Genera il nome del file di output
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(self.output_dir, f'sbom_{repo_name}_{timestamp}.json')
                
                print(f"\nAnalisi del repository {repo_name} con Syft:")
                print(f"Directory: {temp_dir}")
                print(f"File di output: {output_file}")
                
                print("\nContenuto della directory:")
                subprocess.run(['ls', '-la', temp_dir], check=True)
                
                # Rileva i linguaggi principali
                catalogers = self.detect_main_language_catalogers(temp_dir)
                print(f"Cataloger Syft rilevati: {catalogers}")
                
                try:
                    if catalogers:
                        result = subprocess.run(
                            [
                                'syft',
                                temp_dir,
                                '--output', f'cyclonedx-json={output_file}',
                                '--select-catalogers', ','.join(catalogers),
                                '--scope', 'all-layers'
                            ],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                    else:
                        print("\nNessun linguaggio principale rilevato, eseguo analisi generica")
                        result = subprocess.run(
                            [
                                'syft',
                                temp_dir,
                                '--output', f'cyclonedx-json={output_file}',
                                '--scope', 'all-layers'
                            ],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                    
                    print(f"\nOutput di Syft:\n{result.stdout}")
                    if result.stderr:
                        print(f"\nErrori di Syft:\n{result.stderr}")
                    
                    # Formatta il file JSON generato
                    self.format_json_file(output_file)
                    
                    # Genera il file NOTICE se richiesto
                    if self.generate_notice:
                        self.generate_notice_file(repo_name, output_file)
                    
                except subprocess.CalledProcessError as e:
                    print(f"\nErrore durante l'esecuzione di Syft:")
                    print(f"Exit code: {e.returncode}")
                    print(f"Output: {e.stdout}")
                    print(f"Error: {e.stderr}")
                    raise
                
        except Exception as e:
            print(f"\nErrore durante l'elaborazione del repository {repo_name}:")
            print(f"Exit code: {getattr(e, 'returncode', 'N/A')}")
            print(f"Output: {getattr(e, 'stdout', 'N/A')}")
            print(f"Error: {getattr(e, 'stderr', 'N/A')}")
            raise
        finally:
            print(f"\nFine elaborazione repository: {repo_name}")
            print("="*80)
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def run(self):
        try:
            repositories = self.get_repositories()
            print("\nAnalisi di tutti i repository nel workspace\n")
            
            for repo in repositories:
                try:
                    self.process_repository(repo)
                except Exception as e:
                    print(f"\nErrore durante l'elaborazione del repository {repo['name']}:")
                    print(f"Exit code: {getattr(e, 'returncode', 'N/A')}")
                    print(f"Output: {getattr(e, 'stdout', 'N/A')}")
                    print(f"Error: {getattr(e, 'stderr', 'N/A')}")
                    continue  # Continua con il prossimo repository anche in caso di errore
                
        except Exception as e:
            print(f"Errore generale: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    generator = BitbucketSBOMGenerator()
    generator.run() 