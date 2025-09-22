# Usuarios de Tiendas - Flash Promos Marketplace

Este documento describe los usuarios de tiendas registrados en el sistema y cómo consultar las notificaciones enviadas por cada tienda.

## Usuarios y Tiendas Registradas

El sistema cuenta con los siguientes usuarios propietarios de tiendas:

### 1. TechShop Medellín Centro
- **Propietario**: owner_1 (owner1@techshop.com)
- **Username**: owner_1
- **Contraseña**: ownerpass123
- **Ubicación**: Carrera 50 # 53-45, Medellín
- **Coordenadas**: 6.2442, -75.5812
- **Productos**: 5 productos (Audífonos XYZ, Smartphone Alpha, Laptop Gamma, Tablet Beta, Smartwatch Delta)

### 2. TechShop Bogotá Norte
- **Propietario**: owner_2 (owner2@techshop.com)
- **Username**: owner_2
- **Contraseña**: ownerpass123
- **Ubicación**: Calle 85 # 12-45, Bogotá
- **Coordenadas**: 4.7109, -74.0721
- **Productos**: 3 productos (Audífonos ABC, Smartphone Omega, Laptop Sigma)

### 3. TechShop Cali Sur
- **Propietario**: owner_3 (owner3@techshop.com)
- **Username**: owner_3
- **Contraseña**: ownerpass123
- **Ubicación**: Avenida 6N # 24-35, Cali
- **Coordenadas**: 3.4516, -76.5320
- **Productos**: 3 productos (Audífonos Pro, Smartphone Ultra, Laptop Max)

## Consulta de Notificaciones

Para consultar las notificaciones enviadas por una tienda específica, utiliza el siguiente endpoint:

### Endpoint de Estadísticas de Notificaciones

```
GET {{base_url}}/api/notifications/store_stats/
```

**Autenticación requerida:** Bearer Token del propietario de la tienda

**Ejemplo de uso:**
```
GET https://tu-dominio.com/api/notifications/store_stats/
Authorization: Bearer <tu_access_token>
```

**Nota importante:** Este endpoint automáticamente obtiene las estadísticas de la tienda del usuario autenticado, por lo que no necesitas especificar el `store_id`.

### Respuesta del endpoint

Este endpoint te permitirá ver:
- ID y nombre de la tienda
- Período de consulta (fechas de inicio y fin)
- Total de notificaciones enviadas
- Notificaciones agrupadas por estado de entrega
- Número de usuarios únicos notificados
- Notificaciones por día
- Notificaciones por tipo