.PHONY: help install update clean test lint format migrate run shell superuser docker-build docker-up docker-down monitoring-setup monitoring-start monitoring-stop monitoring-logs monitoring-status monitoring-backup monitoring-restore

help:
	@echo "Comandos disponíveis:"
	@echo "  install              - Instala as dependências do projeto"
	@echo "  update              - Atualiza as dependências do projeto"
	@echo "  clean               - Remove arquivos temporários"
	@echo "  test                - Executa os testes"
	@echo "  lint                - Executa verificações de linting"
	@echo "  format              - Formata o código"
	@echo "  migrate             - Aplica as migrações do banco de dados"
	@echo "  run                 - Inicia o servidor de desenvolvimento"
	@echo "  shell               - Abre o shell do Django"
	@echo "  superuser           - Cria um superusuário"
	@echo "  docker-build        - Constrói as imagens Docker"
	@echo "  docker-up           - Inicia os containers Docker"
	@echo "  docker-down         - Para os containers Docker"
	@echo "  monitoring-setup    - Configura o ambiente de monitoramento"
	@echo "  monitoring-start    - Inicia os serviços de monitoramento"
	@echo "  monitoring-stop     - Para os serviços de monitoramento"
	@echo "  monitoring-logs     - Exibe os logs dos serviços de monitoramento"
	@echo "  monitoring-status   - Exibe o status dos serviços de monitoramento"
	@echo "  monitoring-backup   - Faz backup dos dados de monitoramento"
	@echo "  monitoring-restore  - Restaura backup dos dados de monitoramento"

install:
	poetry install

update:
	poetry update

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

test:
	poetry run pytest

lint:
	poetry run flake8 src
	poetry run black --check src
	poetry run isort --check-only src

format:
	poetry run black src
	poetry run isort src

migrate:
	poetry run python src/manage.py migrate

run:
	poetry run python src/manage.py runserver

shell:
	poetry run python src/manage.py shell

superuser:
	poetry run python src/manage.py createsuperuser

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml up

docker-down:
	docker-compose -f docker/docker-compose.yml down

monitoring-setup:
	chmod +x scripts/setup_monitoring.sh
	./scripts/setup_monitoring.sh

monitoring-start:
	docker-compose -f docker/docker-compose.prod.yml up -d prometheus grafana alertmanager node-exporter cadvisor postgres-exporter redis-exporter

monitoring-stop:
	docker-compose -f docker/docker-compose.prod.yml stop prometheus grafana alertmanager node-exporter cadvisor postgres-exporter redis-exporter

monitoring-logs:
	docker-compose -f docker/docker-compose.prod.yml logs -f prometheus grafana alertmanager node-exporter cadvisor postgres-exporter redis-exporter

monitoring-status:
	docker-compose -f docker/docker-compose.prod.yml ps prometheus grafana alertmanager node-exporter cadvisor postgres-exporter redis-exporter

monitoring-backup:
	chmod +x scripts/backup_monitoring.sh
	./scripts/backup_monitoring.sh

monitoring-restore:
	@if [ -z "$(PROMETHEUS_BACKUP)" ] || [ -z "$(GRAFANA_BACKUP)" ]; then \
		echo "Erro: Forneça os arquivos de backup do Prometheus e Grafana"; \
		echo "Uso: make monitoring-restore PROMETHEUS_BACKUP=prometheus_backup.tar.gz GRAFANA_BACKUP=grafana_backup.tar.gz"; \
		exit 1; \
	fi
	chmod +x scripts/restore_monitoring.sh
	./scripts/restore_monitoring.sh $(PROMETHEUS_BACKUP) $(GRAFANA_BACKUP) 