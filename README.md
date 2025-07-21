# TecnoCursosAI - Customização do Dashboard

## feat: customizar dashboard da rota principal do FastAPI

---

## 📁 Estrutura do Projeto

- `quick_server.py`: Endpoint principal do dashboard e lógica de contexto dinâmico.
- `templates/dashboard.html`: Template HTML do dashboard (Jinja2).
- `static/css/dashboard.css`: Estilos modernos e responsivos do dashboard.
- `README_COMPLETO_FINAL.md`: Documentação detalhada do sistema.

---

## 🎨 Como Personalizar o Dashboard

### 1. Editar Textos e Nomes do Sistema
- **Arquivo:** `quick_server.py`
- **Como:**
  - Os textos principais (nome do sistema, versão, subtítulo, autor, ambiente) são definidos por variáveis de ambiente ou diretamente no início do arquivo.
  - Exemplo:
    ```python
    SYSTEM_NAME = os.getenv("SYSTEM_NAME", "TecnoCursos AI")
    SYSTEM_VERSION = os.getenv("SYSTEM_VERSION", "2.0.0")
    SYSTEM_SUBTITLE = os.getenv("SYSTEM_SUBTITLE", "Monitoramento Inteligente de Vídeos e IA")
    ```
  - Para alterar, edite as variáveis ou defina-as no ambiente de execução.

### 2. Editar Componentes, Métricas e Ações Rápidas
- **Arquivo:** `quick_server.py`
- **Como:**
  - No método `get_dashboard_context`, edite os arrays `component_status`, `system_metrics` e `quick_actions`.
  - Exemplo para adicionar um novo componente:
    ```python
    component_status = [
        {"name": "Novo Serviço", "status": "online", "icon": "🆕", "description": "Descrição do serviço", "details": "Detalhes"},
        # ... outros componentes ...
    ]
    ```

### 3. Editar Textos e Layout HTML
- **Arquivo:** `templates/dashboard.html`
- **Como:**
  - O template utiliza variáveis Jinja2 para exibir dados dinâmicos.
  - Para alterar textos fixos, edite diretamente o HTML.
  - Para adicionar novas seções, siga a estrutura de blocos `<section>` já existente.

### 4. Editar Cores, Gradientes e Tipografia
- **Arquivo:** `static/css/dashboard.css`
- **Como:**
  - Todas as cores, gradientes, espaçamentos e fontes estão definidos em variáveis CSS no início do arquivo (`:root`).
  - Exemplo:
    ```css
    :root {
      --primary-color: #3b82f6;
      --gradient-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      --font-family: 'Inter', sans-serif;
      /* ... */
    }
    ```
  - Para alterar o visual, basta modificar os valores dessas variáveis.

### 5. Adicionar Dados Dinâmicos
- **Arquivo:** `quick_server.py`
- **Como:**
  - Para integrar dados reais (ex: banco de dados, APIs), substitua os valores estáticos nos arrays por consultas dinâmicas.
  - Exemplo:
    ```python
    # Exemplo de integração com banco de dados
    component_status = get_components_from_db()
    ```

---

## 🛠️ Dicas Rápidas
- Sempre reinicie o servidor após alterações em arquivos Python.
- Alterações em HTML e CSS podem ser vistas ao recarregar a página.
- Use as variáveis de ambiente para customizar rapidamente o nome, versão e ambiente do sistema sem alterar o código.
- Consulte a documentação automática da API em `/docs` (Swagger UI) e `/redoc` (ReDoc).

---

## ⚙️ Exemplos de Configuração de Ambiente

### Variáveis de Ambiente (Exemplo)

```bash
# Ambiente de desenvolvimento
export SYSTEM_NAME="TecnoCursos AI DEV"
export SYSTEM_VERSION="2.1.0-dev"
export SYSTEM_ENV="dev"
export SYSTEM_SUBTITLE="Dashboard de Desenvolvimento"
export SYSTEM_AUTHOR="Equipe Dev"

# Ambiente de produção
export SYSTEM_NAME="TecnoCursos AI"
export SYSTEM_VERSION="2.1.0"
export SYSTEM_ENV="prod"
export SYSTEM_SUBTITLE="Sistema de Geração de Vídeos"
export SYSTEM_AUTHOR="Equipe TecnoCursos"
```

### Comandos de Execução

#### Ambiente de Desenvolvimento
```bash
python quick_server.py
```

#### Ambiente de Produção (exemplo com Uvicorn)
```bash
uvicorn quick_server:app --host 0.0.0.0 --port 8001 --workers 4
```

---

## 🖼️ Prints e GIFs do Dashboard

Inclua capturas de tela ou GIFs do dashboard para facilitar o onboarding de novos desenvolvedores e demonstrar o visual do sistema.

- **Como adicionar:**
  - Salve as imagens na pasta `docs/` ou `assets/`.
  - No README, adicione:
    ```markdown
    ![Dashboard Principal](docs/dashboard_print.png)
    ```
  - Para GIFs:
    ```markdown
    ![Demo Dashboard](docs/dashboard_demo.gif)
    ```

---

## 📚 Referências
- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Guia de boas práticas para README](https://github.com/Tinymrsb/READMEhowto)

---

**Mantenha o código limpo, documentado e modular para facilitar futuras expansões!** 