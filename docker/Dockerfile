FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Adiciona poetry ao PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Configura diretório de trabalho
WORKDIR $PYSETUP_PATH

# Copia apenas os arquivos de dependências primeiro
COPY poetry.lock pyproject.toml ./

# Instala dependências do projeto
RUN poetry install --no-root --no-dev

# Copia o código do projeto
COPY . .

# Dá permissão de execução ao entrypoint
RUN chmod +x docker/entrypoint.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Porta que será exposta
EXPOSE 8000

# Define o entrypoint
ENTRYPOINT ["docker/entrypoint.sh"] 