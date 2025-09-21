.PHONY: tf-init tf-plan tf-apply tf-destroy tf-clean help tf-run-worker

# Cargar variables del archivo .env si existe
ifneq (,$(wildcard .env))
include .env
export $(shell sed 's/=.*//' .env)
endif

# Valores por defecto para las variables de entorno
AWS_DEFAULT_REGION ?= us-east-1
AWS_ACCESS_KEY_ID ?= test
AWS_SECRET_ACCESS_KEY ?= test
AWS_SQS_ENDPOINT_URL ?= http://localhost:4566
AWS_SNS_ENDPOINT_URL ?= http://localhost:4566

# Variables de Terraform con valores de .env
TF_VARS = -var="aws_region=$(AWS_DEFAULT_REGION)" \
          -var="aws_access_key=$(AWS_ACCESS_KEY_ID)" \
          -var="aws_secret_key=$(AWS_SECRET_ACCESS_KEY)" \
          -var="use_localstack=true" \
          -var="sqs_endpoint=$(AWS_SQS_ENDPOINT_URL)" \
          -var="sns_endpoint=$(AWS_SNS_ENDPOINT_URL)" \
          -var="environment=dev"

# Inicializar Terraform
tf-init:
	terraform init

# Plan de Terraform
tf-plan: tf-init
	terraform plan $(TF_VARS)

# Aplicar cambios de Terraform
tf-apply: tf-init
	terraform apply $(TF_VARS) -auto-approve

# Worker que ejecuta init, plan y apply secuencialmente
tf-run-worker: tf-init tf-plan tf-apply
	@echo "✅ Worker completado: init → plan → apply"

# Destruir recursos de Terraform
tf-destroy: tf-init
	terraform destroy $(TF_VARS) -auto-approve

# Limpiar archivos temporales
tf-clean:
	rm -rf .terraform* terraform.tfstate* terraform.tfvars

# Ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  make tf-init          - Inicializar Terraform"
	@echo "  make tf-plan          - Mostrar plan de Terraform"
	@echo "  make tf-apply         - Aplicar cambios"
	@echo "  make tf-run-worker    - Ejecutar init → plan → apply (worker completo)"
	@echo "  make tf-destroy       - Destruir recursos"
	@echo "  make tf-clean         - Limpiar archivos temporales"