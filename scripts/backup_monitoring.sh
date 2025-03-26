#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Diretório de backup
BACKUP_DIR="backups/monitoring"
DATE=$(date +%Y%m%d_%H%M%S)

echo -e "${YELLOW}Iniciando backup dos dados de monitoramento...${NC}"

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Backup do Prometheus
echo -e "${GREEN}Fazendo backup dos dados do Prometheus...${NC}"
docker run --rm \
    --volumes-from prometheus \
    -v $(pwd)/$BACKUP_DIR:/backup \
    alpine \
    tar czf /backup/prometheus_$DATE.tar.gz /prometheus

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Backup do Prometheus concluído com sucesso${NC}"
else
    echo -e "${RED}Erro ao fazer backup do Prometheus${NC}"
    exit 1
fi

# Backup do Grafana
echo -e "${GREEN}Fazendo backup dos dados do Grafana...${NC}"
docker run --rm \
    --volumes-from grafana \
    -v $(pwd)/$BACKUP_DIR:/backup \
    alpine \
    tar czf /backup/grafana_$DATE.tar.gz /var/lib/grafana

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Backup do Grafana concluído com sucesso${NC}"
else
    echo -e "${RED}Erro ao fazer backup do Grafana${NC}"
    exit 1
fi

# Limpar backups antigos (manter últimos 7 dias)
echo -e "${GREEN}Limpando backups antigos...${NC}"
find "$BACKUP_DIR" -name "prometheus_*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "grafana_*.tar.gz" -mtime +7 -delete

echo -e "${GREEN}Backup concluído com sucesso!${NC}"
echo -e "${YELLOW}Arquivos de backup:${NC}"
echo -e "  - $BACKUP_DIR/prometheus_$DATE.tar.gz"
echo -e "  - $BACKUP_DIR/grafana_$DATE.tar.gz" 