# Agenda de Contactos — Equipo 4

## Integrantes
- Diego Alejandro Cano Muñoz
- Andres felipe Colonia Ocampo
- Kenneth Ibarra Velasco
- lizeth Tatiana Moreno Rosero 

## Descripción
Aplicación web para gestionar contactos (agenda). Permite crear, consultar,
modificar y eliminar contactos, almacenando la información en una base de datos
PostgreSQL. Incluye funcionalidades avanzadas de **búsqueda por nombre** y
**filtro por disponibilidad** tanto en interfaz como vía endpoints/API.

## Tecnologías utilizadas
- Python / Flask
- PostgreSQL
- Docker y Docker Compose
- Git y GitHub

## Arquitectura
```
[ Navegador ] → http://localhost:8080
       │
       ▼
[ Contenedor "web" - Flask ]  ──►  red Docker "agenda_net"  ──►  [ Contenedor "db" - PostgreSQL ]
                                                                        │
                                                                        ▼
                                                              Volumen "agenda_data"
```

## Estructura del proyecto
```
agenda-app/
├── app.py                # Rutas, endpoints y lógica de la aplicación Flask
├── db.py                 # Conexión, creación y migración de tabla PostgreSQL
├── requirements.txt      # Dependencias de Python
├── Dockerfile             # Imagen de la aplicación
├── docker-compose.yml     # Orquestación de servicios web + db
├── .env.example            # Ejemplo de variables de entorno
├── static/
│   └── style.css          # Estilos modernos y responsivos
├── templates/
│   ├── base.html          # Plantilla base con diseño y Google Fonts
│   ├── index.html         # Listado, barra de búsqueda y filtros
│   └── form.html          # Formulario crear/editar con disponibilidad
└── README.md
```

## Configuración (variables de entorno)
Definidas en `docker-compose.yml` y tomadas del archivo `.env`:

| Variable      | Función                                   |
|---------------|--------------------------------------------|
| DB_HOST       | Nombre del servicio de base de datos (`db`) |
| DB_NAME       | Nombre de la base de datos                 |
| DB_USER       | Usuario de PostgreSQL                      |
| DB_PASSWORD   | Contraseña del usuario de PostgreSQL       |
| DB_PORT       | Puerto de PostgreSQL (5432)                |

## ¿Cómo ejecutar el proyecto?
1. Clonar el repositorio:
   ```bash
   git clone <URL-del-repositorio>
   cd agenda-app
   ```
2. Crear el archivo `.env` a partir del ejemplo:
   ```bash
   cp .env.example .env
   ```
3. Construir y levantar los contenedores:
   ```bash
   docker compose up --build
   ```
4. Abrir el navegador en:
   ```
   http://localhost:8080
   ```
5. Para detener los servicios:
   ```bash
   docker compose down
   ```
6. Para comprobar la persistencia de los datos:
   ```bash
   docker compose down
   docker compose up
   ```
   Los contactos creados previamente deben seguir apareciendo.

## Git y trabajo colaborativo
El equipo trabajó con una branch por integrante, cada una enfocada en una parte del
proyecto, y se integraron los cambios a `main` mediante Pull Requests revisados por
el equipo:

- `feature-aplicacion` — lógica Flask y rutas CRUD
- `feature-docker` — Dockerfile de la aplicación
- `feature-base-datos` — modelo de datos y conexión a PostgreSQL
- `feature-compose` — docker-compose.yml, red, volumen y variables de entorno

(Agregar aquí los enlaces a los Pull Requests una vez creados en GitHub.)

## Persistencia
PostgreSQL almacena sus datos en el volumen Docker `agenda_data`, por lo que la
información se conserva aunque se detengan y reinicien los contenedores
(`docker compose down` seguido de `docker compose up`).

## Funcionalidad 1 — Búsqueda por Nombre y Filtro de Disponibilidad (Integrante 1)
- **Base de Datos**: Se agrega automáticamente la columna `disponibilidad VARCHAR(50) DEFAULT 'Disponible'` a la tabla `contactos` si no existe previamente mediante `ALTER TABLE contactos ADD COLUMN IF NOT EXISTS disponibilidad ...`.
- **Lógica y Formulario**: Los contactos pueden registrarse y editarse con estado `Disponible` o `No disponible`.
- **Búsqueda y Filtro (Interfaz)**:
  - Formulario en la vista principal para filtrar en tiempo real por coincidencia parcial en nombre (`ILIKE %nombre%`).
  - Selector desplegable para filtrar por disponibilidad (`Todas`, `Disponible`, `No disponible`).
  - Badges visuales con colores (verde para Disponible, rojo/ámbar para No disponible).
  - Contador de resultados y opción para limpiar/restablecer filtros.
- **Endpoints**:
  - `GET /?nombre=<valor>&disponibilidad=<valor>` (interfaz web filtrada).
  - `GET /buscar?nombre=<valor>&disponibilidad=<valor>` (endpoint directo compatible).
  - `GET /api/buscar?nombre=<valor>&disponibilidad=<valor>` o `GET /api/contactos` (endpoint REST que responde en formato JSON).
