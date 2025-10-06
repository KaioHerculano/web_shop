# ==============================================================================
# Makefile
# ==============================================================================
#
# Uso:
#   - `make help` para ver todos os comandos.
#   - As indentações DEVEM ser feitas com TABs.
#
# ------------------------------------------------------------------------------

# --- ⚙️ Configuração ---
PYTHON = python
MANAGE = $(PYTHON) manage.py
REQUIREMENTS = requirements.txt
# Defina um valor razoável para a cobertura mínima de testes (ex: 85, 90, 100)
MIN_COVERAGE = 100

# --- ℹ️ Ajuda ---
.PHONY: help
help:
	@echo "-----------------------------------------------------"
	@echo "Makefile para o projeto Web Shop"
	@echo "-----------------------------------------------------"
	@echo "\n  📦 Setup & Dependências:"
	@echo "    make install         - Instala as dependências de $(REQUIREMENTS)"
	@echo "    make safety          - Verifica as dependências em busca de vulnerabilidades"
	@echo "\n  💻 Desenvolvimento:"
	@echo "    make run             - Inicia o servidor de desenvolvimento"
	@echo "    make migrate         - Aplica as migrações do banco de dados"
	@echo "    make migrations      - Cria novos arquivos de migração para um app (ex: make migrations APP=brands)"
	@echo "    make shell           - Abre o shell do Django"
	@echo "    make loaddata        - Carrega uma fixture (ex: make loaddata FIXTURE=users)"
	@echo "\n  ✅ Qualidade & Testes:"
	@echo "    make format          - Formata o código com Black e isort"
	@echo "    make lint            - Roda o linter (Ruff) para encontrar erros e problemas de estilo"
	@echo "    make test            - Roda todos os testes do projeto"
	@echo "    make test-app        - Roda os testes de um app específico (ex: make test-app APP=brands)"
	@echo "    make test-coverage   - Roda os testes e gera um relatório de cobertura"
	@echo "    make pre-commit      - Roda os hooks de pre-commit em todos os arquivos"
	@echo "    make ci-check        - Roda todas as verificações de CI (lint, segurança, migrations, testes)"
	@echo "\n  🧹 Limpeza:"
	@echo "    make clean           - Remove arquivos temporários do Python"


# --- 📦 Setup & Dependências ---
.PHONY: install
install:
	pip install -r $(REQUIREMENTS)

.PHONY: safety
safety:
	@echo "🔎 Verificando dependências com Safety..."
	safety check -r $(REQUIREMENTS) --full-report


# --- 💻 Desenvolvimento ---
.PHONY: run
run:
	$(MANAGE) runserver

.PHONY: migrate
migrate:
	$(MANAGE) migrate

.PHONY: migrations
migrations:
	$(MANAGE) makemigrations $(APP)

.PHONY: shell
shell:
	$(MANAGE) shell_plus

.PHONY: loaddata
loaddata:
	@if [ -z "$(FIXTURE)" ]; then \
		echo "ERRO: Especifique a fixture. Ex: make loaddata FIXTURE=nome_do_arquivo"; \
		exit 1; \
	fi
	$(MANAGE) loaddata $(FIXTURE)


# --- ✅ Qualidade & Testes ---
.PHONY: format
format:
	@echo "💅 Formatando o código com Black e isort..."
	black .
	isort .

.PHONY: lint
lint:
	@echo "🧐 Verificando a qualidade do código com Ruff..."
	ruff check .

.PHONY: test
test:
	$(MANAGE) test -v 2

.PHONY: test-app
test-app:
	@if [ -z "$(APP)" ]; then \
		echo "ERRO: Especifique o app. Ex: make test-app APP=brands"; \
		exit 1; \
	fi
	$(MANAGE) test $(APP) -v 2

.PHONY: test-coverage
test-coverage:
	@echo "Rodando testes e gerando relatorio de cobertura (minimo: $(MIN_COVERAGE)%)"
	$(PYTHON) -m coverage run manage.py test -v 2
	$(PYTHON) -m coverage report -m --fail-under=$(MIN_COVERAGE)
	$(PYTHON) -m coverage html
	@echo "Relatório HTML completo disponível em htmlcov/index.html"

.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files

.PHONY: check-migrations
check-migrations:
	@echo "🔍 Verificando se faltam migrações..."
	$(MANAGE) makemigrations --check --no-input

.PHONY: ci-check
ci-check: safety lint check-migrations test-coverage


# --- 🧹 Limpeza ---
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
