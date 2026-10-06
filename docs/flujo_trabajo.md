# Guía de Flujo de Trabajo y Colaboración — Proyecto SIGEAH

Este documento establece las normas y convenciones obligatorias para el desarrollo del proyecto **SIGEAH** mediante **GitHub Flow**.

---

## 1. Gestión de Tareas (Kanban Board)
El proyecto utiliza un tablero Kanban en **GitHub Projects** estructurado en 4 columnas:

1. **Pendiente:** Issues creados y priorizados que aún no han sido asignados.
2. **En proceso:** Tareas en desarrollo activo. Cada integrante mueve su Issue aquí al iniciar.
3. **En revisión:** Tareas con desarrollo finalizado y un Pull Request (PR) abierto.
4. **Finalizado:** Issues cerrados cuyo PR correspondiente ya fue aprobado y fusionado en `main`.

---

## 2. Estrategia de Ramas (GitHub Flow)
- **`main`:** Rama principal de producción. Está protegida y requiere 1 aprobación de PR para integrar cambios. **Prohibido el push directo.**
- **Ramas secundarias:** Se crean obligatoriamente a partir de `main` con la nomenclatura:
  - `feat/nombre-tarea` (Nuevas funcionalidades)
  - `fix/nombre-error` (Corrección de fallos)
  - `docs/nombre-doc` (Documentación)
  - `chore/nombre-config` (Mantenimiento o configuración)

---

## 3. Convención de Commits (Conventional Commits)
Todos los mensajes de commit deben seguir el estándar:

`<tipo>: <descripción breve en minúsculas>`

### Tipos permitidos:
- **`feat:`** Nueva característica.
- **`fix:`** Corrección de un error o bug.
- **`docs:`** Cambios exclusivamente en la documentación.
- **`test:`** Adición o corrección de pruebas unitarias.
- **`chore:`** Tareas de mantenimiento, configuración o herramientas.

---

## 4. Ciclo de Pull Requests (PR) y Revisiones
1. Crear el PR hacia `main` vinculando el Issue correspondiente (ej. `Closes #1`).
2. Solicitar la revisión a un compañero de equipo.
3. Tras recibir al menos **1 aprobación** y verificar la integración, fusionar (*Merge*) el PR.
4. Eliminar la rama secundaria (*Delete branch*) tanto en remoto como en local.