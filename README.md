# Fala Fácil API

API REST para o aplicativo Fala Fácil, uma plataforma de aprendizado de idiomas baseada em flashcards.

## Funcionalidades

- Gerenciamento de decks de flashcards
- Sistema de progresso de estudo
- Sistema de conquistas
- Recomendação personalizada de decks
- Exportação e importação de decks
- Cache para otimização de performance
- Documentação completa da API

## Tecnologias

- Python 3.11
- Django 5.0
- Django REST Framework
- PostgreSQL
- Redis
- Docker
- AWS S3 (armazenamento de mídia)

## Requisitos

- Python 3.11+
- Poetry
- PostgreSQL
- Redis

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/fala-facil-api.git
cd fala-facil-api
```

2. Instale as dependências:
```bash
poetry install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Execute as migrações:
```bash
poetry run python src/manage.py migrate
```

5. Inicie o servidor:
```bash
poetry run python src/manage.py runserver
```

## Documentação da API

A documentação da API está disponível em três formatos:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`

## Endpoints Principais

### Decks

- `GET /api/decks/`: Lista todos os decks públicos
- `GET /api/decks/my-decks/`: Lista decks do usuário
- `GET /api/decks/recommendations/`: Recomendações personalizadas
- `GET /api/decks/{id}/`: Detalhes de um deck
- `POST /api/decks/`: Cria um novo deck
- `PUT /api/decks/{id}/`: Atualiza um deck
- `DELETE /api/decks/{id}/`: Remove um deck
- `POST /api/decks/{id}/duplicate/`: Duplica um deck
- `POST /api/decks/{id}/archive/`: Arquiva um deck
- `POST /api/decks/{id}/unarchive/`: Desarquiva um deck
- `GET /api/decks/{id}/export/`: Exporta um deck (JSON/CSV)
- `POST /api/decks/import/`: Importa um deck (JSON/CSV)

### Flashcards

- `GET /api/cards/`: Lista todos os flashcards
- `GET /api/cards/my-flashcards/`: Lista flashcards do usuário
- `GET /api/cards/{id}/`: Detalhes de um flashcard
- `POST /api/cards/`: Cria um novo flashcard
- `PUT /api/cards/{id}/`: Atualiza um flashcard
- `DELETE /api/cards/{id}/`: Remove um flashcard
- `POST /api/cards/{id}/review/`: Registra uma revisão

### Favoritos

- `GET /api/favorites/`: Lista decks favoritos
- `POST /api/favorites/`: Adiciona um deck aos favoritos
- `DELETE /api/favorites/{id}/`: Remove um deck dos favoritos

## Cache

O sistema utiliza Redis para cache dos seguintes dados:

- Listagem de decks públicos
- Decks do usuário
- Recomendações
- Detalhes do deck
- Favoritos do usuário

## Desenvolvimento

### Comandos úteis

```bash
# Formata o código
make format

# Executa os linters
make lint

# Executa os testes
make test

# Gera relatório de cobertura
make coverage

# Limpa arquivos gerados
make clean
```

### Estrutura do Projeto

```
src/
├── apps/
│   ├── achievements/    # App de conquistas
│   ├── flashcards/     # App principal de flashcards
│   ├── progress/       # App de progresso
│   └── users/          # App de usuários
├── config/             # Configurações do projeto
└── manage.py
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes. 