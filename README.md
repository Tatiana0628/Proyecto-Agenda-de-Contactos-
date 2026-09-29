# Agenda de Contactos — Equipo 4

## Integrantes
- Nombre completo integrante 1
- Nombre completo integrante 2
- Nombre completo integrante 3
- Nombre completo integrante 4

## Descripción
Aplicación web sencilla para gestionar contactos (agenda). Permite crear, consultar,
modificar y eliminar contactos, almacenando la información en una base de datos
PostgreSQL.

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
├── app.py                # Rutas y lógica de la aplicación Flask
├── requirements.txt      # Dependencias de Python
├── Dockerfile             # Imagen de la aplicación
├── docker-compose.yml     # Orquestación de servicios web + db
├── .env.example            # Ejemplo de variables de entorno
├── templates/
│   ├── base.html
│   ├── index.html         # Listado de contactos
│   └── form.html          # Formulario crear/editar
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
