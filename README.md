# SIGEAH-1.0 — Sistema Integrado de Gestión de Emergencias y Atención Humanitaria

# Integrantes:

Jeremias Aguirre,
Amado Carrasco,
Aritzys Morales.

## 1. Problema, usuarios y alcance

**Problema:** la información de las emergencias suele llevarse en papel o
mensajes sueltos, lo que dificulta consultarla y saber en qué estado está
cada atención.

**Personas usuarias:** Seria el personal de coordinación de emergencias
de una comunidad u organización humanitaria o personal de los bomberos, Sinaproc o entidades similares.

**Qué hace:** registrar, consultar, filtrar y actualizar el estado de
emergencias, guardándolas de forma persistente.

**Limitaciones:**

- Aplicación local de un solo usuario (sin red ni cuentas).
- No elimina emergencias ni genera resúmenes o gráficas.
- Los datos se guardan en un archivo SQLite local.

## 2. Stack tecnológico

| Componente          | Tecnología                          |
| ------------------- | ----------------------------------- |
| Lenguaje            | Python 3.10 o superior              |
| Base de datos       | SQLite (módulo `sqlite3` de Python) |
| Interfaz de consola | `rich`                              |
| Interfaz gráfica    | `customtkinter`                     |
| Pruebas             | `pytest`                            |
| Estilo              | `ruff`                              |
| Automatización      | GitHub Actions                      |

## 3. Instalación

```bash
git clone https://github.com/amadoCT/SIGEAH-1.0.git
cd SIGEAH-1.0
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

## 4. Configuración

Copie `.env.example` a `.env` y ajuste los valores si lo necesita:

| Variable         | Para qué sirve                    | Valor por defecto |
| ---------------- | --------------------------------- | ----------------- |
| `SIGEAH_DB_PATH` | Ruta del archivo de base de datos | `data/sigeah.db`  |

El archivo `.env` está en `.gitignore` y nunca se sube al repositorio.
El proyecto no usa credenciales ni servicios externos.

**Secretos de GitHub Actions:** si se activa el escaneo con Snyk, una persona
autorizada debe registrar `SNYK_TOKEN` en _Settings → Secrets and variables →
Actions_. No se publican valores reales.

## 5. Ejecución

```bash
python -m app.gui     # interfaz gráfica
python main.py        # menú de consola
python -m pytest      # pruebas automáticas
ruff check .          # revisión de estilo
```

## 6. Requisitos funcionales

| ID    | Requisito            | Criterio de verificación                                                                                                            |
| ----- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| RF-01 | Registrar emergencia | Con datos válidos, el sistema la guarda y muestra confirmación con su ID; con datos inválidos muestra el error y no se cierra       |
| RF-02 | Consultar y filtrar  | Con emergencias registradas, la búsqueda por texto y los filtros por tipo, estado y prioridad muestran únicamente las que coinciden |
| RF-03 | Actualizar estado    | Se puede cambiar el estado siguiendo pendiente → en proceso → finalizada; un cambio no permitido se rechaza con un mensaje          |

## 7. Equipo

| Integrante                             | Rol                                                     |
| -------------------------------------- | ------------------------------------------------------- |
| Amado Carrasco (@amadoCT)              | Coordinación, repositorio, workflows y documentación    |
| Jeremias Aguirre (@jeremias28a-dotcom) | Lógica y base de datos, interfaces de consola y gráfica |
| Aritzys Morales (@spikechim)           | Validaciones, actualización de estado y pruebas         |

## 8. Herramientas de análisis y calidad

- **Ruff:** estilo y formato, ejecutado en GitHub Actions.
- **Pytest:** pruebas automáticas, ejecutadas en GitHub Actions.
- **Snyk:** análisis de seguridad de dependencias.

## 9. Organización del trabajo

- 📋 Tablero del proyecto: https://github.com/users/amadoCT/projects/1
- 🔀 Flujo de trabajo (GitHub Flow, ramas, revisiones y Conventional Commits):
  [docs/flujo_trabajo.md](docs/flujo_trabajo.md)
