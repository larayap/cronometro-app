---
type: capability-spec
title: "Los colores de acento introducidos por este cambio se ven igual en ambas ventanas"
capability: "design-tokens"
slug: "shared-accent-colors-across-windows"
domain: "feature"
delta_type: null
supersedes: null
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: medium
depends_on: []
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["75f204b"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "El color del indicador de foco se ve igual en la ventana de trabajo y en la ventana de historial"
  - "La ventana de historial, abierta por separado, muestra sus acentos de color sin depender de que la ventana de trabajo esté abierta"
related: ["[[keyboard-focus-indicator-per-palette]]", "[[range-selection-grayscale-palette]]", "[[judgment-fixes-ui-branding-polish-round2]]"]
affects: ["[[keyboard-focus-indicator-per-palette]]", "[[range-selection-grayscale-palette]]", "[[judgment-fixes-ui-branding-polish-round2]]"]
adrs: ["[[0012-history-window-reads-preferences-over-ipc-without-pinia]]"]
scope: ["src/styles/tokens.css", "src/main.js", "src/history/main.js"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Los colores de acento introducidos por este cambio se ven igual en ambas ventanas

## Purpose

La aplicación funciona con dos ventanas independientes —la ventana de trabajo y la ventana
de historial— que hoy no comparten ningún color declarado en un solo lugar: cada componente
define sus propios tonos por separado. Esta spec asegura que los colores de acento que este
cambio introduce (el indicador de foco y el resaltado de rango del calendario) se vean
exactamente igual sin importar en cuál de las dos ventanas aparezcan, para que ajustar el
tono en el futuro no dependa de recordar tocar cada componente por separado.

## Requirements

- El sistema SHALL mostrar el mismo color para cada acento visual que este cambio introduce,
  sin importar en cuál de las dos ventanas de la aplicación aparezca.
- El sistema SHALL mantener disponible cada acento introducido por este cambio en la ventana
  de historial, tanto como en la ventana de trabajo, sin que la falta de un estado
  compartido entre ambas ventanas le impida mostrarlo.
- El sistema SHOULD permitir cambiar el tono de un acento introducido por este cambio en un
  único lugar y ver el resultado reflejado en ambas ventanas.

## Scenarios

### Scenario: El color de foco es igual en ambas ventanas

**GIVEN** un control con indicador de foco visible en la ventana de trabajo y otro en la
ventana de historial
**WHEN** el usuario navega a cada uno con el teclado
**THEN** el color del indicador se ve idéntico en ambas ventanas

### Scenario: La ventana de historial muestra sus acentos sin depender de la ventana de trabajo

**GIVEN** la ventana de historial abierta de forma independiente, sin que la ventana de
trabajo esté necesariamente abierta
**WHEN** el usuario observa el color de foco o el resaltado del calendario
**THEN** ambos se muestran con el color esperado, sin quedar en un color por defecto distinto
ni sin color

## Acceptance Criteria

- [ ] El color del indicador de foco se ve igual en la ventana de trabajo y en la ventana de
  historial. **No verificado en esta fase**: `src/styles/tokens.css` existe con los cuatro
  tokens y se importa primero en `src/main.js` y en `src/history/main.js` (mecanismo
  determinístico: las custom properties de `:root` se heredan en ambos bundles), pero la
  confirmación visual con las dos ventanas abiertas exige `npm run electron:serve`
  (Tarea 1.3, `[manual]`), no ejecutable en este WSL2.
- [ ] La ventana de historial, abierta por separado, muestra sus acentos de color sin
  depender de que la ventana de trabajo esté abierta. **No verificado en esta fase**, misma
  razón (Tarea 1.3, `[manual]`).

## Related

- [[keyboard-focus-indicator-per-palette]] — consume este color compartido para el indicador
  de foco
- [[range-selection-grayscale-palette]] — consume este color compartido para el resaltado de
  rango del calendario
- [[judgment-fixes-ui-branding-polish-round2]] — corrección de judgment sobre el indicador de
  foco; reutiliza el mismo color compartido, sin introducir ninguno nuevo
