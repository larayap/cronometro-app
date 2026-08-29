---
type: proposal
change_name: windows-autostart-single-instance
status: approved
effort: M
created: "2026-08-09"
updated: "2026-08-09"
---

# Autoarranque con Windows, visibilidad configurable e instancia única

## Intent

Que Work Tracker pueda arrancar al iniciar sesión en Windows (opt-in desde el instalador),
que el usuario decida desde **Opciones** si al abrir la app ve la ventana o queda solo en la
bandeja —una única preferencia que gobierna **todo** arranque, manual o automático—, y que
ejecutar el binario con la app ya corriendo enfoque la ventana existente en vez de levantar una
segunda instancia que cuenta sobre el mismo `sessions.json`. Origen: Jira POM-4.

## Decisiones firmes (aprobadas)

- **D1** — El arranque **muestra** la ventana. Hoy no lo hace: `createWindow()` la crea con
  `show: false` (`src/background.js:70`) y ninguna ruta la muestra. Se corrige. Queda subsumida
  en D4 + D5: la preferencia gobierna, y su default es `'window'`.
- **D2** — La casilla del instalador se **pre-marca** leyendo la entrada `Run` existente y
  `customInstall` escribe o borra según su estado final. Toggle real e idempotente; en instalación
  limpia aparece desmarcada, cumpliendo el default del ticket.
- **D3** — Verificación con **build local** en el entorno Windows ya montado
  (`C:\...\cronometro-app-win`) vía interop; workflow `workflow_dispatch` como respaldo.
- **D4** — **`startupVisibility` es la SSOT de la visibilidad al arrancar**, sin excepciones: con
  `'window'` la ventana aparece también en el logon; con `'tray'`, siempre bandeja. El flag
  `--hidden` **deja de gobernar la visibilidad** y desaparece del cambio: la entrada `Run` no lleva
  argumento alguno. Camino único, sin ramas por origen del arranque (KISS/YAGNI).
- **D5** — Default `startupVisibility: 'window'` en `defaultSettings` del main. Aplica también a
  instalaciones existentes: `get-settings` mergea `defaultSettings` sobre el archivo
  (`src/main/ipc-handlers.js:63-66`), así que un `settings.json` viejo hereda el default al
  actualizar sin migración.

## Scope

**Dentro**: `build/installer.nsh` (nuevo), `vue.config.js` (`nsis.include`), `src/background.js`,
`src/main/ipc-handlers.js`, `src/stores/settings.js`, `src/components/OpcionesPanel.vue`.
**Fuera**: toggle del **autoarranque** dentro de la app (sigue administrado por el instalador),
in-app updater, soporte no-Windows, iniciar monitoreo automáticamente al arrancar.

## Approach técnico

electron-builder **22.14.13** verificado en el worktree. Hooks NSIS soportados por esa versión
(leídos en `app-builder-lib/templates/nsis/`): `customHeader`, `preInit`, `customInit`,
`customInstallMode`, `customWelcomePage`, `customPageAfterChangeDir`, `customInstall`,
`customUnInit`, `customRemoveFiles`, `customUnInstall`.

**1. Casilla en el instalador** — `build/installer.nsh`, declarado como `nsis.include` dentro de
`pluginOptions.electronBuilder.builderOptions.nsis`. `build/` no está en `.gitignore`.

- `customPageAfterChangeDir` → página **nsDialogs** con un checkbox, pre-marcado según la entrada
  `Run` (D2). Es el único punto de inserción en orden correcto: `assistedInstaller.nsh`
  (`installer.nsi:33`) inserta todas las páginas MUI —incluida FINISH— **antes** del hook
  `customHeader` (`installer.nsi:38`), así que un `MUI_PAGE_COMPONENTS` inyectado por macro
  quedaría después de la página final. No viable.
- `customInstall` (dentro de la Section install, `installSection.nsh:78`, con `$INSTDIR` resuelto) →
  `WriteRegStr` / `DeleteRegValue` sobre
  `HKCU "Software\Microsoft\Windows\CurrentVersion\Run"` con valor
  `'"$INSTDIR\${APP_EXECUTABLE_FILENAME}"'` — **sin flags** (D4). Las comillas se conservan: el
  ejecutable es `Work Tracker.exe` (con espacio) y el valor sin comillas es ambiguo para el
  parser de `Run`. HKCU literal, no `SHELL_CONTEXT`.
- `customUnInstall` (`uninstaller.nsh:114`) → `DeleteRegValue` **guardado con `${ifNot} ${isUpdated}`**:
  al actualizar, el instalador nuevo corre el desinstalador viejo con `--updated`
  (`installUtil.nsh:203`) antes de `customInstall`; sin el guard cada actualización apagaría el
  autoarranque en silencio.

**2. Instancia única** — `src/background.js`: `app.requestSingleInstanceLock()` antes de registrar
`before-quit`. Sin lock → `app.exit(0)`, no `app.quit()` (`quit()` emite `before-quit`, que llama
`monitorEngine.closeAllRows('app-quit')` y escribiría sobre el `sessions.json` de la instancia
ganadora). `second-instance` → `restore()` si está minimizada + `showMainWindow()`: es una acción
explícita del usuario, siempre muestra, sin consultar la preferencia.

**3. Visibilidad al arrancar: la preferencia, y nada más (D4).**

*Persistencia — el mecanismo ya existe, no se inventa uno nuevo*: la app guarda sus opciones en
`settings.json` bajo `userData` (`src/main/ipc-handlers.js:14-18`), con `defaultSettings` en el main
como SSOT de los defaults (`get-settings` los mergea; el store **deliberadamente no los duplica**,
comentario en `src/stores/settings.js:22-24`). Se agrega
`startupVisibility: 'window' | 'tray'` con default `'window'` (D5).

*El problema de orden se resuelve sin canal IPC nuevo*: `jsonStore.readJson` es **síncrono**
(`fs.readFileSync`, `src/main/json-store.js:8`) y el archivo es del main. Se exporta desde
`ipc-handlers.js` un `readSettings()` que reutiliza `getSettingsFilePath()` y `defaultSettings`, y
`background.js` lo llama directo en el arranque —antes de que exista renderer—. Los canales
`get-settings`/`save-settings` ya existentes transportan la clave nueva sin modificación.
**Invariante**: la lectura debe ocurrir después de `migrateUserDataAt` porque `settings.json` está
en `OWNED_FILES` (`src/main/userdata-migration.js:42`); ya se cumple, `createWindow()` corre al
final de `whenReady`.

```js
// src/background.js — dentro de createWindow(), sin ?. ni ?? (techo ES2016)
// Sin lectura de process.argv: el origen del arranque no entra en la decisión.
if (readSettings().startupVisibility !== 'tray') {
  mainWindow.once('ready-to-show', function () { mainWindow.show() })
}
```

`ready-to-show` es el patrón que el propio proyecto ya usa para la ventana de historial
(`src/background.js:219`).

*Renderer*: en `src/stores/settings.js`, la clave se agrega al `state`, a la carga y —crítico— al
payload de `persist()`, que es el **único punto de escritura**; omitirla ahí borraría la
preferencia del disco cada vez que se mueve un volumen (la propia clase de defecto documentada en
el comentario de las líneas 30-33). En `OpcionesPanel.vue`, un `<select>` en un `div.setting-control`
calcado del control «Formato de hora» ya existente (líneas 30-40), con texto de apoyo que aclare que
la opción rige **todo** arranque, **incluido el automático con Windows**.

## Trade-offs explícitos

| Decisión | Alternativa descartada | Costo aceptado |
|---|---|---|
| La preferencia gobierna todo arranque; el flag `--hidden` se elimina (D4) | `--hidden` soberano en el arranque automático | Con autoarranque activo y preferencia `'window'` —el default— la ventana aparece en **cada inicio de sesión**; quien quiera logon silencioso debe fijar `'tray'`. Decisión explícita del usuario |
| Default `'window'`, también para instalaciones existentes (D5) | Default `'tray'` | Al actualizar, quien ya usaba la app pasa a ver la ventana al abrir; es exactamente el defecto D1 corregido, nadie queda oculto por sorpresa |
| Preferencia leída del `settings.json` existente | `electron-store`, archivo propio, o IPC nuevo | Ninguno relevante: reutiliza store, canales y defaults ya en producción (SSOT/DRY) |
| Autoarranque solo en el instalador | `app.setLoginItemSettings()` + toggle in-app | Dos controles emparentados viven en lugares distintos; la app no puede leer ni cambiar su propio autoarranque |
| Página nsDialogs propia | `MUI_PAGE_COMPONENTS` | Una página de asistente para una casilla (componentes es inviable, ver arriba) |
| `app.exit(0)` en la instancia perdedora | `app.quit()` | Se saltea todo cleanup futuro registrado en `before-quit` |

## Riesgos

- **Nada de esto se verifica desde WSL2**: el instalador exige build, instalación y reinicio de
  sesión en Windows. `probabilidad: Alta` — impacto Alto: cada iteración del `.nsh` cuesta un ciclo
  completo de build.
- **Un error de sintaxis NSIS solo aparece en `makensis`, durante `electron:build`**: `npm run lint`
  no lo ve y `npm run build` solo compila el renderer. `probabilidad: Media` — impacto Medio.
- **La preferencia desaparece del disco** si `persist()` no incluye la clave nueva; cualquier cambio
  de volumen la borraría. `probabilidad: Media` — impacto Medio.
- **La instancia perdedora corrompe el historial** vía `before-quit` → `closeAllRows()`.
  `probabilidad: Media` — impacto Alto.
- **Actualización que apaga el autoarranque** sin el guard `${ifNot} ${isUpdated}`.
  `probabilidad: Alta` sin el guard, `Baja` con él — impacto Medio.
- **Queda una rama muerta por `--hidden`** si el flag sobrevive en algún punto (entrada `Run`, lectura
  de `process.argv`) y contradice la preferencia. `probabilidad: Baja` — impacto Medio: la verificación
  incluye inspeccionar el valor del registro, que debe quedar sin argumentos.
- **Ruptura del bundle del main por sintaxis > ES2016**. `probabilidad: Baja` — impacto Medio.
- **Heurística de antivirus/SmartScreen** ante un instalador sin firmar que escribe en `Run`.
  `probabilidad: Baja` — impacto Medio, fuera del control del cambio.

## Esfuerzo

**M**. El alcance nuevo agrega ~30 líneas repartidas en tres archivos, todas calcadas de patrones ya
presentes (clave en `defaultSettings`, control en `OpcionesPanel`, `ready-to-show` del historial);
D4 lo reduce en vez de aumentarlo (una condición, sin lectura de `argv`). El costo dominante sigue
siendo el ciclo de verificación manual en Windows y la iteración a ciegas sobre la página nsDialogs.

## Verificación propuesta

No hay test runner. Verificación manual en el entorno Windows montado (D3): `npm run electron:build`,
instalar con la casilla marcada y desmarcada, `reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Work Tracker"`
en ambos casos —el valor debe ser la ruta del `.exe` **sin argumentos**—, reinstalación sobre
instalación existente (la casilla debe llegar pre-marcada y el autoarranque sobrevivir), doble
ejecución del acceso directo y desinstalación.

Matriz de visibilidad (4 casos, mismo resultado esperado en ambos orígenes):

| Origen | `startupVisibility` | Esperado |
|---|---|---|
| Manual (acceso directo) | `'window'` | Ventana visible |
| Manual (acceso directo) | `'tray'` | Solo bandeja |
| Logon con autoarranque | `'window'` | Ventana visible |
| Logon con autoarranque | `'tray'` | Solo bandeja |

Además: actualizar sobre una instalación previa sin la clave y confirmar que llega `'window'` por
merge de defaults (D5); y cambiar el volumen después de fijar la preferencia y reabrir, para
confirmar que `persist()` no la borró.
