---
type: change-tasks
change_name: windows-autostart-single-instance
spec_refs: ["[[installer-opt-in-autostart]]", "[[startup-visibility-preference]]", "[[single-instance-focus]]"]
created: "2026-08-09"
updated: "2026-08-09"
tags: [change-tasks]
---

# Tasks — windows-autostart-single-instance

Sin test runner en el proyecto (ESLint 7, sin Jest/Vitest/Mocha): ninguna tarea se marca
`[TDD]`. Introducir un test runner solo para este cambio violaría YAGNI — no está en la
propuesta ni en las specs.

## Orden de ejecución

Las secciones B (`startup-visibility-preference`) y C (`single-instance-focus`) tocan ambas
`src/background.js`; ejecutar B antes que C dentro de ese archivo evita reescribir el mismo
bloque dos veces. La sección A (`installer-opt-in-autostart`) es independiente de B y C —
archivos distintos (`build/installer.nsh`, `vue.config.js`) — y puede ejecutarse en cualquier
punto, pero se lista primero porque así aparece en `spec_refs` de `state.md`.

Orden sugerido: **A1 → A2 → A3 → A4 → B1 → B2 → B3 → B4 → B5 → C1 → C2 → V1 → V2 → V3**.
(`Bx` corresponde a las tareas de `startup-visibility-preference`, `Cx` a las de
`single-instance-focus`, para no chocar con la letra de sección `A`/`B`/`C` de más abajo —
ver la tabla de correspondencia al inicio de cada sección.)

---

## Sección A — Autoarranque opt-in desde el instalador ([[installer-opt-in-autostart]])

Archivos: `build/installer.nsh` (nuevo), `vue.config.js`.

Contexto verificado contra `node_modules/app-builder-lib/templates/nsis/*.nsh` (electron-builder
22.14.13 ya instalado en el repo): el hook `customPageAfterChangeDir` existe en
`assistedInstaller.nsh:44-46`, `customInstall` en `installSection.nsh:78-80` (corre después de
`installApplicationFiles`, con `$INSTDIR` ya resuelto), `customUnInstall` en
`uninstaller.nsh:114-116`, y el patrón `${ifNot} ${isUpdated}` ya se usa en
`uninstaller.nsh:82` para no repetir un efecto en cada actualización — mismo patrón a reusar
acá. `${PRODUCT_NAME}` y `${APP_EXECUTABLE_FILENAME}` están definidos por electron-builder
(`common.nsh:11,13`).

- [x] **A1. Crear `build/installer.nsh` con el macro `customPageAfterChangeDir`** (casilla de
  autoarranque, pre-marcada según el estado real del sistema).
  - Qué hacer: declarar una variable global para el estado de la casilla (p. ej.
    `Var /GLOBAL AutostartCheckbox_State`); antes de `nsDialogs::Show`, leer
    `ReadRegStr $0 HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${PRODUCT_NAME}"` y
    usar el resultado (`$0 != ""`) para fijar el estado inicial de la casilla —
    literal `HKCU`, no `SHELL_CONTEXT` (D4: la propuesta fija HKCU sin importar el contexto
    per-user/per-machine de la instalación). Insertar la página con
    `nsDialogs::Create 1018` / `${NSD_CreateCheckbox}` / `nsDialogs::Show`, siguiendo el
    patrón estándar de páginas custom de electron-builder-NSIS.
  - Archivo: `build/installer.nsh` (nuevo).
  - Criterio de completado: el archivo define `!macro customPageAfterChangeDir` con
    `!macroend` balanceado; la lectura previa usa `HKCU` literal; la casilla queda marcada
    cuando la clave `Run\${PRODUCT_NAME}` ya existe.
  - Depende de: ninguna.

- [x] **A2. Agregar el macro `customInstall` en `build/installer.nsh`** (escribe o borra la
  entrada `Run` según el estado final de la casilla).
  - Qué hacer: dentro de `!macro customInstall`, según el valor final de la variable de
    estado de A1: si quedó marcada,
    `WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${PRODUCT_NAME}" '"$INSTDIR\${APP_EXECUTABLE_FILENAME}"'`;
    si no, `DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${PRODUCT_NAME}"`.
    Sin argumentos en el valor (D4 — el flag `--hidden` no existe; la visibilidad la decide
    `startupVisibility`, sección B, en cada arranque, no un argumento de línea de comandos).
  - Archivo: `build/installer.nsh`.
  - Criterio de completado: instalación limpia con la casilla desmarcada no deja entrada
    `Run`; con la casilla marcada, la entrada `Run\${PRODUCT_NAME}` queda con el path exacto
    del ejecutable entre comillas, sin argumentos adicionales.
  - Depende de: A1 (usa la misma variable de estado de la casilla).

- [x] **A3. Agregar el macro `customUnInstall` en `build/installer.nsh`**, guardado contra
  falsos positivos en actualizaciones.
  - Qué hacer: `DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${PRODUCT_NAME}"`
    dentro de `${ifNot} ${isUpdated} ... ${endif}` (mismo patrón que
    `uninstaller.nsh:82` usa para `isDeleteAppData`) — sin el guard, cada actualización
    (que corre el desinstalador viejo con `--updated` antes de reinstalar) apagaría el
    autoarranque en cada release nueva.
  - Archivo: `build/installer.nsh`.
  - Criterio de completado: desinstalar de forma normal borra la entrada `Run` si existía;
    el macro está envuelto en `${ifNot} ${isUpdated}`.
  - Depende de: ninguna (puede escribirse junto con A1/A2 en el mismo archivo, sin orden
    estricto entre sí).

- [x] **A4. Registrar el include en `vue.config.js`**.
  - Qué hacer: agregar la clave `include: 'build/installer.nsh'` dentro de
    `pluginOptions.electronBuilder.builderOptions.nsis` (junto a `oneClick`, `perMachine`,
    `allowElevation`, `allowToChangeInstallationDirectory`, líneas 91-99 actuales).
  - Archivo: `vue.config.js`.
  - Criterio de completado: `nsis.include === 'build/installer.nsh'` en la config exportada;
    el resto de las claves de `nsis` queda intacto.
  - Depende de: A1 (el archivo referenciado debe existir; `vue.config.js` no valida su
    existencia al cargar, pero el build de electron-builder sí).

---

## Sección B — Preferencia de visibilidad al arrancar ([[startup-visibility-preference]])

Archivos: `src/main/ipc-handlers.js`, `src/stores/settings.js`, `src/components/OpcionesPanel.vue`,
`src/background.js`.

Patrón a calcar en todo punto: `timeFormat` (`configurable-time-format-preference`, ya
implementada end-to-end) — mismo mecanismo de merge de default en `get-settings`, mismo
`persist()` unificado en el store, mismo tipo de control en `OpcionesPanel.vue`.

- [x] **B1. Agregar `startupVisibility: 'window'` a `defaultSettings` en
  `src/main/ipc-handlers.js`** (D5 — SSOT del default).
  - Qué hacer: extender el objeto `defaultSettings` (línea 18 actual:
    `{ masterVolume: 1, interactionVolume: 1, timeFormat: '24h' }`) con la clave
    `startupVisibility: 'window'`.
  - Archivo: `src/main/ipc-handlers.js`.
  - Criterio de completado: `defaultSettings.startupVisibility === 'window'`; el handler
    `get-settings` (que ya mergea `defaultSettings` primero) sigue funcionando sin cambios
    adicionales — el merge existente cubre la clave nueva automáticamente.
  - Depende de: ninguna.

- [x] **B2. Exportar `readSettings()` desde `src/main/ipc-handlers.js`** (lectura síncrona
  para el arranque, fuera del canal IPC).
  - Qué hacer: extraer a una función nombrada `readSettings()` el merge que hoy arma inline
    el handler `get-settings` (`{ ...defaultSettings, ...jsonStore.readJson(getSettingsFilePath(), {}) }`);
    hacer que el handler `get-settings` llame a `readSettings()` en vez de repetir el merge
    (sin duplicar lógica); agregar `readSettings` al `module.exports` junto a
    `registerIpcHandlers`.
  - Archivo: `src/main/ipc-handlers.js`.
  - Criterio de completado: `require('./main/ipc-handlers.js').readSettings` es una función
    que, llamada sin argumentos, devuelve el mismo objeto que hoy arma el handler
    `get-settings`; el handler sigue devolviendo exactamente el mismo resultado que antes de
    la extracción (mismo comportamiento observable, solo refactor).
  - Depende de: B1.

- [x] **B3. Agregar `startupVisibility` al store `src/stores/settings.js`**.
  - Qué hacer: estado inicial `startupVisibility: 'window'` (línea ~14, junto a
    `timeFormat: '24h'`); en `load()`, tomar `settings.startupVisibility` de la respuesta de
    `get-settings` sin fallback propio (mismo comentario/patrón que `timeFormat` — el default
    ya lo entrega el main); en `persist()`, incluir `startupVisibility: this.startupVisibility`
    en el payload de `save-settings` (payload único, D-2 del diseño: agregar la clave sin
    pasar por acá borraría la preferencia al mover el volumen); agregar la acción
    `setStartupVisibility(v) { this.startupVisibility = v; this.persist() }`, calcada de
    `setTimeFormat`.
  - Archivo: `src/stores/settings.js`.
  - Criterio de completado: `persist()` envía 4 claves (`masterVolume`, `interactionVolume`,
    `timeFormat`, `startupVisibility`); `setStartupVisibility` sigue el mismo patrón que
    `setTimeFormat` (asignación + `persist()`, sin lógica adicional).
  - Depende de: B1 (consume el default vía IPC; no lo duplica en el store — ADR-0012).

- [x] **B4. Agregar el control de visibilidad al arranque en
  `src/components/OpcionesPanel.vue`**.
  - Qué hacer: calcar el bloque `.setting-control` de «Formato de hora» (líneas 30-40
    actuales): `<select>` con `:value="settingsStore.startupVisibility"` y
    `@change="settingsStore.setStartupVisibility($event.target.value)"`, opciones
    `value="window"` → «Mostrar la ventana» y `value="tray"` → «Solo en la bandeja»; agregar
    un texto de apoyo (p. ej. `<small>`) que aclare que la preferencia rige todo arranque,
    incluido el automático con el inicio de sesión de Windows.
  - Archivo: `src/components/OpcionesPanel.vue`.
  - Criterio de completado: el `<select>` nuevo sigue la misma estructura markup/estilo que
    el de «Formato de hora»; el texto de apoyo menciona explícitamente el arranque
    automático (no solo "arranque").
  - Depende de: B3.

- [x] **B5. Consumir `readSettings()` en `createWindow()` de `src/background.js`** para
  decidir si se muestra la ventana al arrancar.
  - Qué hacer: importar `readSettings` desde `./main/ipc-handlers.js` (junto al `require`
    existente de `registerIpcHandlers`, línea 14); dentro de `createWindow()` (después de
    que `mainWindow` queda creado con `show: false`), agregar:
    `if (readSettings().startupVisibility !== 'tray') { mainWindow.once('ready-to-show', function () { mainWindow.show() }) }`
    — sin leer `process.argv` en ningún punto (D4: el origen del arranque, manual o
    automático, es irrelevante).
  - Archivo: `src/background.js`.
  - Criterio de completado: con `startupVisibility: 'tray'` persistido, `createWindow()` no
    agenda ningún `.show()` automático (la ventana existe oculta, mostrable después vía el
    tray o `showMainWindow()`); con `'window'` o sin `settings.json` todavía, se agenda el
    show al evento `ready-to-show`. La lectura ocurre dentro de `createWindow()`, que ya
    corre después de `userDataMigration.migrateUserDataAt` en `whenReady()` — invariante ya
    cumplida, sin cambios adicionales en el orden de arranque.
  - Depende de: B2.

---

## Sección C — Instancia única ([[single-instance-focus]])

Archivo: `src/background.js` (mismo archivo que B5 — ejecutar después de B5 para no
reescribir el mismo bloque dos veces).

- [x] **C1. Adquirir el lock de instancia única, antes de cualquier registro de listeners de
  ciclo de vida**.
  - Qué hacer: al principio del módulo (antes de `protocol.registerSchemesAsPrivileged` no
    hace falta moverlo, pero sí antes de `app.whenReady().then(...)` y, sobre todo, antes de
    `app.on('before-quit', ...)`), agregar
    `const gotTheLock = app.requestSingleInstanceLock()` seguido de
    `if (!gotTheLock) { app.exit(0) }` — **no** `app.quit()`: `quit()` dispara `before-quit`
    → `monitorEngine.closeAllRows('app-quit')`, que escribiría sobre el `sessions.json` de la
    instancia ganadora (spec: "la instancia perdedora no altera el historial").
  - Archivo: `src/background.js`.
  - Criterio de completado: en una segunda ejecución mientras la primera sigue corriendo, el
    proceso nuevo llama `app.exit(0)` sin haber llamado `app.quit()` ni disparado
    `before-quit`; el resto del módulo (registro de `before-quit`, `whenReady`, etc.) no se
    ejecuta de forma dañina en la instancia perdedora — `app.exit(0)` termina el proceso de
    inmediato.
  - Depende de: ninguna (independiente de B, pero mismo archivo — ejecutar después de B5 por
    orden de edición, no por dependencia funcional).

- [x] **C2. Registrar el handler `second-instance`** que enfoca la ventana existente,
  restaurándola si está minimizada, sin consultar `startupVisibility`.
  - Qué hacer:
    `app.on('second-instance', () => { if (mainWindow && mainWindow.isMinimized()) mainWindow.restore(); showMainWindow() })`
    — reutiliza `showMainWindow()` ya existente (línea 113 actual), que ya llama
    `.show()` y `.focus()` incondicionalmente; ninguna rama de este handler llama
    `readSettings()` (spec: el enfoque ante un segundo arranque es una acción explícita que
    siempre muestra la ventana, sin importar la preferencia).
  - Archivo: `src/background.js`.
  - Criterio de completado: con la ventana minimizada, un segundo arranque la restaura y
    enfoca; con la ventana oculta por `startupVisibility: 'tray'`, un segundo arranque la
    muestra igual; no hay entradas duplicadas ni pérdida en `sessions.json` (la instancia
    nueva ya salió por C1 antes de tocar cualquier estado de monitoreo).
  - Depende de: C1 (debe registrarse solo en la rama donde `gotTheLock` es verdadero, es
    decir, después del `if (!gotTheLock) { app.exit(0) }` de C1).

---

## Verificación local (factible desde WSL2)

- [x] **V1. Lint de los archivos modificados**.
  - Comando: `npm run lint` desde la raíz del worktree (o `npx vue-cli-service lint --no-fix`
    acotado a los archivos tocados si el lint completo es ruidoso por archivos no tocados en
    este cambio).
  - Alcance: `src/background.js`, `src/main/ipc-handlers.js`, `src/stores/settings.js`,
    `src/components/OpcionesPanel.vue`.
  - Atención adicional (ESLint no lo detecta): techo ES2016 del bundle del main
    (`src/background.js`, `src/main/ipc-handlers.js`) — revisar a mano que ninguna línea
    nueva de B2/B5/C1/C2 use `?.` ni `??` (memoria: `npm run build` solo compila el
    renderer, no detecta esto).
  - Criterio de completado: `npm run lint` sale sin errores nuevos atribuibles a este
    cambio; revisión manual de las líneas nuevas en el main sin `?.`/`??` confirmada.
  - Depende de: A1-A4, B1-B5, C1-C2 (corre sobre el resultado final).
  - **Resultado**: `npx vue-cli-service lint --no-fix` (worktree sin `node_modules` propio;
    se linkeó temporalmente el `node_modules` del repo principal — `package.json` y
    `package-lock.json` idénticos byte a byte entre worktree y `main`, verificado con `diff`
    antes de linkear — y se removió después de usarlo) → 0 errores, 1 warning preexistente en
    `CronometroManual.vue` (`vue/no-deprecated-destroyed-lifecycle`), archivo no tocado por
    este cambio. `grep -n '?\.\|??' src/background.js src/main/ipc-handlers.js` → sin
    coincidencias.

- [x] **V2. Verificación funcional de `readSettings()` sin levantar Electron completo**.
  - Motivo: `readSettings()` (B2) depende de `app.getPath('userData')`, que solo existe
    dentro de un proceso Electron real. Se verifica con un stub mínimo de `electron`
    inyectado por `NODE_PATH` — patrón ya probado durante esta fase de tasks (requerir
    `ipc-handlers.js` con el stub no rompe pese a que `icon-cache.js` y otros módulos del
    main también hacen `require('electron')`, porque ninguno toca `nativeImage`/`app` a
    nivel de módulo, solo dentro de funciones que acá no se invocan).
  - Comandos (usar un directorio temporal cualquiera, p. ej. `mktemp -d`):
    ```bash
    STUB=$(mktemp -d)
    FAKE_USERDATA=$(mktemp -d)
    mkdir -p "$STUB/node_modules/electron"
    printf '{"name":"electron","main":"index.js"}' > "$STUB/node_modules/electron/package.json"
    printf 'module.exports = { app: { getPath: () => process.env.FAKE_USERDATA } }' > "$STUB/node_modules/electron/index.js"

    # Caso 1: sin settings.json -> default 'window'
    FAKE_USERDATA="$FAKE_USERDATA" NODE_PATH="$STUB/node_modules" node -e "
      const { readSettings } = require('$PWD/src/main/ipc-handlers.js');
      const s = readSettings();
      if (s.startupVisibility !== 'window') throw new Error('esperaba window, fue ' + s.startupVisibility);
      console.log('OK sin settings.json:', s.startupVisibility);
    "

    # Caso 2: settings.json parcial (sin startupVisibility) -> también 'window'
    printf '{"timeFormat":"12h"}' > "$FAKE_USERDATA/settings.json"
    FAKE_USERDATA="$FAKE_USERDATA" NODE_PATH="$STUB/node_modules" node -e "
      const { readSettings } = require('$PWD/src/main/ipc-handlers.js');
      const s = readSettings();
      if (s.startupVisibility !== 'window') throw new Error('esperaba window, fue ' + s.startupVisibility);
      console.log('OK settings.json sin la clave:', s.startupVisibility);
    "

    # Caso 3: settings.json con startupVisibility 'tray' -> se respeta
    printf '{"startupVisibility":"tray"}' > "$FAKE_USERDATA/settings.json"
    FAKE_USERDATA="$FAKE_USERDATA" NODE_PATH="$STUB/node_modules" node -e "
      const { readSettings } = require('$PWD/src/main/ipc-handlers.js');
      const s = readSettings();
      if (s.startupVisibility !== 'tray') throw new Error('esperaba tray, fue ' + s.startupVisibility);
      console.log('OK settings.json con tray:', s.startupVisibility);
    "
    ```
  - Criterio de completado: los tres casos imprimen `OK` sin lanzar. Cubre el merge de
    default (B1+B2) que consume B5 en el arranque real — no cubre el `.show()` condicional
    en sí, que requiere Electron real (diferido a W1).
  - Depende de: B1, B2.
  - **Resultado**: el stub por `NODE_PATH` tal como está escrito arriba **no aplica** en
    esta topología de directorios — el worktree cuelga de `.sdd/worktrees/` dentro del propio
    repo principal (`/home/larayap/cronometro-app/.sdd/worktrees/windows-autostart-single-instance`),
    así que la resolución normal de módulos de Node camina hacia arriba del árbol y encuentra
    `/home/larayap/cronometro-app/node_modules/electron` (el paquete real) antes de mirar
    `NODE_PATH`, que tiene prioridad más baja en el algoritmo de resolución — confirmado con
    `require.resolve('electron')` apuntando al paquete real incluso sin `node_modules` propio
    en el worktree. Se logró el mismo objetivo (stub de `electron` sin instancia real, mismos
    3 casos) interceptando `Module._load` en un script descartable
    (`/tmp/.../scratchpad/verify-readSettings.js`, no forma parte del repo) en vez de
    `NODE_PATH`. Resultado: los 3 casos imprimieron `OK` — sin `settings.json` → `window`;
    `settings.json` sin la clave → `window`; `settings.json` con `tray` → `tray`.

- [x] **V3. Revisión estática de `build/installer.nsh`** (sin compilación real: `makensis` no
  está disponible en este WSL2, confirmado ausente del `PATH`; compilar el `.nsi` completo
  requiere el resto del template de electron-builder, no solo el fragmento incluido).
  - Comando de referencia:
    `grep -n "customPageAfterChangeDir\|customInstall\|customUnInstall\|!macro\|!macroend\|SHELL_CONTEXT\|HKCU" build/installer.nsh`
  - Verificar a mano sobre esa salida: los tres macros (`customPageAfterChangeDir`,
    `customInstall`, `customUnInstall`) están presentes; cada `!macro` tiene su
    `!macroend`; ningún `WriteRegStr`/`DeleteRegValue`/`ReadRegStr` usa `SHELL_CONTEXT` (debe
    ser `HKCU` literal en los tres, por D4); el macro `customUnInstall` envuelve el
    `DeleteRegValue` en `${ifNot} ${isUpdated}`.
  - Criterio de completado: los cuatro puntos de la revisión a mano confirmados; no
    reemplaza la compilación real del instalador (diferida a W1).
  - Depende de: A1, A2, A3.
  - **Resultado**: `makensis` confirmado ausente del `PATH` en este WSL2. El grep de
    referencia confirma los cuatro puntos: los tres macros (`customPageAfterChangeDir`,
    `customInstall`, `customUnInstall`) presentes; 3 `!macro` con 3 `!macroend` (balanceado);
    todos los `ReadRegStr`/`WriteRegStr`/`DeleteRegValue` usan `HKCU` literal, sin
    `SHELL_CONTEXT` (la única mención de `SHELL_CONTEXT` en el archivo está dentro de un
    comentario explicando por qué no se usa); `customUnInstall` envuelve su `DeleteRegValue`
    en `${ifNot} ${isUpdated}` / `${endIf}`.

---

## Verificación diferida a sdd-verify (requiere Windows)

- [ ] **W1. Matriz de verificación completa de la propuesta, en el entorno Windows ya
  montado** (memoria `windows-build-stale-and-blocked`: reusar el entorno de verificación en
  `C:\...\cronometro-app-win`; **no** el `.exe` instalado, que es de mar-2025 y está
  desactualizado).
  - Requiere primero: `electron:build` (respetando el techo ES2016 del bundle del main) y
    generación real del instalador NSIS con `build/installer.nsh` incluido — ninguna de las
    dos cosas es factible en WSL2 para este proyecto (sin `wine`+`makensis` verificado como
    ruta confiable para NSIS de electron-builder, y sin entorno Windows real para probar
    rutas de registro).
  - Matriz a ejecutar (de `proposal.md`):
    - Manual × {`window`, `tray`} y logon-autoarranque × {`window`, `tray`} → la ventana
      aparece exactamente cuando la preferencia es `'window'`, en las cuatro combinaciones.
    - `reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"` tras instalar con la
      casilla marcada → entrada presente, sin argumentos.
    - Reinstalar sobre una instalación con autoarranque activo → casilla pre-marcada;
      actualizar → autoarranque conservado.
    - Desinstalar → entrada `Run` eliminada (instalación no-actualización).
    - Actualizar sobre un `settings.json` sin la clave `startupVisibility` → hereda
      `'window'`.
    - Cambiar el volumen después de fijar `startupVisibility` → la clave sobrevive en
      `settings.json` (confirma el `persist()` unificado de B3).
    - Segunda ejecución con la app ya corriendo (ventana visible, oculta y minimizada) →
      enfoca/restaura sin abrir instancia nueva ni alterar `sessions.json`.
  - Criterio de completado: las siete verificaciones de la matriz con resultado PASS,
    documentadas en el reporte de `sdd-verify`.
  - Depende de: A1-A4, B1-B5, C1-C2, V1-V3 (todo el código y la revisión estática ya
    verificados localmente antes de gastar el ciclo de verificación en Windows).
