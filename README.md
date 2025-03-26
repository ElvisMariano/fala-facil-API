# Fala Fácil API

API REST para o aplicativo Fala Fácil, uma plataforma de aprendizado de idiomas baseada em flashcards.

## Tecnologias

- Python 3.11+
- Django 5.0+
- Django REST Framework 3.14+
- PostgreSQL (produção) / SQLite (desenvolvimento)
- Poetry (gerenciamento de dependências)
- JWT (autenticação)
- Swagger/OpenAPI (documentação)
- Black, isort, flake8 (formatação e linting)
- Pytest (testes)

## Requisitos

- Python 3.11+
- Poetry

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/fala-facil-api.git
cd fala-facil-api
```

2. Instale as dependências:
```bash
make install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com suas configurações.

4. Execute as migrações:
```bash
cd src
poetry run python manage.py migrate
```

5. Crie um superusuário (opcional):
```bash
poetry run python manage.py createsuperuser
```

## Desenvolvimento

- Executar o servidor de desenvolvimento:
```bash
cd src
poetry run python manage.py runserver
```

- Formatar o código:
```bash
make format
```

- Executar o linter:
```bash
make lint
```

- Executar os testes:
```bash
make test
```

- Gerar relatório de cobertura:
```bash
make coverage
```

## Documentação da API

A documentação da API está disponível em:

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Estrutura do Projeto

```
fala-facil-api/
├── src/
│   ├── apps/
│   │   ├── achievements/    # App de conquistas
│   │   ├── flashcards/     # App de flashcards
│   │   ├── progress/       # App de progresso
│   │   └── users/          # App de usuários
│   ├── config/             # Configurações do projeto
│   └── manage.py
├── tests/                  # Testes
├── .env.example           # Exemplo de variáveis de ambiente
├── .gitignore
├── LICENSE                # Licença MIT
├── Makefile              # Comandos úteis
├── README.md             # Este arquivo
├── pyproject.toml        # Configuração do Poetry
└── setup.cfg             # Configuração das ferramentas
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes. 