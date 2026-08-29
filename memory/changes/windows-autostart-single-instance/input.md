---
type: external-input
jira_key: "POM-4"
jira_url: "https://larayapdev.atlassian.net/browse/POM-4"
issue_type: "Historia"
labels: []
---

## Contexto

- **Reporter**: Luis Araya
- **Tipo**: Historia
- **Estado**: Stand by
- **Labels**: —

## Descripción

### Contexto

Work Tracker ya se comporta como app residente: tiene icono en bandeja (`createTray()`) y la ventana se oculta al cerrar en vez de salir (`src/background.js`). Falta la pieza que hace útil ese comportamiento: arrancar automáticamente al iniciar sesión en Windows. Además, hoy no existe single-instance lock, por lo que abrir el ejecutable manualmente con la app ya corriendo crea una segunda instancia que cuenta sobre el mismo log de uso.

### Alcance

1. **Casilla en el instalador NSIS** («Iniciar Work Tracker al arrancar Windows»):
   - Vía `nsis.include` con un `installer.nsh` (`customInstall`/`customUnInstall`).
   - Si se marca, escribe la entrada en `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` apuntando al ejecutable instalado con el argumento `--hidden`.
   - La desinstalación elimina la entrada del registro siempre (esté o no marcada la casilla en una reinstalación).
   - Default de la casilla: **desmarcada**.
2. **Instancia única** (`app.requestSingleInstanceLock()`):
   - Si el lock no se obtiene, la instancia nueva termina de inmediato.
   - El evento `second-instance` en la instancia original muestra y enfoca la ventana existente (equivalente a `showMainWindow()`).
3. **Arranque oculto**:
   - Si `process.argv` incluye `--hidden`, la app arranca solo a la bandeja, sin mostrar la ventana principal.
   - El arranque automático deja la app residente; **no** inicia monitoreo automáticamente.

### Notas técnicas

- Electron `^13.0.0`; instalación por usuario (`perMachine: false`, `oneClick: false` en `vue.config.js`) → la ruta del ejecutable en `%LOCALAPPDATA%\Programs` es estable entre actualizaciones y la clave `Run` no se rompe al actualizar.
- Restricción del bundle del main process: techo ES2016 — no usar `?.` ni `??` en `src/background.js` (el `npm run build` no lo detecta; solo compila el renderer).
- Decisión registrada: el estado del autoarranque lo administra el instalador (no hay toggle dentro de la app). El usuario puede desactivarlo además desde Administrador de tareas → Inicio.

## Criterios de aceptación

- Instalando con la casilla marcada, al reiniciar sesión la app aparece solo en la bandeja (sin ventana visible) y un clic en el icono abre la ventana.
- Instalando con la casilla desmarcada, no existe entrada en `HKCU\...\Run`.
- Desinstalar elimina la entrada `Run` si existía.
- Con la app corriendo, ejecutar el acceso directo de nuevo no abre una segunda instancia: enfoca la ventana existente (mostrándola si estaba oculta).
- El arranque manual (sin `--hidden`) sigue mostrando la ventana como hoy.

## Adjuntos

| Nombre | URL | MIME | Tamaño |
|--------|-----|------|--------|

Sin adjuntos.

## Metadatos Jira

- **jira_key**: POM-4
- **jira_url**: https://larayapdev.atlassian.net/browse/POM-4
- **issue_type**: Historia
- **labels**: —
