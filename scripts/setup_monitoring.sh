#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando setup do ambiente de monitoramento...${NC}"

# Criar diretórios necessários
echo -e "${GREEN}Criando diretórios...${NC}"
mkdir -p docker/prometheus/rules
mkdir -p docker/grafana/provisioning/dashboards
mkdir -p docker/alertmanager

# Verificar se os arquivos de configuração existem
echo -e "${GREEN}Verificando arquivos de configuração...${NC}"

files=(
    "docker/prometheus/prometheus.yml"
    "docker/prometheus/rules/alerts.yml"
    "docker/grafana/provisioning/datasources/datasource.yml"
    "docker/grafana/provisioning/dashboards/dashboard.yml"
    "docker/grafana/provisioning/dashboards/fala-facil-dashboard.json"
    "docker/alertmanager/alertmanager.yml"
)

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}Erro: Arquivo $file não encontrado${NC}"
        exit 1
    fi
done

# Verificar variáveis de ambiente
echo -e "${GREEN}Verificando variáveis de ambiente...${NC}"
required_vars=(
    "GRAFANA_ADMIN_USER"
    "GRAFANA_ADMIN_PASSWORD"
    "SLACK_WEBHOOK_URL"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}Erro: Variável de ambiente $var não definida${NC}"
        exit 1
    fi
done

# Criar volumes Docker se não existirem
echo -e "${GREEN}Criando volumes Docker...${NC}"
volumes=(
    "prometheus_data"
    "grafana_data"
)

for volume in "${volumes[@]}"; do
    if ! docker volume inspect "$volume" >/dev/null 2>&1; then
        docker volume create "$volume"
    fi
done

# Iniciar serviços de monitoramento
echo -e "${GREEN}Iniciando serviços de monitoramento...${NC}"
docker-compose -f docker/docker-compose.prod.yml up -d prometheus grafana alertmanager node-exporter cadvisor postgres-exporter redis-exporter

# Verificar status dos serviços
echo -e "${GREEN}Verificando status dos serviços...${NC}"
services=(
    "prometheus"
    "grafana"
    "alertmanager"
    "node-exporter"
    "cadvisor"
    "postgres-exporter"
    "redis-exporter"
)

for service in "${services[@]}"; do
    if ! docker ps | grep -q "$service"; then
        echo -e "${RED}Erro: Serviço $service não está rodando${NC}"
        exit 1
    fi
done

echo -e "${GREEN}Setup do ambiente de monitoramento concluído com sucesso!${NC}"
echo -e "${YELLOW}Acesse o Grafana em: http://localhost:3000${NC}"
echo -e "${YELLOW}Acesse o Prometheus em: http://localhost:9090${NC}"
echo -e "${YELLOW}Acesse o AlertManager em: http://localhost:9093${NC}" 