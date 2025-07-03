# 🎮 SimpleMMO Bot v4.0.0 - Arquitetura Simplificada

> **Bot automatizado para SimpleMMO com interface gráfica moderna e arquitetura limpa**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.23%2B-green)](https://selenium.dev)
[![Status](https://img.shields.io/badge/Status-Estável-brightgreen)]()
[![Version](https://img.shields.io/badge/Version-4.0.0-orange)]()

---

## ✨ Características Principais

- 🎯 **Foco nas Essenciais**: Apenas funcionalidades core (Coleta, Combate, Steps)
- 🖥️ **Interface Moderna**: GUI simplificada e responsiva
- 🎯 **ChromeDriver Auto-Detection**: Detecta automaticamente o chromedriver na raiz do projeto
- 🔧 **Fácil Configuração**: Setup automatizado com VS Code
- 🛡️ **Estável**: Código limpo e bem testado
- 🚀 **Performance**: Arquitetura otimizada

---

## 🚀 Instalação e Uso

### ⚡ Instalação Rápida

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/[seu-usuario]/SimpleMMO-Bot.git
   cd SimpleMMO-Bot
   ```

2. **Crie o ambiente virtual**:
   ```bash
   python -m venv venv
   ```

3. **Ative o ambiente virtual**:
   ```bash
   # Windows
   venv\\Scripts\\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute o bot**:
   ```bash
   python src/main.py
   ```

### 🎯 Uso com VS Code (Recomendado)

1. **Abra o projeto no VS Code**
2. **Pressione** `Ctrl+Shift+P`
3. **Digite**: `Tasks: Run Task`
4. **Selecione**: `🚀 Run SimpleMMO Bot`

---

## 📁 Arquitetura do Projeto

```
SimpleMMO-Bot/
├── src/                     # 📦 Código-fonte principal
│   ├── core/                # 🎯 Funcionalidades essenciais (8 arquivos)
│   │   ├── bot_loop.py      # Loop principal do bot
│   │   ├── fight.py         # Sistema de combate
│   │   ├── gather.py        # Sistema de coleta
│   │   ├── step.py          # Sistema de steps
│   │   ├── healing.py       # Sistema de cura
│   │   ├── captcha.py       # Resolução de captcha
│   │   ├── context.py       # Contexto do bot
│   │   └── __init__.py
│   ├── driver/              # 🚗 Integração com browser (3 arquivos)
│   │   ├── manager.py       # Gerenciamento do driver
│   │   ├── actions.py       # Ações do navegador
│   │   └── __init__.py
│   ├── ui/                  # 🖥️ Interface gráfica (6 arquivos)
│   │   ├── gui.py           # Interface principal
│   │   ├── components.py    # Componentes UI
│   │   ├── controller.py    # Controlador
│   │   ├── data_manager.py  # Gerenciador de dados
│   │   ├── base.py          # Classes base
│   │   └── __init__.py
│   ├── utils/               # 🛠️ Utilitários (5 arquivos)
│   │   ├── config.py        # Configurações
│   │   ├── logger.py        # Sistema de logs
│   │   ├── timing.py        # Controle de tempo
│   │   ├── notifier.py      # Notificações
│   │   └── __init__.py
│   └── main.py              # 🚪 Ponto de entrada principal
├── .vscode/                 # ⚙️ Configurações VS Code
├── config.json              # 📋 Configurações do bot
├── pyproject.toml           # 🐍 Configurações Python
└── requirements.txt         # 📦 Dependências
```

---

## 🎮 Funcionalidades

### 🎯 Core Essencial
- **Steps**: Movimentação automática no mapa
- **Coleta**: Sistema de gathering automático
- **Combate**: Batalhas automáticas
- **Cura**: Sistema de healing inteligente
- **Captcha**: Resolução automática

### 🖥️ Interface
- **Dashboard moderno**: Interface gráfica intuitiva
- **Logs em tempo real**: Acompanhe todas as ações
- **Controles simples**: Start/Stop com um clique
- **Configuração fácil**: Settings integrados

### 🔧 Browser Integration
- **Brave Browser**: Suporte nativo ao Brave
- **Debugging remoto**: Conecta a instâncias existentes
- **Auto-recovery**: Reconexão automática

---

## ⚙️ Configuração

### 🎯 **Detecção Automática de ChromeDriver**

O bot agora detecta automaticamente o ChromeDriver! Simplesmente coloque o arquivo `chromedriver.exe` na **raiz do projeto** (junto com o `src/`) e o bot irá encontrá-lo automaticamente.

**Locais de busca (em ordem de prioridade):**
1. `./chromedriver.exe` (raiz do projeto)
2. `./chromedriver` (Linux/Mac)
3. `./drivers/chromedriver.exe` (subpasta drivers)
4. `./drivers/chromedriver` (Linux/Mac)

### 📋 config.json
```json
{
    "chromedriver_path": "./chromedriver.exe",
    "remote_debugging_address": "127.0.0.1:9222",
    "url": "https://web.simple-mmo.com/travel",
    "brave_profile_path": "C:\\\\temp\\\\brave_profile"
}
```

**💡 Dica**: Use `"./chromedriver.exe"` para detecção automática ou especifique um caminho absoluto para um local específico.

### 🎯 Personalizações
- **Intervalos**: Configure tempos entre ações
- **Prioridades**: Defina ordem das operações
- **Limites**: Configure HP mínimo para cura
- **Logs**: Personalize nível de detalhamento

---

## 🛠️ Desenvolvimento

### 📦 Dependências
```txt
selenium>=4.23.0
tkinter (incluído no Python)
```

### 🧪 Testes
```bash
# Executar todos os testes
pytest

# Executar com coverage
pytest --cov=src
```

### 🎨 Code Quality
```bash
# Formatação
ruff format src/

# Linting
ruff check src/ --fix

# Type checking
mypy src/
```

---

## 🤝 Contribuindo

1. **Fork o projeto**
2. **Crie sua feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit suas mudanças**: `git commit -m 'Add AmazingFeature'`
4. **Push para a branch**: `git push origin feature/AmazingFeature`
5. **Abra um Pull Request**

---

## 📝 Changelog

### v4.0.0 - Arquitetura Simplificada
- ✅ **Limpeza massiva**: Removidos 80% dos arquivos desnecessários
- ✅ **Foco essencial**: Apenas funcionalidades core mantidas
- ✅ **Interface simplificada**: GUI limpa e responsiva
- ✅ **Correções Windows**: Paths e tasks corrigidos
- ✅ **Brave integration**: Botão "Abrir Brave" funcionando

### v3.0.0 - Sistema Modular
- ✅ Sistema de quest avançado
- ✅ Interface modular completa
- ✅ Arquitetura flexível

---

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## ⚠️ Disclaimer

Este bot é para fins educacionais e de automação pessoal. Use com responsabilidade e respeite os termos de serviço do SimpleMMO.

---

## 📞 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/[seu-usuario]/SimpleMMO-Bot/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/[seu-usuario]/SimpleMMO-Bot/discussions)

---

**⭐ Se este projeto te ajudou, considere dar uma estrela!**
