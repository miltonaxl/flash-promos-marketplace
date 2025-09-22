# Flash Promos Marketplace

Plataforma de comercio electrónico especializada en promociones flash y ofertas por tiempo limitado.

## Configuración Rápida

### Prerrequisitos
- Docker y Docker Compose instalados
- Make instalado

### Instalación

1. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   ```
   Edita el archivo `.env` con tus configuraciones específicas si es necesario.

2. **Configuración completa del proyecto**
   ```bash
   make setup-complete
   ```
   Este comando ejecutará automáticamente:
   - Construcción de imágenes Docker
   - Inicio de todos los servicios
   - Aplicación de migraciones de base de datos
   - Configuración inicial de LocalStack (AWS local)

### Servicios Incluidos

- **Web**: Aplicación Django (puerto 8000)
- **PostgreSQL**: Base de datos con PostGIS (puerto 5432)
- **Redis**: Cache y message broker (puerto 6379)
- **Celery Worker**: Procesamiento de tareas asíncronas
- **Celery Beat**: Programador de tareas
- **LocalStack**: Emulación de servicios AWS (puerto 4566)

### Acceso a la Aplicación

Una vez completada la configuración:
- **API**: http://localhost:8000

### Comandos Útiles

```bash
# Ver logs de todos los servicios
make logs

# Acceder al shell de Django
make shell

# Ejecutar migraciones
make migrate

# Ejecutar tests
make test

# Detener todos los servicios
make down
```

### Documentación

Para información detallada, consulta la documentación en la carpeta `docs/`:
- [Configuración del Proyecto](docs/PROJECT.md)
- [Configuración de Docker](docs/DOCKER.md)
- [Configuración de Celery](docs/CELERY.md)
- [Variables de Entorno](docs/CONFIGURATION.md)
- [Estructura del Proyecto](docs/STRUCTURE.md)
- [Infraestructura Terraform](docs/TERRAFORM.md)

### Troubleshooting

Si encuentras problemas:
1. Verifica que Docker esté ejecutándose
2. Asegúrate de que los puertos no estén en uso
3. Revisa los logs con `make logs`
4. Consulta la documentación específica en `docs/`

---

*Para más información técnica y configuración avanzada, consulta la documentación completa en la carpeta `docs/`.*