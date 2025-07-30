# 🚀 TecnoCursos AI - Como Iniciar o Sistema

## ⚡ INÍCIO RÁPIDO

### Método 1 - Clique Duplo (Mais Fácil)
1. **Clique duas vezes** no arquivo: `INICIAR_SERVIDOR.bat`
2. Aguarde o sistema inicializar
3. Acesse: http://127.0.0.1:8000

### Método 2 - PowerShell
1. **Clique com botão direito** em `INICIAR_SISTEMA.ps1`
2. Selecione **"Executar com PowerShell"**
3. Aguarde o sistema inicializar

### Método 3 - Terminal Manual
```bash
# Abra o PowerShell ou CMD e execute:
python simple_backend.py
```

### Método 4 - Uvicorn
```bash
# Se tiver uvicorn instalado:
uvicorn simple_backend:app --host 127.0.0.1 --port 8000 --reload
```

## 🌐 URLs do Sistema

Depois de iniciar, acesse:

- **🏠 Homepage:** http://127.0.0.1:8000
- **📚 Documentação da API:** http://127.0.0.1:8000/docs
- **❤️ Health Check:** http://127.0.0.1:8000/health
- **📊 Status:** http://127.0.0.1:8000/api/status

## 🔑 Credenciais de Teste

### Administrador
- **Email:** admin@tecnocursos.com
- **Senha:** admin123

### Usuário Normal
- **Email:** user@tecnocursos.com  
- **Senha:** user123

## 🛠️ Solução de Problemas

### ❌ Erro: "Python não encontrado"
**Solução:** Instale o Python de https://python.org

### ❌ Erro: "Módulo não encontrado"
**Solução:** Execute no terminal:
```bash
pip install fastapi uvicorn python-multipart pyjwt
```

### ❌ Erro: "Porta 8000 em uso"
**Solução:** Mate o processo ou use outra porta:
```bash
# Ver processos na porta 8000
netstat -ano | findstr :8000

# Usar porta diferente
uvicorn simple_backend:app --host 127.0.0.1 --port 8001
```

### ❌ Erro: "ERR_CONNECTION_REFUSED"
**Causa:** Servidor não está rodando
**Solução:** Siga um dos métodos de inicialização acima

## 📁 Estrutura do Projeto

```
TecnoCursosAI/
├── simple_backend.py          # Servidor principal
├── INICIAR_SERVIDOR.bat       # Script Windows
├── INICIAR_SISTEMA.ps1        # Script PowerShell  
├── EXECUTAR_SERVIDOR.py       # Executor Python
├── DIAGNOSTICO.py             # Ferramenta de diagnóstico
└── README_INICIAR.md          # Este arquivo
```

## 🎯 Testando o Sistema

Após iniciar, teste se está funcionando:

1. **Acesse:** http://127.0.0.1:8000
2. **Veja se aparece:** "TecnoCursos AI" com status verde
3. **Teste login:** Use admin@tecnocursos.com / admin123
4. **Explore a API:** http://127.0.0.1:8000/docs

## 🚨 Status do Sistema

### ✅ Sistema Online
- Página inicial carrega
- Health check retorna "healthy"
- Login funciona com credenciais de teste

### ❌ Sistema Offline  
- Página não carrega (ERR_CONNECTION_REFUSED)
- Health check não responde
- Servidor não está rodando

## 💡 Dicas

1. **Mantenha o terminal aberto** enquanto usar o sistema
2. **Use Ctrl+C** para parar o servidor
3. **Veja os logs** no terminal para debug
4. **Use o Simple Browser** do VS Code para testes rápidos

## 🆘 Suporte

Se nada funcionar, execute o diagnóstico:
```bash
python DIAGNOSTICO.py
```

Este arquivo identificará automaticamente o problema e sugerirá soluções.

---

**✨ Sistema desenvolvido para resolver ERR_CONNECTION_REFUSED e fornecer plataforma completa de cursos com IA!**
