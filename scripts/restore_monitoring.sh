#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar argumentos
if [ "$#" -ne 2 ]; then
    echo -e "${RED}Erro: Forneça os arquivos de backup do Prometheus e Grafana${NC}"
    echo -e "Uso: $0 prometheus_backup.tar.gz grafana_backup.tar.gz"
    exit 1
fi

PROMETHEUS_BACKUP=$1
GRAFANA_BACKUP=$2

# Verificar se os arquivos existem
if [ ! -f "$PROMETHEUS_BACKUP" ]; then
    echo -e "${RED}Erro: Arquivo de backup do Prometheus não encontrado: $PROMETHEUS_BACKUP${NC}"
    exit 1
fi

if [ ! -f "$GRAFANA_BACKUP" ]; then
    echo -e "${RED}Erro: Arquivo de backup do Grafana não encontrado: $GRAFANA_BACKUP${NC}"
    exit 1
fi

echo -e "${YELLOW}Iniciando restauração dos dados de monitoramento...${NC}"

# Parar serviços
echo -e "${GREEN}Parando serviços de monitoramento...${NC}"
docker-compose -f docker/docker-compose.prod.yml stop prometheus grafana

# Restaurar dados do Prometheus
echo -e "${GREEN}Restaurando dados do Prometheus...${NC}"
docker run --rm \
    --volumes-from prometheus \
    -v $(pwd):/backup \
    alpine \
    sh -c "cd / && tar xzf /backup/$PROMETHEUS_BACKUP"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dados do Prometheus restaurados com sucesso${NC}"
else
    echo -e "${RED}Erro ao restaurar dados do Prometheus${NC}"
    exit 1
fi

# Restaurar dados do Grafana
echo -e "${GREEN}Restaurando dados do Grafana...${NC}"
docker run --rm \
    --volumes-from grafana \
    -v $(pwd):/backup \
    alpine \
    sh -c "cd / && tar xzf /backup/$GRAFANA_BACKUP"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dados do Grafana restaurados com sucesso${NC}"
else
    echo -e "${RED}Erro ao restaurar dados do Grafana${NC}"
    exit 1
fi

# Reiniciar serviços
echo -e "${GREEN}Reiniciando serviços de monitoramento...${NC}"
docker-compose -f docker/docker-compose.prod.yml start prometheus grafana

# Verificar status dos serviços
echo -e "${GREEN}Verificando status dos serviços...${NC}"
services=("prometheus" "grafana")

for service in "${services[@]}"; do
    if ! docker ps | grep -q "$service"; then
        echo -e "${RED}Erro: Serviço $service não está rodando${NC}"
        exit 1
    fi
done

echo -e "${GREEN}Restauração concluída com sucesso!${NC}"
echo -e "${YELLOW}Acesse o Grafana em: http://localhost:3000${NC}"
echo -e "${YELLOW}Acesse o Prometheus em: http://localhost:9090${NC}" 