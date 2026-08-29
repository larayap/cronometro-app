---
type: capability-spec
title: "Correcciones de judgment (ui-branding-polish): altura del bloque de agrupar y modo de falla documentado de un token ausente"
capability: "session-groups"
slug: "judgment-fixes-ui-branding-polish"
domain: "feature"
delta_type: added
supersedes: null
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: medium
depends_on: ["[[full-surface-drop-target-for-grouping]]"]
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["0cfd1e7"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "El bloque de agrupar de un grupo nuevo conserva al menos la altura visible que tenía antes de esta corrección, con la etiqueta de invitación adentro"
  - "Toda la superficie visible del bloque de agrupar de un grupo nuevo —etiqueta incluida— acepta el drop sin depender del umbral de inserción de listas vacías de SortableJS"
  - "ADR-0015 describe el modo de falla real de un token ausente: la declaración queda inválida en tiempo de valor computado y el indicador de foco desaparece por completo"
related: ["[[full-surface-drop-target-for-grouping]]", "[[group-composition-and-drag]]", "[[shared-accent-colors-across-windows]]"]
affects: ["[[full-surface-drop-target-for-grouping]]"]
adrs: ["[[0008-sessions-and-groups-as-entry-metadata]]", "[[0015-shared-css-token-layer-across-renderer-bundles]]"]
scope: ["src/components/CronometroAplicacion.vue", "memory/adrs/0015-shared-css-token-layer-across-renderer-bundles.md"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec, judgment-fix]
---

# Correcciones de judgment (ui-branding-polish)

## Purpose

`sdd-judgment` devolvió veredicto FAIL en la iteración 1. Un juez adjudicó tres hallazgos y el
otro ninguno; el triage confirmó los tres mecánicamente contra el código instalado de
SortableJS y contra el CSS real del componente, y retuvo dos como trabajo. La evidencia
completa está en `changes/ui-branding-polish/judgment-report.md`; acá va solo lo que hay que
corregir y con qué criterio se da por corregido.

Ninguno de los dos ítems toca la mecánica de arrastre: el movimiento de la etiqueta al slot
`#header` de `vuedraggable` quedó verificado como correcto por ambos jueces, a nivel del código
de SortableJS. Lo que falta es el ajuste de caja que el diseño dio por innecesario y una
corrección de documentación.

## Requirements

### C1 — El bloque de agrupar de un grupo nuevo conserva su altura visible (medium)

Mover `.group-strip` al slot `#header` del `<draggable v-model="dragNewGroup">` metió la
etiqueta **dentro** de la caja que `.new-group-list { min-height: 40px }` dimensiona
(`src/components/CronometroAplicacion.vue:368-370`). El `min-height` quedó sin ajustar, así que
los 40px que antes eran área vacía debajo de la etiqueta ahora tienen que absorber la etiqueta
entera: el bloque punteado pasa de ~73px a ~42px de altura visible (la etiqueta mide ~31px:
`font-size: 0.75rem` más `padding: 0.5rem` arriba y abajo), mientras el nodo Sortable sigue
midiendo 40px.

`design.md § D-6.4` afirma que "el modelo de caja resultante es idéntico y no hace falta tocar
ninguna declaración". Es cierto para los grupos existentes —`.group-header` no tiene alto
mínimo que competir y el contenedor mide lo mismo antes y después— y **falso** para la franja
de creación, que es el único de los dos bloques cuyo alto lo fija un `min-height` sobre el
propio nodo Sortable.

El efecto neto de la corrección del ítem 6 sobre la franja de creación queda entonces en cero:
alinea lo visible con lo activo (que era el defecto a corregir) pero deja el área que el usuario
puede acertar en los mismos 40px, con un bloque 42% más chico que nadie pidió encoger.

- El bloque de agrupar de un grupo nuevo SHALL conservar al menos la altura visible que tenía
  antes de esta corrección, con la etiqueta de invitación contenida adentro.
- Toda la superficie visible de ese bloque —etiqueta incluida— SHALL aceptar el drop de una
  fila.
- La corrección SHALL NO alterar la mecánica de arrastre ya verificada: sin tocar la plantilla
  de los `<draggable>`, sus handlers, sus guardas (`isDragging` / `pendingRows` /
  `pendingIntent`) ni el `<draggable v-model="dragUngrouped">`, que no lleva slot `#header`.

Dirección preferida (KISS, una declaración): subir el `min-height` de `.new-group-list` para que
absorba el alto de la etiqueta **más** los 40px de área vacía que el bloque tenía antes (~72px),
y actualizar el comentario de esas líneas, que hoy justifica el `min-height` como "sin alto
propio, SortableJS no tendría área sobre la que aceptar el drop" — con la etiqueta adentro el
nodo ya tiene alto propio, y lo que el `min-height` preserva ahora es el área de destino por
debajo de la etiqueta.

No introducir `height` fijo ni tocar `.group-strip`, `.group-header`, `.group-container` ni
`.drag-list`: el resto de las cajas mide lo mismo antes y después del cambio.

### C2 — ADR-0015 debe describir el modo de falla real de un token ausente (low)

`ADR-0015 § Consequences` afirma que si un entry del renderer no importa `tokens.css`, "los
acentos caen al valor por defecto del navegador o de la librería". No es lo que pasa. Las tres
reglas que consumen el token lo hacen sin valor de respaldo —`src/styles/tokens.css:24`,
`src/components/TitleBar.vue:276` y `src/history/HistoryView.vue:310`, todas
`var(--focus-ring)` a secas—, así que con el token indefinido la declaración queda *invalid at
computed-value time* y se comporta como `unset`: `outline` cae a `outline-style: none` y el
`box-shadow` a `none`. El resultado no es otro color, es **ningún indicador de foco**, y en
silencio.

Eso importa porque el propio diseño borró los 9 `outline: none` preexistentes (`D-1.2`)
apoyándose en que la regla global siempre aplica, y porque dentro de `.vc-container` el
`outline: none` de v-calendar deja al `box-shadow` de `HistoryView.vue:310` como único indicador
de las celdas del calendario. La salvaguarda que el ADR invoca —que el costo sería "visible de
inmediato"— no existe: un anillo de foco ausente no se nota hasta que alguien navega con Tab.

No hay defecto vivo: los dos entries importan `tokens.css` y los cuatro tokens llegan a los dos
bundles compilados (verificado de forma independiente por los dos jueces sobre
`dist/css/index.*.css` y `dist/css/history.*.css`). Lo que hay que corregir es el modelo mental
que el ADR documenta, porque es el que dejaría pasar la regresión en un refactor futuro.

- ADR-0015 SHALL describir el modo de falla real de un token ausente: declaración inválida en
  tiempo de valor computado, sin indicador de foco, sin señal visible hasta que se navega con
  teclado.

**Explícitamente fuera de alcance**: agregar valores de respaldo (`var(--focus-ring, #e0e0e0)`).
Duplicaría el valor del token en tres lugares y contradiría el SSOT que ADR-0015 establece; la
protección sería además parcial, porque los tres tokens del rango del calendario tampoco lo
llevan. La mitigación correcta es que el ADR diga la verdad sobre la consecuencia, y que el
único punto de definición siga siendo `tokens.css`.

## Scenarios

### Scenario: El bloque de agrupar de un grupo nuevo no se encoge

**GIVEN** al menos una fila suelta en el listado visible
**WHEN** el usuario mira el bloque de agrupar de un grupo nuevo
**THEN** el bloque tiene al menos la misma altura visible que tenía antes de esta corrección,
con la etiqueta de invitación adentro

### Scenario: Soltar sobre la etiqueta del bloque de un grupo nuevo agrupa la fila

**GIVEN** dos o más filas sueltas en el listado visible
**WHEN** el usuario arrastra una y la suelta sobre la etiqueta de invitación del bloque de
agrupar
**THEN** esa fila pasa a formar parte de un grupo nuevo

### Scenario: El resto de la mecánica de agrupar no cambia

**GIVEN** dos filas ya agrupadas
**WHEN** el usuario consulta su reloj individual, su entrada de historial y el total del grupo,
y saca una fila del grupo
**THEN** los tres se comportan igual que antes de esta corrección y la fila vuelve al listado
suelto

## Acceptance Criteria

- [x] El bloque de agrupar de un grupo nuevo conserva al menos la altura visible que tenía antes
  de esta corrección, con la etiqueta de invitación adentro.
- [x] Toda la superficie visible del bloque de agrupar de un grupo nuevo —etiqueta incluida—
  acepta el drop sin depender del umbral de inserción de listas vacías de SortableJS.
- [x] ADR-0015 describe el modo de falla real de un token ausente: la declaración queda inválida
  en tiempo de valor computado y el indicador de foco desaparece por completo.

## Notas de verificación

C1 es verificable en este entorno por lectura del CSS y por cálculo del modelo de caja; la
confirmación óptica y el arrastre real quedan diferidos al entorno Windows, como el resto del
guion manual de este cambio (`verify-report.md § Límite de entorno`). El umbral de inserción de
listas vacías (`emptyInsertThreshold: 5` de SortableJS) **deja de aplicar** a la franja de
creación desde que el slot `#header` le da un hijo permanente —`_detectNearestEmptySortable`
aborta cuando `lastChild(sortable)` es truthy y lo consulta sin selector
(`node_modules/sortablejs/modular/sortable.core.esm.js:1106-1110`)—, así que la corrección de
C1 no debe apoyarse en ese halo de 5px: el área de destino tiene que estar dentro del rectángulo
del bloque. El drop sigue resolviéndose por el camino normal de `_onDragOver`, que con la lista
sin hijos `[data-draggable]` cae en `el.appendChild(dragEl)` sin ninguna comprobación
geométrica.

C2 es una corrección de texto, verificable por lectura.

Sin test runner en el proyecto: la verificación es estática, como en el resto del cambio.

## Related

- [[full-surface-drop-target-for-grouping]] — C1 completa su corrección: sin el ajuste de caja,
  el bloque de creación cumple el criterio de "toda la superficie acepta el drop" encogiendo el
  bloque en vez de agrandando el destino
- [[group-composition-and-drag]] — sus criterios ya cumplidos no se tocan; C1 es puramente
  dimensional
- [[shared-accent-colors-across-windows]] — C2 corrige el modo de falla documentado de la capa
  de tokens que esta spec establece
