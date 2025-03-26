# Prompt para Criação da API Fala Fácil Learn em Django

## Objetivo
Criar uma API RESTful usando Django e Django REST Framework que replique todas as funcionalidades da API Fala Fácil Learn original, mantendo a mesma estrutura de dados e endpoints, mas aproveitando os recursos e boas práticas do ecossistema Django.

## Tecnologias Principais
- Django 5.0+
- Django REST Framework
- PostgreSQL
- JWT para autenticação
- Poetry para gerenciamento de dependências
- Docker e Docker Compose para desenvolvimento e produção
- Pytest para testes
- Black e isort para formatação de código
- Flake8 para linting
- Swagger/OpenAPI para documentação

## Estrutura do Projeto

```
fala_facil_api/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
├── docs/
│   └── api.md
├── src/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── utils.py
│   ├── apps/
│   │   ├── users/
│   │   ├── flashcards/
│   │   ├── progress/
│   │   └── achievements/
│   └── manage.py
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

## Modelos de Dados

### User (Estendendo AbstractUser)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='A1')
    xp = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    timezone = models.CharField(max_length=50, default='UTC')
    last_activity_at = models.DateTimeField(null=True)
```

### Flashcard
```python
class Flashcard(models.Model):
    front = models.TextField()
    back = models.TextField()
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    category = models.CharField(max_length=100)
    tags = ArrayField(models.CharField(max_length=50))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['category'])
        ]
```

### FlashcardProgress
```python
class FlashcardProgress(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    flashcard = models.ForeignKey('Flashcard', on_delete=models.CASCADE)
    correct_attempts = models.IntegerField(default=0)
    incorrect_attempts = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0)
    last_reviewed = models.DateTimeField(null=True)
    next_review_date = models.DateTimeField(null=True)
    ease_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'flashcard']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['flashcard']),
            models.Index(fields=['next_review_date'])
        ]
```

### UserProgress
```python
class UserProgress(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    current_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='A1')
    total_cards = models.IntegerField(default=0)
    mastered_cards = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    accuracy_rate = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    cards_per_day = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)
    last_study_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Achievement
```python
class Achievement(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['type'])
        ]
```

## Endpoints da API

### Autenticação
- POST `/api/auth/register/`
- POST `/api/auth/login/`
- POST `/api/auth/refresh/`

### Usuários
- GET `/api/users/me/profile/`
- PATCH `/api/users/me/profile/`
- GET `/api/users/me/progress/`
- GET `/api/users/me/achievements/`
- GET `/api/users/me/achievements/stats/`

### Flashcards
- GET `/api/flashcards/`
- POST `/api/flashcards/`
- GET `/api/flashcards/{id}/`
- PUT `/api/flashcards/{id}/`
- DELETE `/api/flashcards/{id}/`
- GET `/api/flashcards/progress/`
- POST `/api/flashcards/{id}/review/`

### Progresso
- GET `/api/progress/`
- GET `/api/progress/{lesson_id}/`
- PUT `/api/progress/{lesson_id}/`

### Conquistas
- GET `/api/achievements/`
- POST `/api/achievements/`
- GET `/api/achievements/{id}/`

## Funcionalidades Específicas

### Sistema de Autenticação
- Implementar autenticação JWT com refresh tokens
- Middleware de autenticação personalizado
- Decoradores para permissões específicas

### Sistema de Revisão Espaçada
- Implementar algoritmo SuperMemo 2 para revisão espaçada
- Calcular próximas datas de revisão
- Atualizar fatores de facilidade

### Sistema de Conquistas
- Sistema de eventos para desbloquear conquistas
- Cálculo automático de progresso
- Notificações de novas conquistas

### Sistema de Progresso
- Cálculo automático de estatísticas
- Atualização de níveis baseada em performance
- Tracking de streak diário

## Requisitos Técnicos

### Segurança
- Implementar rate limiting
- Validação de dados com Django REST Framework
- Sanitização de inputs
- Proteção contra CSRF, XSS e SQL Injection
- Configuração de CORS

### Performance
- Implementar caching com Redis
- Otimização de queries com select_related e prefetch_related
- Paginação para listagens
- Compressão de respostas

### Monitoramento
- Logging estruturado
- Integração com Sentry para tracking de erros
- Métricas de performance
- Health checks

### Testes
- Testes unitários para models
- Testes de integração para views
- Testes de performance
- Fixtures para dados de teste

## Configurações de Ambiente

### Variáveis de Ambiente
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/falafacil_db
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000
JWT_SECRET_KEY=1656589655446654424998654652481000813099
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Configuração do Docker
```dockerfile
FROM python:3.11-slim

# ... configurações do Dockerfile ...
```

### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
  db:
    image: postgres:15
  redis:
    image: redis:7
```

## Instruções de Desenvolvimento

1. Clone o repositório
2. Configure o ambiente virtual com Poetry
3. Copie .env.example para .env e configure
4. Execute as migrações
5. Rode os testes
6. Inicie o servidor de desenvolvimento

## Padrões de Código

- Seguir PEP 8
- Documentar usando docstrings
- Tipagem estática com mypy
- Commits semânticos
- Code review obrigatório

## Documentação

- Swagger/OpenAPI para endpoints
- README detalhado
- Documentação de arquitetura
- Guias de contribuição
- Changelog

## Deploy

- Configuração para deploy no Heroku
- Scripts de CI/CD
- Checklist de segurança
- Backup automático

## Monitoramento e Logs

- Configuração do Sentry
- Logs estruturados
- Métricas de performance
- Alertas automáticos

## Considerações de Segurança

- Autenticação JWT
- Rate limiting
- Validação de dados
- Sanitização de inputs
- Headers de segurança
- CORS configurado
- Proteção contra ataques comuns

## Melhorias Futuras

1. Implementar GraphQL
2. Adicionar WebSockets para real-time
3. Implementar cache distribuído
4. Adicionar suporte a múltiplos idiomas
5. Implementar sistema de gamificação avançado
6. Adicionar análise de dados e dashboards
7. Implementar machine learning para personalização
8. Adicionar suporte a vídeos e áudios
9. Implementar sistema de recomendação
10. Adicionar integração com apps de terceiros

## Requisitos de Qualidade

- Cobertura de testes > 90%
- Tempo de resposta < 200ms
- Disponibilidade > 99.9%
- Zero vulnerabilidades críticas
- Documentação atualizada
