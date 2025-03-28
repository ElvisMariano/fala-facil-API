# Deploy da API Fala Fácil no Railway

Este guia explica como fazer o deploy da API Fala Fácil no Railway.app.

## Pré-requisitos

- Conta no [Railway.app](https://railway.app/)
- Repositório Git com o código da API
- Conhecimento básico de linha de comando

## Passos para Deploy

### 1. Preparação do Projeto

O projeto já está configurado para deploy com os seguintes arquivos:

- `Procfile`: Define o comando para iniciar a aplicação
- `runtime.txt`: Especifica a versão do Python (3.11.7)
- `requirements.txt`: Lista as dependências do projeto
- `railway.toml`: Configurações específicas para o Railway

### 2. Criar um Novo Projeto no Railway

1. Faça login no [Railway.app](https://railway.app/)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Conecte sua conta GitHub e selecione o repositório da API Fala Fácil

### 3. Configurar Variáveis de Ambiente

No Railway, vá para a aba "Variables" e adicione as seguintes variáveis baseadas no arquivo `.env.example`:

```
DEBUG=False
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=.railway.app,seu-dominio-personalizado.com
CORS_ALLOWED_ORIGINS=https://seu-frontend.com

# Database (Railway fornece automaticamente)
# DATABASE_URL será configurado automaticamente pelo Railway

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com

# JWT
JWT_SECRET_KEY=sua-chave-jwt-secreta
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1440

# AWS S3 (se necessário)
AWS_ACCESS_KEY_ID=sua-access-key
AWS_SECRET_ACCESS_KEY=sua-secret-key
AWS_STORAGE_BUCKET_NAME=seu-bucket
AWS_S3_REGION_NAME=sua-regiao

# Segurança
DJANGO_SECURE_SSL_REDIRECT=True
```

### 4. Deploy

O Railway detectará automaticamente que é um projeto Python/Django e iniciará o deploy. O processo inclui:

1. Instalação das dependências do `requirements.txt`
2. Execução das migrações do banco de dados
3. Inicialização do servidor Gunicorn

### 5. Monitoramento

Após o deploy, você pode monitorar a aplicação através do painel do Railway:

- Logs: Verifique os logs da aplicação para identificar possíveis erros
- Métricas: Monitore o uso de CPU, memória e outros recursos
- Healthcheck: O Railway verificará automaticamente o endpoint `/api/health/` para garantir que a aplicação está funcionando corretamente

### 6. Domínio Personalizado (Opcional)

1. Na aba "Settings" do seu projeto no Railway
2. Vá para a seção "Domains"
3. Clique em "Generate Domain" para obter um domínio *.railway.app ou configure seu domínio personalizado

## Solução de Problemas

- **Erro de Banco de Dados**: Verifique se o Railway configurou corretamente a variável `DATABASE_URL`
- **Erro de Estáticos**: Certifique-se de que o `STATIC_ROOT` está configurado corretamente
- **Erro de Healthcheck**: Verifique se o endpoint `/api/health/` está respondendo corretamente

## Recursos Adicionais

- [Documentação do Railway](https://docs.railway.app/)
- [Documentação de Deploy do Django](https://docs.djangoproject.com/en/5.0/howto/deployment/)