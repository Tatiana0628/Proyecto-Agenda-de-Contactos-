# Agenda de Contactos

## Integrantes

- Diego Alejandro Cano Muñoz
- Andrés Felipe Colonia Ocampo
- Kenneth Ibarra Velasco
- Lizeth Tatiana Moreno Rosero

Aplicación web para registrar y administrar contactos. Permite crear, consultar,
editar y eliminar registros, buscarlos por nombre y filtrar la lista por
disponibilidad. Los datos se guardan en PostgreSQL.

## Contenido

- [Funciones](#funciones)
- [Tecnologías](#tecnologías)
- [Estructura](#estructura-del-proyecto)
- [Ejecución con Docker](#ejecución-con-docker)
- [Ejecución local](#ejecución-local-sin-docker)
- [Configuración](#configuración)
- [Uso y rutas](#uso-y-rutas)
- [API JSON](#api-json)
- [Validaciones](#validaciones)
- [Base de datos y persistencia](#base-de-datos-y-persistencia)
- [Pruebas](#pruebas)
- [Integración continua y publicación de imagen](#integración-continua-y-publicación-de-imagen)

## Funciones

- Crear, editar y eliminar contactos.
- Mostrar los contactos ordenados del más reciente al más antiguo.
- Buscar por coincidencia parcial en el nombre, sin distinguir mayúsculas y
  minúsculas.
- Filtrar por `Disponible` o `No disponible`, y combinar el filtro con la
  búsqueda por nombre.
- Validar los datos al salir de los campos del formulario y nuevamente en el
  servidor al guardar.
- Rechazar teléfonos y correos duplicados. Para comparar, se normaliza el
  teléfono quitando todo excepto los dígitos y se compara el correo sin
  distinguir mayúsculas ni espacios exteriores.
- Consultar y validar contactos mediante endpoints JSON.

## Tecnologías

- Python 3.11
- Flask 3.0.3
- PostgreSQL 16 y `psycopg2`
- Docker y Docker Compose
- pytest para pruebas unitarias y de integración
- GitHub Actions y GitHub Container Registry (GHCR)

## Estructura del proyecto

```text
.
├── app.py                       # Aplicación Flask, vistas y endpoints
├── db.py                        # Conexión, inicialización y consultas a PostgreSQL
├── validaciones.py              # Validación y normalización de datos
├── requirements.txt             # Dependencias de ejecución
├── requirements-dev.txt         # Dependencias de desarrollo y pruebas
├── pytest.ini                   # Configuración de pytest
├── Dockerfile                   # Imagen de la aplicación
├── docker-compose.yml           # Aplicación local y PostgreSQL
├── docker-compose.ghcr.yml      # Aplicación desde la imagen publicada en GHCR
├── .env.example                 # Ejemplo de variables de entorno
├── .github/workflows/ci-cd.yml  # Pruebas y publicación de la imagen
├── tests/
│   ├── conftest.py              # Preparación de la base de pruebas y cliente Flask
│   ├── test_unitarias.py        # Pruebas de validación y normalización
│   └── test_integracion.py      # Pruebas de rutas, persistencia y API
├── templates/
│   ├── base.html                # Estructura común de las páginas
│   ├── index.html               # Listado, búsqueda y filtros
│   └── form.html                # Formulario de alta y edición
└── static/
    └── style.css                # Estilos de la interfaz
```

## Ejecución con Docker

Requisitos: Docker Desktop (o Docker Engine) y Docker Compose v2.

1. Clona el repositorio y entra en su carpeta:

   ```bash
   git clone https://github.com/Tatiana0628/Proyecto-Agenda-de-Contactos-.git
   cd Proyecto-Agenda-de-Contactos-
   ```

2. Crea el archivo de configuración. Puedes conservar los valores de ejemplo
   para desarrollo local o modificarlos:

   ```bash
   cp .env.example .env
   ```

   En PowerShell, usa `Copy-Item .env.example .env`.

3. Construye la imagen y levanta la aplicación y PostgreSQL:

   ```bash
   docker compose up --build
   ```

4. Abre <http://localhost:8080>.

Para detener los contenedores sin borrar los datos:

```bash
docker compose down
```

Los datos están en el volumen `agenda_data`, que se conserva al ejecutar
`docker compose down`. Para borrar también la base de datos y todos sus datos:

```bash
docker compose down -v
```

> **Atención:** no uses `-v` si quieres conservar los contactos. Los valores
> predeterminados de `.env.example` son para desarrollo; configura credenciales
> seguras antes de exponer la aplicación fuera de un entorno local.

### Ejecutar la imagen publicada en GHCR

El archivo `docker-compose.ghcr.yml` usa
`ghcr.io/tatiana0628/agenda-contactos:latest` en lugar de construir la imagen
localmente. Si el paquete es accesible para tu cuenta:

```bash
docker compose -f docker-compose.ghcr.yml up -d
```

La aplicación queda disponible en <http://localhost:8080>. Esta configuración
usa el volumen independiente `agenda_data_ghcr`. Para detenerla:

```bash
docker compose -f docker-compose.ghcr.yml down
```

## Ejecución local sin Docker

Se necesita Python 3.11, PostgreSQL 16 y una base de datos accesible. Crea un
entorno virtual e instala las dependencias:

```bash
python -m venv .venv
```

Activa el entorno e instala el paquete:

```powershell
# Windows / PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Linux / macOS
source .venv/bin/activate
pip install -r requirements.txt
```

Configura las variables de conexión para que apunten a tu PostgreSQL local. Por
ejemplo, en PowerShell:

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "agenda"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
python app.py
```

En Linux o macOS:

```bash
DB_HOST=localhost DB_PORT=5432 DB_NAME=agenda DB_USER=postgres DB_PASSWORD=postgres python app.py
```

La aplicación crea la tabla al iniciar si no existe. En este modo se ejecuta
con el servidor de desarrollo de Flask; no está configurada como despliegue de
producción.

## Configuración

Docker Compose lee `.env` y pasa estas variables a la aplicación y a
PostgreSQL:

| Variable | Valor predeterminado | Descripción |
|---|---|---|
| `DB_HOST` | `db` en Compose | Host de PostgreSQL visto por la aplicación. En Compose es el nombre del servicio. |
| `DB_PORT` | `5432` | Puerto de PostgreSQL. |
| `DB_NAME` | `agenda` | Nombre de la base de datos. |
| `DB_USER` | `postgres` | Usuario de PostgreSQL. |
| `DB_PASSWORD` | `postgres` | Contraseña de PostgreSQL. |

`DB_HOST` y `DB_PORT` se fijan en `docker-compose.yml`; las otras tres
variables se pueden cambiar mediante `.env`. En ejecución directa con Python,
las variables de entorno del proceso se usan para la conexión. La aplicación
reintenta la conexión hasta diez veces, con una pausa de tres segundos entre
intentos.

## Uso y rutas

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Lista contactos; acepta filtros por query string. |
| `GET` | `/buscar` | Alias de la vista de listado y búsqueda. |
| `GET`, `POST` | `/add` | Muestra y procesa el formulario de creación. |
| `GET`, `POST` | `/edit/<id>` | Muestra y procesa la edición de un contacto. |
| `POST` | `/delete/<id>` | Elimina el contacto indicado. |

La búsqueda y el filtro se pueden combinar:

```text
/?nombre=ana&disponibilidad=Disponible
```

`nombre` busca coincidencias parciales; también se acepta `q` como alias.
`disponibilidad` acepta `Disponible` o `No disponible`. Los valores `todas` y
`todos` no aplican un filtro de disponibilidad.

## API JSON

Los endpoints de consulta devuelven un arreglo JSON con los campos
`id`, `nombre`, `telefono`, `email`, `notas` y `disponibilidad`.

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/contactos` | Lista contactos en JSON. |
| `GET` | `/api/buscar` | Busca y filtra contactos en JSON. |
| `POST` | `/api/validar-contacto` | Valida datos sin guardarlos. |

Los endpoints `GET` aceptan los mismos parámetros `nombre`/`q` y
`disponibilidad`. La vista `/` también responde con JSON si se solicita con
`?format=json` o con el encabezado `Accept: application/json`.

El endpoint de validación recibe un objeto JSON con `nombre`, `telefono`,
`email` y `notas`; al editar, se puede incluir `id` para excluir el propio
contacto de la comprobación de duplicados:

```json
{
  "id": 1,
  "nombre": "Ana Pérez",
  "telefono": "+57 300 123 4567",
  "email": "ana@correo.com",
  "notas": "Amiga"
}
```

Su respuesta tiene esta forma:

```json
{
  "valido": true,
  "errores": []
}
```

Si hay datos incorrectos, `valido` será `false` y `errores` contendrá los
mensajes. El endpoint de validación responde `200`; los formularios de alta y
edición responden `400` ante errores de formato y `409` si el teléfono o email
ya está asociado a otro contacto. La edición de un identificador inexistente
responde `404`.

## Validaciones

- El nombre es obligatorio y admite hasta 100 caracteres.
- El teléfono es opcional; acepta dígitos, espacios, paréntesis, guiones y un
  signo `+` inicial. Debe contener entre 7 y 15 dígitos.
- El email es opcional, debe tener formato válido y no superar 100 caracteres.
- Las notas son opcionales y admiten hasta 255 caracteres.
- La disponibilidad se elige entre `Disponible` y `No disponible`; si no se
  envía, se usa `Disponible`.
- La interfaz consulta `/api/validar-contacto` al salir de los campos de texto.
  El servidor vuelve a validar los datos al guardar; la validación del
  navegador no sustituye la del servidor.

## Base de datos y persistencia

La tabla `contactos` se inicializa automáticamente y contiene:

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | `SERIAL PRIMARY KEY` | Identificador autoincremental. |
| `nombre` | `VARCHAR(100) NOT NULL` | Nombre del contacto. |
| `telefono` | `VARCHAR(30)` | Teléfono opcional. |
| `email` | `VARCHAR(100)` | Email opcional. |
| `notas` | `VARCHAR(255)` | Notas opcionales. |
| `disponibilidad` | `VARCHAR(50)` | Estado; por defecto `Disponible`. |

Al iniciar, `db.py` crea la tabla si no existe y añade la columna
`disponibilidad` a instalaciones anteriores que aún no la tengan. También
actualiza los valores nulos de esa columna a `Disponible`.

En Docker, el volumen nombrado conserva los datos aunque se eliminen los
contenedores. La configuración de GHCR usa un volumen diferente para separar
sus datos de los de la ejecución local.

## Pruebas

Las pruebas unitarias no necesitan base de datos. Las de integración requieren
PostgreSQL en `localhost:5432` con la base `agenda_test`, usuario `postgres` y
contraseña `postgres`. La configuración de pruebas fija estas credenciales y
vacía la tabla antes de cada prueba; **no apuntes las pruebas a una base con
datos que quieras conservar**.

Una forma de crear la base de pruebas localmente con Docker es:

```bash
docker run --name agenda-db-test -e POSTGRES_DB=agenda_test -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
```

Instala las dependencias de desarrollo y ejecuta la suite:

```bash
pip install -r requirements-dev.txt
pytest -v
```

Al terminar, detén y elimina el contenedor de pruebas:

```bash
docker stop agenda-db-test
docker rm agenda-db-test
```

## Integración continua y publicación de imagen

El workflow [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) se
ejecuta en cada Pull Request hacia `main` y en cada push a `main`.

1. El job **Pruebas** configura Python 3.11 y PostgreSQL 16, instala
   `requirements-dev.txt` y ejecuta `pytest -v`.
2. Solo después de que las pruebas pasen, un push a `main` activa el job
   **Construir y publicar**, que crea la imagen y la publica en GHCR:
   `ghcr.io/tatiana0628/agenda-contactos`.
3. Se publican las etiquetas `latest` y `sha-<commit>`. Los Pull Requests
   ejecutan las pruebas, pero no publican la imagen.

## Equipo

- Diego Alejandro Cano Muñoz
- Andres Felipe Colonia Ocampo
- Kenneth Ibarra Velasco
- Lizeth Tatiana Moreno Rosero
