# 🗳️ Cadastro de Eleitores

Sistema web para cadastro de eleitores com informações de título e endereço.
**Funciona em computador e celular** (design responsivo).

---

## Funcionalidades

- ✅ Cadastrar eleitores (título, nome, CPF, endereço, zona/seção)
- ✅ Editar dados cadastrados
- ✅ Excluir eleitores
- ✅ Busca por nome, título, CPF ou cidade
- ✅ Consulta de CEP automática (ViaCEP)
- ✅ Máscara automática para CPF, telefone e CEP
- ✅ Design responsivo (desktop + mobile)
- ✅ API REST completa
- ✅ Dados salvos em SQLite (sem configuração de banco)

---

## Como Rodar

### 1. Instalar dependências

```bash
cd cadastro-eleitores
pip install -r requirements.txt
```

### 2. Iniciar o servidor

```bash
python app.py
```

### 3. Acessar

- **Computador:** http://localhost:5000
- **Celular:** http://<IP-da-maquina>:5000

> Para acessar pelo celular, ambos devem estar na mesma rede Wi-Fi.
> Descubra o IP com `ipconfig` (Windows) ou `ifconfig` (Mac/Linux).

---

## Estrutura

```
cadastro-eleitores/
├── app.py                  # Backend Flask + rotas API
├── requirements.txt        # Dependências Python
├── eleitores.db            # Banco SQLite (criado automaticamente)
├── templates/
│   └── index.html          # Página principal
└── static/
    ├── css/
    │   └── style.css       # Estilos responsivos
    └── js/
        └── main.js         # Lógica do frontend
```

---

## API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/eleitores` | Listar todos (suporta `?busca=`) |
| POST | `/api/eleitores` | Cadastrar novo eleitor |
| GET | `/api/eleitores/<id>` | Consultar um eleitor |
| PUT | `/api/eleitores/<id>` | Atualizar eleitor |
| DELETE | `/api/eleitores/<id>` | Excluir eleitor |
| GET | `/api/stats` | Estatísticas gerais |

---

## Campos Cadastrados

### Dados Pessoais
- Título Eleitoral (obrigatório)
- Nome Completo (obrigatório)
- CPF
- Data de Nascimento
- Sexo
- Telefone
- E-mail

### Endereço
- CEP (busca automática)
- Logradouro, Número, Complemento
- Bairro, Cidade, Estado

### Dados Eleitorais
- Zona Eleitoral
- Seção Eleitoral

### Observações
- Campo livre para anotações

---

## Tecnologias

- **Backend:** Python Flask
- **Banco:** SQLite (sem configuração)
- **Frontend:** HTML5 + CSS3 + JavaScript vanilla
- **API de CEP:** ViaCEP (gratuita)
- **Responsivo:** CSS Grid + Flexbox + Media Queries

---

## Nota sobre Produção

Este é um protótipo para uso local. Para produção, recomenda-se:
- Usar PostgreSQL ao invés de SQLite
- Adicionar autenticação de usuários
- Implementar HTTPS
- Usar um servidor WSGI (Gunicorn) reverso com Nginx
