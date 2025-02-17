.ONESHELL:

ENV_PREFIX=$(shell python3 -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")
@echo "ENV_PREFIX: $(ENV_PREFIX)"
#Variables

# Define the virtual environment name.
VENV_NAME := .venv

# Specify the python and the pip binaries.
PYTHON := $(ENV_PREFIX)python3
PIP := $(ENV_PREFIX)pip

# Directories
SRC_DIR := ./src
CTAGS_DIR := ./


# Declare the targets that will not produce the files.
.PHONY: help virtualenv show-venv install run tags source lint test debug

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Target for creating the virtual environment.
virtualenv: ## Create a virtual environment and install dependencies.
	@echo "Creating virtualenv ..."
	@rm -rf $(VENV_NAME)
	@$(PYTHON) -m venv $(VENV_NAME)
	@$(PIP) install -U pip
	@echo "Virtual environment created."
	@make install

# Target for installing dependencies from requirements-base.txt.
install: ## Install base dependencies into the virtual environment.
	@echo "$(ENV_PREFIX)"
	@echo "Installing dependencies ..."
	@$(PIP) install -r requirements.txt
	@echo "Dependencies installed."
	@echo "!!!Activate the virtual environment by running: source $(VENV_NAME)/bin/activate"

# Target for showing the virtual environment.
show-venv: ## Show the virtual environment.
	@echo "Virtual environment: $(VENV_NAME)"
	@echo "Running using $(PYTHON) ..."
	@echo "Python Version" && $(PYTHON) --version
	@$(PYTHON) -m site

# Target for running the application.
run: ## Run the application.
	@echo "Running the application using $(PYTHON)..."
	@$(PYTHON) $(SRC_DIR)/app.py $(ARGS)
	@echo "Application stopped."

# DEBUG_DOC_PATH := ./dataset/DISP-111415_FinalPaymentDetermination.pdf
# DEBUG_CSV_PATH := ./output/

# Allow passing ARGS from the command line or using default values
# ARGS ?= $(-- DEBUG_DOC_PATH) $(-- DEBUG_CSV_PATH)

# Debug target
debug: ## Debug the application using pudb.
	@echo "Debugging the application using $(PYTHON) ..."
	@$(PYTHON) -m pudb $(SRC_DIR)/app.py $(ARGS)
	@echo "Debugging stopped."

tags: ## Generate ctags.
	@echo "Generating ctags ..."
	@ctags -R --languages=python --python-kinds=-i  "$(SRC_DIR)"
	@echo "ctags generated."

# Target for creating the source files.
source: ## Create source files.
	@./scripts/bash/generate_source.sh

# Target for linting the code.
lint: ## Lint the code.
	@echo "Linting the code ..."
	@$(ENV_PREFIX)flake8 $(SRC_DIR)
	@find $(SRC_DIR) -name '*.py' -exec echo Linting {} \; -exec $(ENV_PREFIX)flake8 {} \;
	@echo "Code linted."

# Target for running the tests.
test: lint ## Lint the code and run the tests. 
	@echo "Running the tests ..."
	@$(ENV_PREFIX)pytest 
	@echo "Generating coverage report ..."
	@$(ENV_PREFIX)coverage html
	@echo "Tests run."

clean: ## Remove temporary files and log files.
	@echo "Cleaning temporary files..."
	@find . -type f \( -name '*.pyc' -o -name '*.bin' -o -name '*.tmp' -o -name '*.log' -o -name '.gitkeep' \) -exec rm -f {} +
	@echo "Cleaned."

