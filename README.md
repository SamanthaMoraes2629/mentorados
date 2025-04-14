# 💻 Sistema de Autenticação Django
**Este projeto implementa um sistema de autenticação básico usando Django, com páginas de login e cadastro estilizadas com Tailwind CSS.**

 ## Funcionalidades
 
- Cadastro de novos usuários

- Login de usuários existentes

- Validação de formulários

- Mensagens de feedback para o usuário

- Design responsivo e moderno

## 🛠️ Tecnologias Utilizadas

- Django (Python)

- Tailwind CSS

- HTML5

- CSS3

## 🗂️ Estrutura do Projeto

```
PSW13/
├── mentorados/
│   ├── templates/
│   │   ├── auth_mentorado.html
│   │   ├── escolher_dia.html
│   │   ├── mentorados.html
│   │   ├── reunioes.html
│   │   ├── tarefa.html
│   │   └── tarefa_mentorado.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── auth.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── usuarios/
│   ├── migrations/
│   ├── templates/
│   │   ├── cadastro.html
│   │   └── login.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py

```

## ▶️ Como Executar

Clone o repositório:

```
bash

git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
Instale as dependências:
```


```bash

pip install -r requirements.txt
```

Execute as migrações:

```bash

python manage.py migrate

```

Inicie o servidor de desenvolvimento:


```bash
python manage.py runserver
```

## ✅ Requisitos

- Python 3.x

- Django

- Navegador moderno

## 📸 Screenshots

Página de Login

Página de Cadastro

--

## 📄 Licença

Distribuído sob a licença **MIT**. Veja LICENSE para mais informações.
