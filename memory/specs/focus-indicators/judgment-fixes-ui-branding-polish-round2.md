---
type: capability-spec
title: "Correcciones de judgment ronda 2 (ui-branding-polish): el indicador de foco cubre el botón de mes/año y el estado de sesión completada"
capability: "focus-indicators"
slug: "judgment-fixes-ui-branding-polish-round2"
domain: "feature"
delta_type: MODIFY
supersedes: "[[keyboard-focus-indicator-per-palette]]"
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: high
depends_on: ["[[shared-accent-colors-across-windows]]"]
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["f42f807", "7161abe"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "El control que abre el selector de mes/año del calendario de día y el del selector de rango tienen, cada uno, una regla de foco propia con la especificidad necesaria para no perder contra la regla de foco de la librería del calendario"
  - "Recorrer con Tab el calendario de día y el selector de rango en la ventana de historial muestra el indicador de foco sobre el control de mes/año"
  - "El campo de edición y el control de quitar de una sesión de Pomodoro usan, en el estado de sesión completada, un color de indicador de foco que se distingue del fondo de ese estado"
  - "Dar foco con teclado al campo de edición o al control de quitar de una sesión completada muestra, a simple vista, un indicador de foco perceptible"
  - "Las declaraciones de estilo sin efecto visible sobre las tarjetas de tipo de módulo ya no están en el código"
  - "El ajuste de layout compartido por las tarjetas de tipo de módulo deja constancia, en el propio código, de que también alcanza a la tarjeta del manual"
related: ["[[keyboard-focus-indicator-per-palette]]", "[[shared-accent-colors-across-windows]]"]
affects: []
adrs: ["[[0015-shared-css-token-layer-across-renderer-bundles]]"]
scope: ["src/history/HistoryView.vue", "src/components/CronometroPomodoro.vue", "src/components/TitleBar.vue"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec, judgment-fix]
---

# Correcciones de judgment ronda 2 (ui-branding-polish): el indicador de foco cubre el botón de mes/año y el estado de sesión completada

## Purpose

`keyboard-focus-indicator-per-palette` establece un requisito absoluto: ningún control de la
aplicación queda sin ninguna señal visual de foco al navegar con el teclado. `sdd-judgment`,
tras dos rondas con jueces independientes, confirmó que el cambio declara ese requisito
cumplido y no lo cumple en dos controles reales — el detalle completo está en
`changes/ui-branding-polish/judgment-report.md` (hallazgo C-1, instancias I-1 e I-2). Esta
corrección endurece el requisito exactamente donde falló: que el indicador sea efectivamente
perceptible en cada control y en cada estado en que ese control puede encontrarse, incluidos
los que un mecanismo de foco de una librería externa o un fondo dinámico pueden anular sin que
la regla global de la aplicación se entere. Aprovecha el mismo barrido para resolver dos
declaraciones de limpieza detectadas en los mismos archivos, sin promoverlas a requisito de
comportamiento observable.

## Requirements

### I-1 — El botón de mes/año del calendario recibe un indicador de foco propio (medium — comportamiento)

- El sistema SHALL mostrar un indicador de foco visible en el control que abre el selector de
  mes/año del calendario, en cada pantalla del historial en que ese control aparece, incluso
  cuando un mecanismo de foco propio de una librería externa integrada en el calendario
  suprime el indicador nativo de un control al que esa librería no le da su propio indicador.

### I-2 — El indicador de foco se distingue del fondo del control en cualquier estado (low — comportamiento)

- El sistema SHALL mostrar, en el campo de edición y en el control de quitar de una sesión, un
  indicador de foco que se distinga visualmente del fondo de ese control en cualquier estado
  en que el control pueda encontrarse — incluido el estado visual que identifica una sesión ya
  completada —, de modo que el indicador no quede, en la práctica, imperceptible en ninguno de
  esos estados.

### Límite de las dos correcciones anteriores

- La corrección de I-1 e I-2 SHALL NOT alterar el mecanismo global de foco que
  `keyboard-focus-indicator-per-palette` ya estableció — la regla única basada en la
  navegación por teclado, sus excepciones ya documentadas, y el resto de los controles que ya
  reciben el indicador correctamente —: se acota a los dos controles donde ese mecanismo
  demostradamente no alcanza.

### S-1 — Limpieza: declaraciones de estilo sin efecto en las tarjetas de tipo de módulo (low — limpieza, sin comportamiento observable)

- El sistema SHOULD eliminar, del selector de tipo de módulo, las declaraciones de estilo que
  quedaron sin ningún efecto visible desde que sus tarjetas muestran una imagen en lugar de una
  letra. No es un requisito de comportamiento: el estado de cada tarjeta (normal, resaltada,
  seleccionada) sigue comunicándose por los mismos medios visuales antes y después de esta
  limpieza, y ningún Scenario de esta spec depende de ella.

### S-2 — Limpieza: alcance documentado de un ajuste de layout ya aceptado (low — documentación, sin comportamiento observable)

- El sistema SHOULD dejar constancia, en el mismo lugar donde se declaró el ajuste, de que un
  ajuste de layout introducido para las tarjetas de tipo de módulo alcanza también a la tarjeta
  del manual, aunque esa tarjeta no formaba parte del motivo original del ajuste. No es un
  requisito de comportamiento: el cambio de alineación de esa tarjeta ya ocurrió y se acepta
  como mejora; lo que este punto corrige es que quede registrado, para que no se lea como una
  omisión de alcance.

## Scenarios

### Scenario: El botón de mes/año recibe indicador propio dentro del calendario

**GIVEN** el usuario abre la ventana de historial y navega con Tab dentro del calendario de
día o del selector de rango
**WHEN** el foco llega al control que abre el selector de mes/año
**THEN** ese control muestra el indicador de foco de la paleta de la aplicación, sin quedar
sin ninguna señal visual

### Scenario: El indicador de foco se distingue también sobre una sesión completada

**GIVEN** una sesión de Pomodoro que ya terminó, con el fondo visual propio de ese estado
**WHEN** el usuario le da el foco con el teclado al campo de edición o al control de quitar de
esa sesión
**THEN** el indicador de foco se distingue del fondo del control, de la misma forma en que se
distingue sobre una sesión en curso o pendiente

### Scenario: El resto del mecanismo de foco no cambia

**GIVEN** cualquier otro control ya cubierto por el indicador de foco de la paleta
**WHEN** el usuario navega hacia él con el teclado o lo activa con el mouse
**THEN** se comporta exactamente igual que antes de esta corrección

### Scenario: Las tarjetas de tipo de módulo no conservan estilos heredados de un contenido que ya no muestran

**GIVEN** el selector de tipo de módulo, con sus tres tarjetas mostrando cada una una imagen
**WHEN** se revisa el estilo declarado para esas tarjetas
**THEN** no aparece ninguna declaración que solo tenía sentido cuando la tarjeta mostraba una
letra

### Scenario: El alcance del ajuste de layout de las tarjetas queda a la vista

**GIVEN** el ajuste de layout compartido por las tres tarjetas de tipo de módulo
**WHEN** alguien revisa qué tarjetas cambian de aspecto por ese ajuste
**THEN** encuentra constancia explícita de que la tarjeta del manual también cambia, sin que
haga falta inferirlo leyendo el código de otro componente

## Acceptance Criteria

- [x] El control que abre el selector de mes/año del calendario de día y el del selector de
  rango tienen, cada uno, una regla de foco propia con la especificidad necesaria para no
  perder contra la regla de foco de la librería del calendario. **Verificado**: por lectura
  del CSS instalado de la librería (`node_modules/v-calendar/dist/style.css:1264-1266`,
  especificidad (0,2,0), sin `focus-visible` propia) y cálculo de especificidad de la regla
  agregada (`.dark-calendar .vc-title:focus-visible`, (0,3,0)); confirmado además en
  `dist/css/history.*.css` tras `npm run build`.
- [ ] Recorrer con Tab el calendario de día y el selector de rango en la ventana de historial
  muestra el indicador de foco sobre el control de mes/año. **No verificable en esta fase**:
  exige `npm run electron:serve`, no ejecutable en este WSL2 (Node v24.15.0 instalado contra
  16.20.2 de `.nvmrc`). Diferido al recorrido manual en Windows.
- [x] El campo de edición y el control de quitar de una sesión de Pomodoro usan, en el estado
  de sesión completada, un color de indicador de foco que se distingue del fondo de ese
  estado. **Verificado**: por lectura de CSS y cálculo de contraste WCAG — `outline-color:
  #6f6f6f` da 3.36:1 sobre el fondo `#d3d3d3` de una sesión completada y 4.18:1 sobre el
  `black` por defecto de una pendiente, ambos ≥ 3:1.
- [ ] Dar foco con teclado al campo de edición o al control de quitar de una sesión completada
  muestra, a simple vista, un indicador de foco perceptible. **No verificable en esta fase**:
  exige la app corriendo. Diferido al recorrido manual en Windows.
- [x] Las declaraciones de estilo sin efecto visible sobre las tarjetas de tipo de módulo ya
  no están en el código. **Verificado**: por lectura directa del archivo — las cuatro
  declaraciones (`font-size`, `text-align`, los dos `color`) ya no están en
  `TitleBar.vue`.
- [x] El ajuste de layout compartido por las tarjetas de tipo de módulo deja constancia, en el
  propio código, de que también alcanza a la tarjeta del manual. **Verificado**: por lectura
  directa del archivo — comentario agregado junto al `display: flex` de `.option-card`.

## Notas de verificación

**I-1**: la regla agregada gana por especificidad sola —(0,3,0) contra el máximo (0,2,0) de
la hoja de v-calendar—, sin depender del orden de inyección entre `chunk-vendors.css` e
`history.css`. Verificado además que ese orden real en producción (`dist/history.html`:
vendors antes que `history.css`) también favorece la regla del proyecto, por si la
especificidad hubiera empatado. El recorrido con teclado real queda diferido a Windows
(`verify-report.md § Límite de entorno`).

**I-2**: el ejemplo de corrección de `judgment-report.md` (`outline-color: #1b1b1b`) no se
adoptó tal cual — da 11.51:1 sobre `#d3d3d3` pero solo 1.22:1 sobre el fondo `black` por
defecto de una sesión pendiente, es decir hubiera resuelto un estado rompiendo el otro. Se
calculó `#6f6f6f` porque cumple ≥ 3:1 (WCAG 2.2 SC 1.4.11) contra los dos fondos sólidos
reales que estos controles pueden tener detrás (el "degradado" de `getFillStyle()` es en
realidad un corte sólido entre `#d3d3d3` y `black`, sin mezcla intermedia). Detalle completo
del cálculo en `observations.md` (entrada `sdd-apply` de esta fecha).

**S-1 / S-2**: verificación directa por lectura de `TitleBar.vue`, sin depender del render.

Sin test runner en el proyecto: la verificación es estática, como en el resto del cambio.
`npm run lint -- --no-fix` → 0 errores, 1 warning preexistente
(`vue/no-deprecated-destroyed-lifecycle`, `CronometroManual.vue:76`, fuera de alcance).

## Observations

**Origen**: `sdd-judgment` escaló en su segunda iteración (el máximo que el protocolo admite)
con el hallazgo C-1 confirmado por los dos jueces —cada uno sobre una instancia distinta— más
dos hallazgos suspect `low` de un solo juez. El usuario, con el reporte completo en mano,
eligió corregir las cuatro cosas y cerrar. Detalle íntegro, con cadenas de verificación por
triage, en `changes/ui-branding-polish/judgment-report.md § Hallazgos Confirmados` y
`§ Hallazgos Suspect`.

**I-1 — cadena técnica**: `v-calendar@3.1.2` declara, a nivel superior de su hoja de estilos
instalada, `.vc-container:focus, .vc-container *:focus { outline: none }` con especificidad
(0,2,0), que le gana a la regla `:focus-visible` de `tokens.css` (0,1,0). Dentro del
calendario solo quedan cubiertos los elementos que la librería marca con su propia clase de
foco (flechas, celdas de día, ítems del popover de navegación, el `<select>` interno); el
botón que abre el selector de mes/año (`class: "vc-title"` en el código instalado de la
librería) no lleva esa clase y no tiene ninguna regla `focus-visible` propia. Las dos
instancias del control —el calendario de día y el `v-date-picker` de la pestaña "Rango"—
comparten la clase `dark-calendar` que `HistoryView.vue` ya les aplica (líneas 11 y 30), así
que la corrección puede vivir en el `<style>` ya existente de ese componente, acotada a esa
clase, sin tocar la hoja de la librería. Dirección de corrección sugerida por el triage: una
regla `.dark-calendar .vc-title:focus-visible { box-shadow: 0 0 0 2px var(--focus-ring) }` en
el mismo bloque donde ya vive `.vc-focus:focus`.

**I-2 — cadena técnica**: `CronometroPomodoro.vue` usa el anillo global (`--focus-ring:
#e0e0e0` en `tokens.css`) con `outline-offset: 2px`, dibujado fuera del control, sobre el
fondo de `.session-item`. `getFillStyle(index)` pinta ese fondo con `#d3d3d3` para una sesión
ya completada (y con un gradiente que llega a `#d3d3d3` para la sesión en curso). El
resultado, calculado sobre esos dos valores literales, es 1.13:1 — contra el umbral de 3:1 de
WCAG 2.2 SC 1.4.11 que `design.md § D-2.3` ya adopta como criterio para los grises del
proyecto. Dirección de corrección sugerida por el triage: acotar el color del anillo en este
componente (por ejemplo, un `outline-color` más oscuro sobre `.edit-input:focus-visible` y
`.remove-btn:focus-visible`), sin tocar el token compartido — el color del anillo en el resto
de la aplicación no cambia.

**S-1 — declaraciones muertas**: `TitleBar.vue` conserva cuatro declaraciones sin efecto desde
que sus tres tarjetas de tipo de módulo muestran una imagen en vez de una letra: tamaño de
fuente y alineación de texto en `.option-card`, color de texto en `.option-card:hover`, y
color de texto en `.option-card.selected`. Ninguna tiene efecto visible hoy: el estado se
comunica por `border-color` (hover) y `background` (selected).

**S-2 — alcance del ajuste de layout**: el `display: flex` con centrado que este cambio
agregó a `.option-card` alcanza a las tres tarjetas, incluida la del manual, cuya imagen pasa
de alinearse a la línea base a centrarse en la caja de 24×24. Es un cambio de presentación
menor y aceptado como mejora. Lo que corrige este punto es la evidencia: el cuarto criterio de
`module-icons-for-work-and-pomodoro` se verificó con `git diff --stat` sobre
`CronometroManual.vue` y `Menu.vue`, ninguno de los cuales contiene la tarjeta del manual —esa
tarjeta vive en `TitleBar.vue`—. El criterio sigue siendo literalmente cierto (Manual no
estrena ningún ícono nuevo), pero sin una constancia explícita del alcance ampliado, quien
recorra el guion manual en Windows podría leer el cambio de render de esa tarjeta como una
sorpresa en vez de una consecuencia ya conocida y aceptada del ajuste de layout.

**Por qué `adrs[]` lista solo ADR-0015, no ADR-0012**: ADR-0015 documenta, como trade-off ya
aceptado, que "dentro del calendario manda el indicador propio de la librería" por cascada de
especificidad — I-1 demuestra que esa cobertura no alcanza a `.vc-title` específicamente, sin
que el ADR quede falso: sigue describiendo correctamente la mecánica de cascada, solo no
anticipaba que la librería no le da indicador propio a *todos* sus controles. Es el ADR que
gobierna cómo cruza una constante de presentación entre los dos bundles, y esta corrección
vive enteramente dentro de esa frontera ya decidida. ADR-0012 gobierna cómo cruza el *dato* de
preferencia (IPC, sin Pinia) entre bundles; ninguna de las dos correcciones de comportamiento
introduce IPC, store ni dependencia nueva en el bundle de historial — es CSS puro dentro de un
`<style>` que `HistoryView.vue` ya tiene. Por eso no se incluye.

**Limitación de entorno**: este WSL2 no renderiza la app — único Node instalado v24.15.0
contra el 16.20.2 de `.nvmrc`, `npm run electron:serve` no corre. Los dos acceptance criteria
que exigen navegación real con teclado quedan diferidos al recorrido manual en el entorno
Windows ya montado, igual que el resto del guion manual de este cambio
(`verify-report.md § Límite de entorno`). Lo verificable en esta fase es análisis estático —
cascada CSS, especificidad, y los valores de color literales en el código—, el mismo tipo de
evidencia con la que `sdd-judgment` estableció el hallazgo C-1 como confirmado (no por falta
de verificación en vivo).

**Exclusiones de `proposal.md § Scope` respetadas**: esta corrección no migra los hex ya
hardcodeados a tokens, no deduplica los bloques `.modal-overlay`/`.modal-content`, no toca
`vue.config.js` y no iconifica `Menu.vue`. Los tres archivos de `scope[]` no requieren ninguna
de esas cuatro cosas para resolver I-1, I-2, S-1 o S-2.

## Related

- [[keyboard-focus-indicator-per-palette]] — spec original que esta corrección extiende; el
  mecanismo global de foco (navegación por teclado, excepciones ya documentadas, y el resto de
  los controles ya cubiertos) sigue vigente sin cambios
- [[shared-accent-colors-across-windows]] — provee el color compartido (`--focus-ring`) que
  I-1 e I-2 reutilizan; ninguna de las dos correcciones introduce un color nuevo
