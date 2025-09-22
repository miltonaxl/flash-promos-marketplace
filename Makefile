.PHONY: setup-complete setup-with-data install-system-deps localstack-only terraform-setup db-services install-python-deps web-service migrate seed localstack-status clean-all git-push git-push-force test logs help

# Default target that runs everything
all: setup-complete

# Install system dependencies
install-system-deps:
	@echo "🔧 Verificando e instalando dependencias del sistema..."
	@OS=$$(uname -s); \
	echo "🖥️  Sistema operativo detectado: $$OS"; \
	if ! command -v docker >/dev/null 2>&1; then \
		echo "📦 Docker no encontrado. Instalando..."; \
		case "$$OS" in \
			Darwin) \
				if command -v brew >/dev/null 2>&1; then \
					brew install --cask docker; \
				else \
					echo "❌ Homebrew no encontrado. Por favor instala Docker Desktop manualmente desde https://docker.com/products/docker-desktop"; \
					exit 1; \
				fi ;; \
			Linux) \
				if command -v apt-get >/dev/null 2>&1; then \
					sudo apt-get update && sudo apt-get install -y docker.io docker-compose; \
					sudo systemctl enable docker; \
				elif command -v yum >/dev/null 2>&1; then \
					sudo yum install -y docker docker-compose; \
					sudo systemctl enable docker; \
				elif command -v pacman >/dev/null 2>&1; then \
					sudo pacman -S docker docker-compose; \
					sudo systemctl enable docker; \
				else \
					echo "❌ Gestor de paquetes no soportado. Por favor instala Docker manualmente"; \
					exit 1; \
				fi ;; \
			*) \
				echo "❌ Sistema operativo no soportado: $$OS"; \
				exit 1 ;; \
		esac; \
	else \
		echo "✅ Docker ya está instalado"; \
	fi
	@OS=$$(uname -s); \
	if ! docker info >/dev/null 2>&1; then \
		echo "🚀 Iniciando Docker..."; \
		case "$$OS" in \
			Darwin) \
				open -a Docker; \
				echo "⏳ Esperando a que Docker se inicie en macOS (90 segundos máximo)..."; ;; \
			Linux) \
				sudo systemctl start docker; \
				echo "⏳ Esperando a que Docker se inicie en Linux (60 segundos máximo)..."; ;; \
		esac; \
		max_wait=90; \
		if [ "$$OS" = "Linux" ]; then max_wait=60; fi; \
		for i in $$(seq $$max_wait -1 1); do \
			if docker info >/dev/null 2>&1; then \
				echo "✅ Docker daemon está ejecutándose"; \
				break; \
			fi; \
			echo "⏳ Esperando... $$i segundos restantes"; \
			sleep 1; \
		done; \
		if ! docker info >/dev/null 2>&1; then \
			echo "❌ Error: Docker daemon no se pudo iniciar después de $$max_wait segundos"; \
			case "$$OS" in \
				Darwin) \
					echo "💡 Por favor, inicia Docker Desktop manualmente y vuelve a ejecutar este comando"; ;; \
				Linux) \
					echo "💡 Por favor, verifica el estado del servicio Docker: sudo systemctl status docker"; ;; \
			esac; \
			exit 1; \
		fi; \
	else \
		echo "✅ Docker daemon ya está ejecutándose"; \
	fi
	@OS=$$(uname -s); \
	if [ "$$OS" = "Darwin" ]; then \
		echo "✅ Docker Compose viene incluido con Docker Desktop en macOS"; \
	else \
		if ! command -v docker-compose >/dev/null 2>&1; then \
			echo "❌ Docker Compose no encontrado en Linux"; \
			exit 1; \
		else \
			echo "✅ Docker Compose está disponible"; \
		fi; \
	fi
	@if ! command -v terraform >/dev/null 2>&1; then \
		echo "📦 Instalando Terraform..."; \
		OS=$$(uname -s); \
		case "$$OS" in \
			Darwin) \
				if command -v brew >/dev/null 2>&1; then \
					brew install terraform; \
				else \
					echo "❌ Homebrew no encontrado. Por favor instala Terraform manualmente"; \
					exit 1; \
				fi ;; \
			Linux) \
				if command -v apt-get >/dev/null 2>&1; then \
					wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg; \
					echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list; \
					sudo apt-get update && sudo apt-get install -y terraform; \
				elif command -v yum >/dev/null 2>&1; then \
					sudo yum install -y yum-utils; \
					sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo; \
					sudo yum install -y terraform; \
				else \
					echo "❌ Gestor de paquetes no soportado para Terraform. Por favor instala manualmente"; \
					exit 1; \
				fi ;; \
		esac; \
	else \
		echo "✅ Terraform ya está instalado"; \
	fi
	@echo "🎉 Todas las dependencias del sistema han sido instaladas y verificadas"

# Install Python dependencies
install-python-deps:
	@echo "🐍 Verificando e instalando dependencias de Python..."
	@if [ ! -f requirements.txt ]; then \
		echo "❌ Archivo requirements.txt no encontrado"; \
		exit 1; \
	fi
	@echo "🔧 Creando entorno virtual de Python..."
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
		echo "✅ Entorno virtual creado en ./venv"; \
	else \
		echo "✅ Entorno virtual ya existe"; \
	fi
	@echo "📦 Instalando dependencias en el entorno virtual..."
	@. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "🐳 Construyendo imagen Docker con dependencias de Python..."
	@docker build -t flash-promos-marketplace .
	@echo "✅ Dependencias de Python instaladas en entorno virtual y contenedor"

# Complete setup following the new sequential flow
setup-complete: install-system-deps localstack-only terraform-setup db-services install-python-deps web-service migrate seed
	@echo "🎉 Proyecto completamente configurado con datos:"
	@echo "   1. ✅ Dependencias del sistema instaladas"
	@echo "   2. ✅ LocalStack ejecutándose"
	@echo "   3. ✅ Infraestructura Terraform configurada"
	@echo "   4. ✅ Servicios de base de datos iniciados"
	@echo "   5. ✅ Dependencias del proyecto instaladas"
	@echo "   6. ✅ Servicio web ejecutándose"
	@echo "   7. ✅ Migraciones aplicadas"
	@echo "   8. ✅ Datos de prueba cargados"
	@echo "🌐 Aplicación disponible en: http://localhost:8000"



# LocalStack operations
localstack-only:
	@echo "☁️ Iniciando solo LocalStack..."
	docker-compose up -d localstack
	@echo "⏳ Esperando a que LocalStack esté listo..."
	@for i in $$(seq 30 -1 1); do \
		if curl -s http://localhost:4566/_localstack/health >/dev/null 2>&1; then \
			echo "✅ LocalStack está listo"; \
			break; \
		fi; \
		echo "⏳ Esperando LocalStack... ($$i segundos restantes)"; \
		sleep 1; \
	done
	@if ! curl -s http://localhost:4566/_localstack/health >/dev/null 2>&1; then \
		echo "❌ LocalStack no pudo iniciarse correctamente"; \
		echo "💡 Verifica los logs con: docker-compose logs localstack"; \
		exit 1; \
	fi



localstack-status:
	@echo "☁️ Verificando estado de LocalStack..."
	@if curl -s http://localhost:4566/_localstack/health >/dev/null 2>&1; then \
		echo "✅ LocalStack está ejecutándose"; \
		curl -s http://localhost:4566/_localstack/health | python3 -m json.tool 2>/dev/null || echo "Servicio activo"; \
	else \
		echo "❌ LocalStack no está ejecutándose"; \
		echo "💡 Ejecuta 'make localstack-up' para iniciarlo"; \
	fi

# Start only database services (postgres, redis)
db-services:
	@echo "🗄️ Iniciando solo servicios de base de datos..."
	docker-compose up -d postgres redis
	@echo "⏳ Esperando a que los servicios estén listos..."
	@sleep 5
	@echo "✅ Servicios de base de datos (postgres, redis) iniciados"



# Start web service
web-service:
	@echo "🌐 Iniciando solo el servicio web..."
	docker-compose up -d web
	@echo "⏳ Esperando a que el servicio web esté listo..."
	@sleep 3
	@echo "✅ Servicio web iniciado en http://localhost:8000"



# Terraform operations
terraform-setup: localstack-only
	@echo "🏗️ Configurando infraestructura completa con Terraform..."
	@cd terraform && terraform init
	@echo "📋 Generando plan de Terraform..."
	@cd terraform && terraform plan
	@echo "🚀 Aplicando configuración de Terraform..."
	@cd terraform && terraform apply -auto-approve
	@echo "✅ Infraestructura LocalStack configurada completamente"



# Run database migrations
migrate:
	@echo "🔄 Ejecutando migraciones de base de datos..."
	docker-compose exec web python manage.py migrate
	@echo "✅ Migraciones completadas"

# Run database seeders
seed:
	@echo "🌱 Ejecutando seeders de base de datos..."
	docker-compose exec web python manage.py seed_all
	@echo "✅ Seeders completados"

# Full clean: containers + virtual environment
clean-all:
	@echo "🧹 Limpiando recursos Docker..."
	docker-compose down -v
	docker system prune -f
	@echo "🧹 Limpiando entorno virtual de Python..."
	@if [ -d "venv" ]; then \
		rm -rf venv; \
		echo "✅ Entorno virtual eliminado"; \
	else \
		echo "ℹ️ No hay entorno virtual que limpiar"; \
	fi
	@echo "🎉 Limpieza completa finalizada"

# Git operations with SSH key
git-push:
	@echo "🔑 Haciendo push a GitHub con llave SSH..."
	@if [ ! -f "id_key" ]; then \
		echo "❌ Archivo de llave SSH 'id_key' no encontrado"; \
		echo "💡 Asegúrate de que el archivo 'id_key' esté en la raíz del proyecto"; \
		exit 1; \
	fi
	@chmod 600 id_key
	@echo "📤 Ejecutando git push con llave SSH..."
	@GIT_SSH_COMMAND="ssh -i ./id_key -o StrictHostKeyChecking=no" git push
	@echo "✅ Push completado exitosamente"

git-push-force:
	@echo "🔑 Haciendo push forzado a GitHub con llave SSH..."
	@if [ ! -f "id_key" ]; then \
		echo "❌ Archivo de llave SSH 'id_key' no encontrado"; \
		echo "💡 Asegúrate de que el archivo 'id_key' esté en la raíz del proyecto"; \
		exit 1; \
	fi
	@chmod 600 id_key
	@echo "⚠️  ADVERTENCIA: Esto sobrescribirá el historial remoto"
	@echo "📤 Ejecutando git push --force con llave SSH..."
	@GIT_SSH_COMMAND="ssh -i ./id_key -o StrictHostKeyChecking=no" git push --force
	@echo "✅ Push forzado completado exitosamente"

# Run tests
test:
	@echo "🧪 Ejecutando tests del proyecto..."
	@if ! docker-compose ps | grep -q "web.*Up"; then \
		echo "❌ El contenedor web no está ejecutándose"; \
		echo "💡 Ejecuta 'make web-service' primero"; \
		exit 1; \
	fi
	@echo "📋 Ejecutando todos los tests..."
	@docker-compose exec web python manage.py test --verbosity=2
	@echo "✅ Tests completados"

# Run tests without LocalStack (optimized for CI/CD)
test-only:
	@echo "🧪 Ejecutando tests optimizados (solo PostgreSQL)..."
	@echo "🔧 Levantando PostgreSQL..."
	@docker-compose up -d postgres
	@echo "⏳ Esperando a que PostgreSQL esté listo..."
	@sleep 5
	@echo "🚀 Levantando contenedor web..."
	@docker-compose up -d web
	@echo "⏳ Esperando a que el contenedor web esté listo..."
	@sleep 3
	@echo "🛑 Deteniendo servicios innecesarios..."
	@docker-compose stop redis localstack 2>/dev/null || true
	@echo "📋 Ejecutando tests con configuración de test..."
	@docker-compose exec web python manage.py test --settings=marketplace.settings_test --verbosity=2
	@echo "✅ Tests optimizados completados"

# Show web service logs
logs:
	@echo "📋 Mostrando logs del servicio web..."
	@if ! docker-compose ps | grep -q "web.*Up"; then \
		echo "❌ El contenedor web no está ejecutándose"; \
		echo "💡 Ejecuta 'make web-service' primero"; \
		exit 1; \
	fi
	@echo "📄 Logs en tiempo real (Ctrl+C para salir):"
	@docker-compose logs -f web

# Show help
help:
	@echo "📋 Comandos disponibles:"
	@echo ""
	@echo "🚀 Comandos principales:"
	@echo "  make setup-complete  - Flujo completo: sistema → localstack → terraform → db → proyecto → web"
	@echo "  make setup-with-data - Flujo completo + migraciones + datos de prueba"
	@echo ""
	@echo "🔧 Comandos por pasos:"
	@echo "  make install-system-deps - Instalar dependencias del sistema"
	@echo "  make localstack-only     - Iniciar solo LocalStack"
	@echo "  make terraform-setup     - Configurar infraestructura con Terraform"
	@echo "  make db-services         - Levantar servicios de BD (postgres, redis)"
	@echo "  make install-python-deps - Instalar dependencias de Python"
	@echo "  make web-service         - Levantar servicio web"
	@echo "  make migrate             - Ejecutar migraciones de base de datos"
	@echo "  make seed                - Cargar datos de prueba"
	@echo ""
	@echo "🧪 Testing y Desarrollo:"
	@echo "  make test               - Ejecutar todos los tests del proyecto"
	@echo "  make logs               - Ver logs del servicio web en tiempo real"
	@echo ""
	@echo "🔐 Comandos Git:"
	@echo "  make git-push       - Push a GitHub usando llave SSH (id_key)"
	@echo "  make git-push-force - Push forzado a GitHub usando llave SSH (id_key)"
	@echo ""
	@echo "🛠️ Utilidades:"
	@echo "  make localstack-status - Verificar estado de LocalStack"
	@echo "  make clean-all         - Limpieza completa"
	@echo "  make help              - Mostrar esta ayuda"


