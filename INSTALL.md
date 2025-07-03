# 🚀 Guia de Instalação - SimpleMMO Bot v4.0.0

## 📋 Pré-requisitos

- ✅ **Python 3.10+** instalado
- ✅ **Git** instalado (opcional)
- ✅ **Brave Browser** ou **Chrome** instalado
- ✅ **VS Code** (recomendado)

---

## ⚡ Instalação Rápida

### Método 1: Script Automático (Windows)

1. **Clone ou baixe o projeto**
2. **Execute o script de setup**:
   ```cmd
   setup.bat
   ```
3. **Execute o bot**:
   ```cmd
   run.bat
   ```

### Método 2: Manual

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
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure o bot**:
   ```bash
   copy config.example.json config.json
   # Edite config.json com seus caminhos
   ```

6. **Execute o bot**:
   ```bash
   python src/main.py
   ```

---

## ⚙️ Configuração

### 🎯 **ChromeDriver - Detecção Automática**

**Método Simples (Recomendado):**
1. **Baixe o ChromeDriver** do [chromedriver.chromium.org](https://chromedriver.chromium.org)
2. **Coloque o arquivo** `chromedriver.exe` na **raiz do projeto** (junto com `src/`)
3. **Pronto!** O bot detectará automaticamente 🎉

### 📁 config.json

Copie `config.example.json` para `config.json`:

```json
{
    "chromedriver_path": "./chromedriver.exe",
    "remote_debugging_address": "127.0.0.1:9222",
    "url": "https://web.simple-mmo.com/travel",
    "brave_profile_path": "C:\\\\temp\\\\brave_profile"
}
```

**💡 Dica**: Use `"./chromedriver.exe"` para detecção automática!

### 🔧 Configurações Importantes

- **chromedriver_path**: Caminho para o chromedriver.exe
- **brave_profile_path**: Diretório para perfil temporário do Brave
- **remote_debugging_address**: Endereço para debugging remoto

---

## 🎯 Uso com VS Code (Recomendado)

1. **Abra o projeto no VS Code**
2. **Instale extensões recomendadas** (será sugerido automaticamente)
3. **Pressione** `Ctrl+Shift+P`
4. **Digite**: `Tasks: Run Task`
5. **Escolha uma task**:
   - 🚀 **Run SimpleMMO Bot** - Executar o bot
   - 📦 **Install Dependencies** - Instalar dependências
   - 🧪 **Test Environment** - Testar ambiente

---

## 🔍 Solução de Problemas

### ❌ Erro: "python não é reconhecido"
- Instale Python 3.10+ do [python.org](https://python.org)
- Marque "Add to PATH" durante a instalação

### ❌ Erro: "chromedriver não encontrado"
- Baixe chromedriver do [chromedriver.chromium.org](https://chromedriver.chromium.org)
- Atualize o caminho em `config.json`

### ❌ Erro: "Brave não abre"
- Verifique se o Brave está instalado no caminho padrão
- O caminho correto está em `src/driver/manager.py`

### ❌ Erro: "venv não encontrado"
- Execute `setup.bat` primeiro
- Ou crie manualmente: `python -m venv venv`

---

## 📞 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/[seu-usuario]/SimpleMMO-Bot/issues)
- 📖 **Wiki**: [GitHub Wiki](https://github.com/[seu-usuario]/SimpleMMO-Bot/wiki)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/[seu-usuario]/SimpleMMO-Bot/discussions)

---

## ✅ Verificação da Instalação

Execute este teste para verificar se tudo está funcionando:

```bash
# Ativar ambiente
venv\Scripts\activate

# Testar imports
python -c "import selenium; print('✅ Selenium OK')"
python -c "import tkinter; print('✅ Tkinter OK')" 
python -c "import requests; print('✅ Requests OK')"

# Testar módulos do bot
python -c "from src.ui.gui import iniciar_interface; print('✅ Bot OK')"
```

Se todos os testes passarem, sua instalação está pronta! 🎉
