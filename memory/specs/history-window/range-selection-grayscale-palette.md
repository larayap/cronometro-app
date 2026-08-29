---
type: capability-spec
title: "El rango seleccionado del calendario se muestra en escala de grises"
capability: "history-window"
slug: "range-selection-grayscale-palette"
domain: "feature"
delta_type: null
supersedes: null
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: low
depends_on: ["[[shared-accent-colors-across-windows]]"]
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["9e3e5ab"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "Seleccionar un rango de fechas en el historial muestra ambos extremos del rango en tonos de gris/blanco/negro, sin azul"
  - "Los días intermedios de ese rango se muestran en tonos de gris consistentes con los extremos"
  - "El día puntual seleccionado en el calendario de día conserva su apariencia gris actual, sin cambios"
related: ["[[shared-accent-colors-across-windows]]", "[[usage-chart-by-interval]]"]
affects: []
adrs: []
scope: ["src/history/HistoryView.vue"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# El rango seleccionado del calendario se muestra en escala de grises

## Purpose

Al elegir un rango de fechas en el calendario del historial, los extremos y los días
intermedios del rango se resaltan hoy en azul, el único color de acento del calendario que no
sigue la paleta oscura del resto de la ventana. El día puntual seleccionado en el calendario
de día ya se muestra en gris; esta spec extiende ese mismo tratamiento al modo de rango, sin
afectar el resto de la apariencia del calendario.

## Requirements

- El sistema SHALL mostrar los extremos de un rango de fechas seleccionado, y los días
  intermedios de ese rango, en tonos de gris/blanco/negro acordes a la paleta oscura, en vez
  de azul.
- El sistema SHALL mantener sin cambios la apariencia del día puntual seleccionado en el
  calendario de día, que ya sigue esa misma paleta.
- El sistema SHALL NOT modificar ningún otro color del calendario o de la ventana de
  historial fuera del resaltado de rango.

## Scenarios

### Scenario: Elegir un rango muestra sus extremos en gris

**GIVEN** el historial abierto en la pestaña de rango
**WHEN** el usuario elige la fecha de inicio y la fecha de fin de un rango
**THEN** ambos extremos del rango se resaltan en tonos de gris/blanco/negro, sin ningún azul

### Scenario: Los días intermedios del rango también siguen la paleta

**GIVEN** un rango de varios días seleccionado
**WHEN** el usuario mira los días entre el inicio y el fin
**THEN** esos días intermedios se muestran resaltados en tonos de gris, consistentes con los
extremos

### Scenario: El día puntual sigue como está

**GIVEN** el calendario de día con una fecha puntual seleccionada
**WHEN** el usuario la mira
**THEN** se sigue mostrando en el mismo tono de gris que ya tenía, sin cambios

## Acceptance Criteria

- [ ] Seleccionar un rango de fechas en el historial muestra ambos extremos del rango en
  tonos de gris/blanco/negro, sin azul. **No verificado en esta fase**: las cuatro reglas
  nuevas están agregadas en `HistoryView.vue` con los selectores exactos de `design.md § D-2`
  (confirmado por grep: capa de fondo sin `.vc-blue`, capa de contenido con `.vc-blue`), pero
  observar el arrastre real sobre el calendario exige `npm run electron:serve` (Tarea 3.2,
  `[manual]`), no ejecutable en este WSL2.
- [ ] Los días intermedios de ese rango se muestran en tonos de gris consistentes con los
  extremos. **No verificado en esta fase**, misma razón (Tarea 3.2, `[manual]`).
- [ ] El día puntual seleccionado en el calendario de día conserva su apariencia gris actual,
  sin cambios. **No verificado en esta fase**: `git diff` confirma que las dos reglas
  `-solid` preexistentes quedan byte-idénticas (Tarea 3.1), pero la confirmación visual en
  pantalla es parte del mismo recorrido manual de la Tarea 3.2.

## Related

- [[shared-accent-colors-across-windows]] — provee el color de gris compartido que este
  resaltado usa
- [[usage-chart-by-interval]] — el alcance de rango que aquí se resalta visualmente es el
  mismo que ese gráfico agrega
