import json
from pathlib import Path
from typing import Dict

CONFIG_PATH = "config.json"

def get_project_root() -> Path:
    """Retorna o diretório raiz do projeto (onde está o main.py)."""
    # Procura pelo main.py subindo na hierarquia de diretórios
    current_path = Path(__file__).resolve()
    
    # Subir até encontrar main.py ou atingir a raiz do sistema
    for parent in current_path.parents:
        main_py_path = parent / "src" / "main.py"
        if main_py_path.exists():
            return parent
        
        # Alternativa: procurar main.py diretamente na pasta
        main_py_direct = parent / "main.py"
        if main_py_direct.exists():
            return parent
    
    # Fallback: usar diretório atual
    return Path.cwd()

def get_chromedriver_path() -> str:
    """Detecta automaticamente o caminho do chromedriver na raiz do projeto."""
    project_root = get_project_root()
    
    # Possíveis localizações do chromedriver
    possible_paths = [
        project_root / "chromedriver.exe",  # Windows
        project_root / "chromedriver",      # Linux/Mac
        project_root / "drivers" / "chromedriver.exe",
        project_root / "drivers" / "chromedriver",
    ]
    
    # Usar next() para encontrar o primeiro caminho válido
    return next((str(path.resolve()) for path in possible_paths if path.exists()), "./chromedriver.exe")

DEFAULT_CONFIG = {
    "chromedriver_path": "./chromedriver.exe",
    "remote_debugging_address": "127.0.0.1:9222",
    "url": "https://web.simple-mmo.com/travel",
    "brave_profile_path": "C:\\temp\\brave_profile",
}


def carregar_config() -> Dict[str, str]:
    """Carrega a configuração, criando arquivo padrão se não existir."""
    project_root = get_project_root()
    config_path = project_root / CONFIG_PATH
    
    # Criar config padrão se não existir
    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    
    # Carregar configuração
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    
    # Auto-detectar chromedriver se configurado como relativo
    if config.get("chromedriver_path", "").startswith("./"):
        detected_path = get_chromedriver_path()
        config["chromedriver_path"] = detected_path
    
    return config
