---
type: change-verify-report
change_name: windows-autostart-single-instance
spec_refs: ["[[installer-opt-in-autostart]]", "[[startup-visibility-preference]]", "[[single-instance-focus]]"]
verdict: partial
created: "2026-08-09"
updated: "2026-08-09"
tags: [change-verify-report]
---

# Verify Report — windows-autostart-single-instance

Veredicto: **PARTIAL por limitación de entorno** (ver sección dedicada al final). Todas las
verificaciones locales realizables desde WSL2 pasan; el bloqueo es exclusivamente la matriz de
comportamiento que exige Windows real (W1), tal como ya anticipaban `proposal.md`,
`tasks.md` y `observations.md` de `sdd-apply`.

Todas las verificaciones de esta sección fueron **re-ejecutadas de forma independiente**
(no se reutilizaron los resultados de `sdd-apply`, salvo como punto de comparación).

## Verificaciones locales re-ejecutadas de forma independiente

- **Lint** (`npx vue-cli-service lint --no-fix`, tras symlink temporal y transitorio de
  `node_modules` del repo principal, removido al terminar): **0 errores, 1 warning
  preexistente** en `src/components/CronometroManual.vue` (`vue/no-deprecated-destroyed-lifecycle`,
  archivo no tocado por este cambio). Coincide con lo reportado por `sdd-apply` (V1).
- **Techo ES2016**: `grep -n '?\.\|??' src/background.js src/main/ipc-handlers.js` → sin
  coincidencias en los dos archivos del main tocados por este cambio.
- **`readSettings()`, 3 casos** (interceptando `Module._load` con un script propio y
  descartable, distinto del de `sdd-apply`, mismo objetivo: el worktree cuelga de
  `.sdd/worktrees/` dentro del repo principal, así que `NODE_PATH` no gana la resolución de
  `require('electron')` — confirmado independientemente):
  - Sin `settings.json` → `{"startupVisibility":"window", ...}`. OK.
  - `settings.json` con `{"timeFormat":"12h"}` (sin la clave) → `startupVisibility: "window"`. OK.
  - `settings.json` con `{"startupVisibility":"tray"}` → `startupVisibility: "tray"`. OK.
- **Revisión estática de `build/installer.nsh`**: 3 `!macro`/`!macroend` balanceados
  (`customPageAfterChangeDir`, `customInstall`, `customUnInstall`); todo `ReadRegStr`/
  `WriteRegStr`/`DeleteRegValue` usa `HKCU` literal (la única mención de `SHELL_CONTEXT` está en
  un comentario explicando por qué no se usa); el valor `Run` se escribe como
  `'"$INSTDIR\${APP_EXECUTABLE_FILENAME}"'` — comillas presentes, sin argumentos; `customUnInstall`
  envuelve `DeleteRegValue` en `${ifNot} ${isUpdated}` / `${endIf}`.
- **`vue.config.js`**: `nsis.include === 'build/installer.nsh'`, resto de claves de `nsis` intacto.

## installer-opt-in-autostart

| Acceptance Criteria | Estado |
|---|---|
| Instalación limpia ofrece la opción sin marcar por defecto | Revisión estática PASS (lógica en `AutostartPageCreate`: `BST_UNCHECKED` si `ReadRegStr` no encuentra la clave) — comportamiento en instalador real DIFERIDO |
| Marcar la opción deja el arranque registrado | Revisión estática PASS (`customInstall`, rama `BST_CHECKED` → `WriteRegStr`) — DIFERIDO |
| No marcar la opción deja sin arranque | Revisión estática PASS (`customInstall`, rama `${Else}` → `DeleteRegValue`, no-op en instalación limpia) — DIFERIDO |
| Reinstalar conserva el estado ya elegido | Revisión estática PASS (`AutostartPageCreate` lee `Run\${PRODUCT_NAME}` existente y pre-marca) — DIFERIDO |
| Actualizar conserva el arranque activado | Revisión estática PASS (`customUnInstall` guardado con `${ifNot} ${isUpdated}`, mismo patrón que `isDeleteAppData` de electron-builder) — DIFERIDO |
| Desinstalar quita el arranque | Revisión estática PASS (`customUnInstall`, rama normal sin `isUpdated`) — DIFERIDO |

Los 6 criterios están **verificados a nivel de lógica estática**, ninguno a nivel de
comportamiento real (requiere `makensis` + instalación/reinstalación/actualización/
desinstalación en Windows). Ver intento de build más abajo.

## startup-visibility-preference

| Acceptance Criteria | Estado |
|---|---|
| El panel ofrece elegir ventana/bandeja | PASS (estático: `<select>` en `OpcionesPanel.vue` con `value="window"`/`value="tray"`, `:value`/`@change` ligados a `settingsStore.startupVisibility`/`setStartupVisibility`) |
| Elegir "ventana" muestra la ventana en todo arranque | PASS (estático, flujo): `createWindow()` agenda `.show()` en `ready-to-show` salvo `startupVisibility === 'tray'` — comportamiento runtime DIFERIDO |
| Elegir "bandeja" no muestra la ventana en ningún arranque | PASS (estático, flujo): con `'tray'` no se agenda ningún `.show()` — runtime DIFERIDO |
| La preferencia se mantiene entre reinicios | PASS (estático): `persist()` en `stores/settings.js` incluye `startupVisibility` en las 4 claves del payload de `save-settings`; `readSettings()` la relee — runtime DIFERIDO |
| Usuario que nunca eligió ve la ventana | PASS (verificado con los 3 casos de `readSettings()` de arriba: sin `settings.json` y con uno sin la clave, ambos devuelven `'window'`) |

Coherencia adicional verificada por lectura de código (no solo revisión de `sdd-apply`):
- `defaultSettings.startupVisibility === 'window'` en `src/main/ipc-handlers.js:18` (SSOT, D5).
- `readSettings()` (línea 25-30) hace el mismo merge que antes armaba inline el handler
  `get-settings`, ahora reutilizado por ambos consumidores (IPC y `background.js`).
- `stores/settings.js`: estado inicial `startupVisibility: 'window'`, `load()` la toma de
  `get-settings` sin fallback propio, `persist()` la incluye, `setStartupVisibility(v)` sigue
  el mismo patrón que `setTimeFormat(v)`.
- **Orden de arranque real** (leído completo `src/background.js`): `app.whenReady().then(async () => { ... userDataMigration.migrateUserDataAt(...) ...; createTray(); createWindow() })` —
  `migrateUserDataAt` corre primero (líneas ~174-181), `createWindow()` se invoca al final del
  callback (línea 198), y `readSettings()` se llama dentro de `createWindow()` (línea 107). El
  orden migración → `readSettings()` se cumple en el único camino real de arranque. `createWindow()`
  es reentrante (también la llaman `showMainWindow()` y `activate`), pero esas rutas solo pueden
  dispararse después de que `whenReady()` ya completó, así que el invariante se sostiene en todos
  los caminos observables.
- `OpcionesPanel.vue`: el `<small>` de apoyo menciona explícitamente "el arranque automático con
  el inicio de sesión de Windows" (no solo "arranque").

Runtime real (mostrar/ocultar ventana con Electron corriendo, en ambos orígenes de arranque):
DIFERIDO a W1.

## single-instance-focus

| Acceptance Criteria | Estado |
|---|---|
| Máximo una instancia corriendo | PASS (estático): `app.requestSingleInstanceLock()` al inicio del módulo, antes de cualquier registro de listener |
| Segundo arranque enfoca la ventana existente | PASS (estático): `app.on('second-instance', ...)` llama `showMainWindow()`, que hace `.show()` + `.focus()` incondicional |
| Ventana minimizada se restaura y enfoca | PASS (estático): el handler chequea `mainWindow.isMinimized()` y llama `.restore()` antes de `showMainWindow()` |
| Instancia perdedora no altera el historial | PASS (estático, más fuerte de lo documentado por `sdd-apply`): ver hallazgo abajo |

Hallazgo de flujo, verificado con lectura completa del archivo: el bloque
`if (!gotTheLock) { app.exit(0) }` está en las líneas 32-34 de `src/background.js`, **antes**
de la definición de `createTray()`, de `createWindow()`, de `app.whenReady().then(...)` y del
`app.on('before-quit', () => monitorEngine.closeAllRows('app-quit'))` (línea 308). Como el
módulo se ejecuta top-to-bottom y `app.exit(0)` termina el proceso de inmediato, en la instancia
perdedora **el listener `before-quit` nunca llega a registrarse** — no es solo que `app.exit()`
evite disparar `before-quit` en vez de `app.quit()`, sino que el resto del módulo, incluido el
registro de ese listener, no se ejecuta en absoluto. Garantía más fuerte que la mínima exigida
por la spec.

`second-instance` (línea 40-43) no llama `readSettings()` en ninguna rama — confirmado por
lectura íntegra del handler — cumple el requisito de no consultar la preferencia.

Ejecución real con dos procesos Electron simultáneos: DIFERIDO a W1.

## Intento best-effort de build en el entorno Windows

Se localizó el entorno de verificación ya montado (`C:\Users\Luis Araya\dev\cronometro-app-win`,
accesible por `/mnt/c` sin abrir ninguna ventana ni tocar el escritorio real). Hallazgo no
documentado antes: **no es un repositorio git** y su `package.json` (`cronometro-apps@1.0.0`,
con scripts de `electron-forge`) y su árbol `src/` son de una generación anterior del proyecto
—le falta por completo `src/main/userdata-migration.js` y tiene componentes desactualizados—,
bastante más atrás que el rename a `work-tracker`. `devDependencies` clave (`electron@^13.0.0`,
`vue-cli-plugin-electron-builder@~2.1.1`, `eslint@^7.32.0`, etc.) sí coinciden con el stack
actual, así que su `node_modules` (con fecha 05-08-2026) es utilizable sin `npm ci`.

Se sincronizó (copia de archivos, sin tocar `node_modules`/`package.json`/`package-lock.json`
existentes) el árbol completo `src/`, `build/`, `public/`, `vue.config.js`, `babel.config.cjs`,
`jsconfig.json`, `.eslintrc.js` del worktree (HEAD `dec815d`) hacia ese directorio, y se lanzó
`npm run electron:build` como proceso batch (`CSC_IDENTITY_AUTO_DISCOVERY=false`, sin firma), en
background, con salida espejada a
`C:\Users\Luis Araya\dev\cronometro-app-win\electron-build-verify.log`.

**Resultado dentro del presupuesto de esta verificación (~4 minutos de espera acotada, sin
bloquear indefinidamente)**: el build alcanzó la etapa de *bundling* del renderer (`Building for
production...`, warnings repetidos de `browserslist` desactualizado, deoptimización de Babel en
`@fortawesome/free-solid-svg-icons`) pero **no llegó a completarse** dentro de la ventana
observada — no se vio ni el log de bundling del proceso main ni el de generación del instalador
NSIS, y `dist_electron/` todavía tenía `index.js` con fecha de un build anterior (06-08-2026),
sin sobrescribir. No se observó ningún error ni traceback en el log durante la ventana de espera.

**Se dejó el proceso corriendo en background** (no se mató): si terminó después de este reporte,
el resultado queda en `C:\Users\Luis Araya\dev\cronometro-app-win\electron-build-verify.log`
(el archivo está en UTF-16LE, típico de la salida de PowerShell redirigida — decodificar con
`iconv -f UTF-16LE -t UTF-8` antes de leerlo) y el instalador, de completarse, en
`C:\Users\Luis Araya\dev\cronometro-app-win\dist_electron\`. No se pudo, por tanto, inspeccionar
`makensis`/strings del instalador para confirmar que `build/installer.nsh` quedó incluido en el
build real — sigue diferido.

## Coherencia de Grafo de Specs

Alcance: las 3 specs de `spec_refs`. Las tres declaran `depends_on: []` y `affects: []` — no hay
ningún `T`/`U` que resolver por la regla de coherencia bidireccional depends_on/affects, así que
el chequeo es trivialmente consistente (nada que corregir, nada FAIL, nada WARN).

Como verificación adicional de higiene del grafo (fuera del alcance estricto de la regla, pero de
bajo costo), se confirmó que los specs referenciados en `related` de las tres specs existen en el
corpus: `unified-product-identity` (`project-identity/`), `configurable-time-format-preference`
(`app-settings/`), `judgment-fixes-iteration-1` y `sessions-json-persistence` (`app-monitoring/`).
También existen los dos ADRs referenciados: `0006-userdata-json-persistence` y
`0002-main-process-owns-monitoring-state`. Sin inconsistencias.

## PARTIAL por limitación de entorno

Causa única: no hay `makensis` en el PATH de WSL2 y el intento best-effort de compilar el
instalador completo en el entorno Windows montado no terminó dentro del presupuesto de esta
verificación (ver sección anterior) — no por un fallo de código detectado, sino por el tiempo que
toma el build completo (bundling + NSIS) y la imposibilidad de bloquear indefinidamente sobre un
proceso batch en una máquina de interop que es el escritorio real del usuario.

Todo lo estáticamente/funcionalmente verificable desde WSL2 (lint, techo ES2016, los 3 casos de
`readSettings()`, revisión estructural completa del `.nsh`, coherencia del `<select>` con el
store, `persist()` con las 4 claves, orden `migrateUserDataAt` → `createWindow()` → `readSettings()`,
`second-instance` sin `readSettings()`, `app.exit(0)` sin `app.quit()` con la garantía reforzada de
que `before-quit` ni se registra) da **PASS**.

Verificaciones diferidas al usuario (matriz W1, sin cambios respecto a lo ya previsto en
`tasks.md`):

1. Instalar limpio con la casilla marcada / desmarcada → `reg query
   "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Work Tracker"` en ambos casos.
2. Reinstalar sobre una instalación con autoarranque activo → casilla debe llegar pre-marcada.
3. Actualizar sobre una instalación con autoarranque activo → debe seguir activo tras actualizar.
4. Desinstalar (no como parte de una actualización) → la entrada `Run` debe desaparecer.
5. Matriz de visibilidad, 4 combinaciones: {manual, logon-autoarranque} × {`window`, `tray`} → la
   ventana aparece exactamente cuando la preferencia es `'window'`.
6. Cambiar el volumen después de fijar `startupVisibility` y reabrir → la clave debe sobrevivir en
   `settings.json`.
7. Segunda ejecución con la app ya corriendo (ventana visible, oculta y minimizada) → debe
   enfocar/restaurar sin abrir instancia nueva ni alterar `sessions.json`.
8. Confirmar que `C:\Users\Luis Araya\dev\cronometro-app-win\electron-build-verify.log` terminó
   sin errores y que el instalador generado en `dist_electron\` incluye el texto del checkbox de
   autoarranque sin corrupción de codificación (riesgo UTF-8 ya señalado en `observations.md` de
   `sdd-apply`, tampoco resuelto por este intento al no completar el build).

`verified_at` de las 3 specs **no se actualiza** (queda `null`): el veredicto es PARTIAL-por-entorno,
no PASS pleno.
