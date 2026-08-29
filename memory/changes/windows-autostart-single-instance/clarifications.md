---
type: clarifications
change_name: windows-autostart-single-instance
created: "2026-08-09"
---

## Iteración 1 — Preguntas

### Q1 — El criterio de aceptación sobre el arranque manual describe un comportamiento que hoy no existe

El ticket dice: «El arranque manual (sin `--hidden`) sigue mostrando la ventana como hoy».

Verificado en el código del worktree: `createWindow()` (`src/background.js:63`) crea la ventana
con `show: false` y **ninguna ruta la muestra durante el arranque**. Los únicos `.show()` del
proyecto son `showMainWindow()` (línea 117, que solo invocan el clic y el menú de la bandeja) y la
ventana de historial (línea 219). No hay handler de `ready-to-show` para la ventana principal.
El `show: false` viene del commit original del proyecto, y el mensaje de `5860da0` ya dejaba
constancia de que el flujo de la bandeja nunca se probó en Windows.

Es decir: **hoy la app ya arranca oculta siempre**. Sin resolver esto, `--hidden` sería un no-op
y el criterio de aceptación no es verificable.

- **(a)** El arranque manual debe **mostrar** la ventana (comportamiento nuevo: agregar
  `ready-to-show` → `show()` cuando no viene `--hidden`). Amplía el alcance con un arreglo del
  arranque actual, pero es la única lectura en que `--hidden` significa algo.
- **(b)** Conservar literalmente el comportamiento actual (siempre oculto) y dejar `--hidden` como
  marca sin efecto observable, reservada para uso futuro.

Recomendación: **(a)**.

### Q2 — ¿Una reinstalación o actualización debe preservar el estado del autoarranque?

El ticket fija «default de la casilla: desmarcada». En un instalador asistido esa casilla se
muestra también al reinstalar sobre una instalación existente (el flujo de actualización de
electron-builder desinstala la versión vieja y vuelve a correr `customInstall`).

- **(a)** La casilla se pre-marca leyendo si ya existe la entrada `Run`, y `customInstall` escribe
  o borra según su estado final. En una instalación limpia no hay entrada, así que aparece
  desmarcada: el criterio del ticket se cumple igual. La casilla pasa a ser un toggle real.
- **(b)** Siempre desmarcada. Cada reinstalación o actualización manual apaga el autoarranque sin
  avisar, y el usuario debe volver a marcarla en cada versión.

Recomendación: **(a)**.

### Q3 — ¿Cómo se produce el instalador para verificar?

`release.yml` solo compila en Windows ante un tag `v*` y publica la release. La verificación de
este cambio necesita un `.exe` antes de publicar nada.

- **(a)** Build local en el entorno Windows ya montado (`C:\...\cronometro-app-win`) vía interop
  desde WSL2. Requiere Node 16.20.2 y `npm ci` funcionando ahí (incluida la recompilación nativa
  de `active-win`), lo que no está confirmado.
- **(b)** Tag de pre-release (`v2.1.0-rc.1`) para que CI produzca el instalador. Choca con la
  guarda «tag == package.json.version» del workflow, que exigiría versionar el rc.
- **(c)** Agregar un workflow manual (`workflow_dispatch`) que compile en `windows-latest` y suba
  el instalador como artifact sin publicar release. Es trabajo adicional fuera del alcance del ticket.

Recomendación: **(a)**, con **(c)** como respaldo si el build local no arranca.

## Iteración 1 — Respuestas (2026-08-09)

- **Q1**: (a) — El arranque manual debe **mostrar** la ventana. Agregar `ready-to-show` → `show()` cuando NO viene `--hidden`. El alcance incorpora el arreglo del arranque actual; `--hidden` pasa a tener efecto observable.
- **Q2**: (a) — La casilla se **pre-marca leyendo la entrada `Run` existente** y `customInstall` escribe o borra según su estado final. En instalación limpia aparece desmarcada (cumple el default del ticket). Toggle real e idempotente.
- **Q3**: (a) — Verificación con **build local en el entorno Windows ya montado** (`C:\...\cronometro-app-win`) vía interop WSL2, con (c) workflow manual como respaldo si el build local no arranca.

### Feedback adicional del usuario (misma iteración, 2026-08-09)

Aparte de la opción de arranque con Windows, el comportamiento al iniciar la app debe ser
**configurable**: si se muestra la ventana o si queda solo en la bandeja del sistema.
Además, esa opción debe poder configurarse **desde la configuración de la propia app**
(no solo quedar fijada por el instalador/flag).

Implicancias a resolver en el refinamiento:
- Esto ajusta la «decisión registrada» previa de "sin toggle dentro de la app": la
  visibilidad al arranque SÍ tiene control in-app. El autoarranque con Windows sigue
  administrado por el instalador (eso no cambió).
- Definir la relación entre la preferencia persistida in-app y el flag `--hidden` del
  autoarranque (¿la preferencia gobierna todo arranque y `--hidden` actúa como override
  del arranque automático, o la preferencia reemplaza al flag?).
- Identificar dónde persiste la app sus settings hoy (OpcionesPanel.vue / userData) y
  seguir ese mismo mecanismo.

## Iteración 2 — Preguntas

### Q4 — Confirmar la semántica propuesta: ¿`--hidden` ignora la preferencia?

La propuesta ya adopta una semántica y la sostiene; esta pregunta existe para que puedas vetarla
antes de que baje a spec.

- **(a) — adoptada en la propuesta.** `--hidden` **siempre gana**: el arranque automático con
  Windows inicia en bandeja aunque la preferencia diga «mostrar ventana». La preferencia gobierna
  todo arranque manual. Camino único, sin combinaciones que resolver, y el instalador no necesita
  saber nada de la preferencia. Costo: con autoarranque activo y preferencia «mostrar», al iniciar
  sesión no aparece la ventana; puede leerse como que la opción no funciona.
- **(b)** La preferencia gobierna **todo** arranque y `--hidden` pasa a ser un default que la
  preferencia puede sobreescribir. Más «obediente», pero convierte el autoarranque en algo que
  puede abrir una ventana sin que el usuario haya pedido abrir la app, que es justo lo que el
  arranque a bandeja evita.

Recomendación: **(a)**.

### Q5 — ¿Qué valor por defecto toma `startupVisibility`?

Los defaults viven en `defaultSettings` (`src/main/ipc-handlers.js:18`) y `get-settings` los mergea
sobre el `settings.json` en disco, así que el default elegido aplica por igual a instalaciones
nuevas y a las existentes (que hoy no tienen la clave).

- **(a)** `'window'` — mostrar la ventana. Coherente con Q1=(a), que declaró defectuoso el
  «siempre oculto» actual. Al actualizar, los usuarios existentes empiezan a ver la ventana al
  abrir la app: es un cambio de comportamiento visible, aunque sea el comportamiento correcto.
- **(b)** `'tray'` — conservar lo que la app hace hoy y dejar que quien quiera la ventana la
  active. No sorprende a nadie al actualizar, pero mantiene por defecto un arranque que parece
  fallido para un usuario nuevo (abre el .exe y no pasa nada visible).

Recomendación: **(a)**.

## Iteración 2 — Respuestas (2026-08-09)

- **Q4**: **(b)** — override de la recomendación. La preferencia `startupVisibility` gobierna
  **todo** arranque, incluido el automático con Windows: con preferencia `'window'`, la ventana
  aparece también al iniciar sesión. Consecuencia aceptada: el flag `--hidden` deja de gobernar
  la visibilidad (la SSOT de visibilidad es la preferencia persistida); redefinir o eliminar el
  flag en la entrada Run según lo que resulte más simple.
- **Q5**: (a) — default `startupVisibility: 'window'`, aplica también a instalaciones existentes.
- **Decisión global**: [A] Aprobar — con Q4b y Q5a integradas la propuesta queda aprobada;
  el pipeline continúa a sdd-spec sin nueva pausa.
