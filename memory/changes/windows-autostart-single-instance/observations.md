---
type: change-observations
change_name: windows-autostart-single-instance
created: "2026-08-09"
updated: "2026-08-09"
tags: [change-observations]
---

# Observations — windows-autostart-single-instance (sdd-apply)

## V2 — el stub de `electron` vía `NODE_PATH` de tasks.md no aplica en esta topología

`tasks.md` prescribe inyectar un stub de `electron` con `NODE_PATH` para poder llamar
`readSettings()` fuera de un proceso Electron real. En este repo el worktree cuelga de
`.sdd/worktrees/<change>/` **dentro del propio repo principal**
(`/home/larayap/cronometro-app/.sdd/worktrees/windows-autostart-single-instance`), así que la
resolución normal de módulos de Node, al hacer `require('electron')` desde
`src/main/ipc-handlers.js`, camina hacia arriba del árbol de directorios y encuentra
`/home/larayap/cronometro-app/node_modules/electron` (el paquete real) antes de llegar a mirar
`NODE_PATH`, que en el algoritmo de resolución de Node tiene prioridad más baja que los
`node_modules` hallados por ese recorrido — confirmado con
`require.resolve('electron')` apuntando al paquete real incluso sin ningún `node_modules`
propio en el worktree.

Se logró el mismo objetivo de V2 (electron stubeado, sin instancia real, mismos 3 casos)
interceptando `Module._load` en un script descartable, en vez de depender de `NODE_PATH`. El
script no forma parte del repo (vivió en el scratchpad de la sesión). Resultado: los 3 casos
pasaron sin cambios de comportamiento respecto a lo que tasks.md esperaba verificar.

## V1 — `node_modules` del worktree

El worktree no trae `node_modules` propio (correcto: está gitignoreado y no se corrió
`npm install` ahí). Para poder correr `npx vue-cli-service lint`, se verificó primero que
`package.json` y `package-lock.json` fueran idénticos byte a byte entre el worktree y `main`
(`diff` limpio en ambos) y se enlazó temporalmente (`ln -s`) el `node_modules` del repo
principal — de solo lectura, sin instalar nada nuevo ni tocar el repo principal — y se removió
el symlink apenas terminó el lint, antes de correr V2 (cuyo resultado dependía de que
`require('electron')` NO resolviera al paquete real).

## Acceptance criteria de las tres specs: ninguno verificable localmente

Los `acceptance_criteria` de `installer-opt-in-autostart`, `startup-visibility-preference` y
`single-instance-focus` quedan **todos sin marcar** tras `sdd-apply`. Los tres describen
comportamiento observable que requiere, como mínimo, un proceso Electron real corriendo
(`startup-visibility-preference`, `single-instance-focus`) o el instalador NSIS compilado y
ejecutado en Windows (`installer-opt-in-autostart`) — ninguno de los dos es factible en este
WSL2 (sin `makensis` en el `PATH`, y el entorno Windows de verificación ya montado —
`windows-build-stale-and-blocked`— se reserva para W1 en `sdd-verify`). Lo que sí se verificó
localmente (V1/V2/V3 en `tasks.md`) cubre la mitad determinista y sin efectos secundarios de
la lógica: lint limpio, ausencia de `?.`/`??` en el bundle del main, el merge de
`readSettings()` con sus tres casos, y la estructura estática del `.nsh` (macros balanceados,
`HKCU` literal, guard `${ifNot} ${isUpdated}`). La matriz completa de comportamiento
(W1) queda íntegra para `sdd-verify`.

## Riesgo no verificado: codificación UTF-8 del `.nsh`

`build/installer.nsh` usa caracteres acentuados en español directamente (comentarios y el
texto del checkbox: "automáticamente", "sesión"). No se pudo compilar con `makensis` en este
WSL2 para confirmar que NSIS los renderiza correctamente en el instalador real — depende de
que el archivo se lea como UTF-8 en tiempo de compilación (comportamiento por defecto de NSIS
3.x con Unicode habilitado, que es el caso acá vía `unicode` no seteado a `false` en
`vue.config.js`). Si W1 muestra el texto del checkbox con caracteres corruptos, es el primer
punto a revisar.
