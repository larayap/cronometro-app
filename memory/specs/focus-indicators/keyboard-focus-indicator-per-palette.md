---
type: capability-spec
title: "Indicador de foco acorde a la paleta, visible al navegar con teclado"
capability: "focus-indicators"
slug: "keyboard-focus-indicator-per-palette"
domain: "feature"
delta_type: null
supersedes: null
superseded_by: "[[judgment-fixes-ui-branding-polish-round2]]"
status: review
assigned_agent: "sdd-apply"
priority: high
depends_on: ["[[shared-accent-colors-across-windows]]"]
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["4053574"]
mr: ""
acceptance_criteria:
  - "Recorrer con Tab cada control interactivo de la ventana de trabajo y de la ventana de historial muestra, en todos los casos, un indicador de foco visible acorde a la paleta oscura"
  - "Hacer click con el mouse sobre esos mismos controles no muestra el indicador de foco"
  - "El diálogo de la barra de la ventana que se navega con flechas de teclado muestra el indicador de foco sobre el elemento activo"
  - "Ningún control de la aplicación queda sin ninguna señal visual de foco al navegar con el teclado"
related: ["[[shared-accent-colors-across-windows]]"]
affects: []
adrs: []
scope: ["src/components/AppSelectorModal.vue", "src/components/OpcionesPanel.vue", "src/components/CronometroAplicacion.vue", "src/components/CronometroPomodoro.vue", "src/components/CronometroManual.vue", "src/components/AppRow.vue", "src/components/TitleBar.vue", "src/components/Menu.vue", "src/history/HistoryView.vue", "src/history/TitleBar.vue"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Indicador de foco acorde a la paleta, visible al navegar con teclado

## Purpose

El indicador de foco que hoy ve el usuario en varios controles es el anillo amarillo/dorado
por defecto del sistema operativo, ajeno a la paleta oscura del resto de la interfaz, y
varios controles lo suprimen sin ningún reemplazo. Uno de esos controles suprimidos es,
además, un diálogo que se opera activamente con las flechas del teclado —una regresión de
accesibilidad ya presente hoy—. Esta spec reemplaza todo indicador de foco nativo o
suprimido por uno consistente con la paleta oscura, y hace que aparezca específicamente
cuando el usuario navega con el teclado, no cuando activa un control con el mouse.

## Requirements

- El sistema SHALL mostrar un indicador de foco visible, acorde a la paleta oscura de la
  aplicación, en todo control que pueda recibir el foco del teclado —incluidos botones,
  campos de texto, listas desplegables, controles deslizantes y diálogos que se navegan con
  las flechas del teclado.
- El sistema SHALL NOT dejar ningún control sin ningún indicador de foco: todo control que
  hoy suprime el indicador nativo sin reemplazo pasa a mostrar el indicador de la paleta.
- El sistema SHALL mostrar el indicador de foco únicamente cuando el usuario navega con el
  teclado, no cuando activa el control con el mouse.
- El sistema SHALL mantener el indicador de foco perceptible mientras el control lo conserve,
  sin que desaparezca antes de que el usuario mueva el foco a otro control.

## Scenarios

### Scenario: Navegar con teclado muestra el indicador de la paleta

**GIVEN** cualquier control interactivo de la aplicación
**WHEN** el usuario le da el foco presionando Tab
**THEN** el control muestra un indicador de foco visible, con un color acorde a la paleta
oscura

### Scenario: Hacer click no muestra el indicador

**GIVEN** cualquier control interactivo de la aplicación
**WHEN** el usuario lo activa haciendo click con el mouse
**THEN** el control no muestra el indicador de foco

### Scenario: Un diálogo navegado con flechas conserva el indicador

**GIVEN** un diálogo de la barra de la ventana que se recorre con las flechas del teclado
**WHEN** el usuario lo abre y navega con el teclado
**THEN** el elemento con el foco muestra el indicador de la paleta, sin quedar sin ninguna
señal visual de dónde está el foco

### Scenario: Ningún control queda sin indicador

**GIVEN** cualquier control de la aplicación que antes de este cambio no mostraba ningún
indicador de foco al navegar con teclado
**WHEN** el usuario le da el foco con el teclado
**THEN** el control muestra el indicador de la paleta en vez de quedar sin ninguna señal
visual

## Acceptance Criteria

- [ ] Recorrer con Tab cada control interactivo de la ventana de trabajo y de la ventana de
  historial muestra, en todos los casos, un indicador de foco visible acorde a la paleta
  oscura. **No verificado en esta fase**: las tres invariantes por `grep` de `design.md § D-1.4`
  pasan (cero `outline: none`, una sola `:focus-visible` en `tokens.css`, dos excepciones
  `:focus` documentadas), pero el recorrido real con teclado exige `npm run electron:serve`
  (Tarea 2.5, `[manual]`), no ejecutable en este WSL2.
- [ ] Hacer click con el mouse sobre esos mismos controles no muestra el indicador de foco.
  **No verificado en esta fase** (Tarea 2.5, `[manual]`).
- [ ] El diálogo de la barra de la ventana que se navega con flechas de teclado muestra el
  indicador de foco sobre el elemento activo. **No verificado en esta fase**: la excepción
  `.modal-content:focus` está agregada en `TitleBar.vue` (D-1.3), pero confirmar que se ve
  sobre el panel real exige el mismo recorrido manual (Tarea 2.5).
- [ ] Ningún control de la aplicación queda sin ninguna señal visual de foco al navegar con
  el teclado. **No verificado en esta fase** (Tarea 2.5, `[manual]`).

## Related

- [[shared-accent-colors-across-windows]] — provee el color compartido que este indicador
  usa en ambas ventanas
