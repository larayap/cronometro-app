---
type: capability-spec
title: "El rótulo del módulo de trabajo dentro de la interfaz usa el nombre del producto"
capability: "project-identity"
slug: "in-app-module-label-matches-product-name"
domain: "feature"
delta_type: ADD
supersedes: "[[unified-product-identity]]"
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: medium
depends_on: []
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["6dc14b1"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "El encabezado del módulo de trabajo muestra el nombre completo del producto"
  - "El encabezado de la ventana de historial no cambia respecto a su texto actual"
related: ["[[unified-product-identity]]"]
affects: []
adrs: []
scope: ["src/components/CronometroAplicacion.vue"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# El rótulo del módulo de trabajo dentro de la interfaz usa el nombre del producto

## Purpose

La identidad del producto ya es consistente en el instalador, el acceso directo, el título
de la ventana y el paquete distribuible bajo el nombre completo del producto. Dentro de la
propia interfaz, sin embargo, el encabezado del módulo de trabajo todavía muestra el rótulo
corto anterior. Esta spec extiende esa consistencia al encabezado visible dentro de la
ventana de trabajo, dejando fuera de forma explícita una segunda ocurrencia del mismo texto
corto en el historial, donde la palabra tiene un significado distinto (horas trabajadas, no
rótulo de módulo).

## Requirements

- El sistema SHALL mostrar el encabezado del módulo de trabajo, dentro de la ventana de la
  aplicación, con el nombre completo del producto.
- El sistema SHALL NOT modificar el encabezado de la ventana de historial que usa el rótulo
  corto anterior con el sentido de horas trabajadas, no como rótulo de módulo.

## Scenarios

### Scenario: El encabezado del módulo de trabajo muestra el nombre completo

**GIVEN** el módulo de trabajo abierto
**WHEN** el usuario mira su encabezado
**THEN** ve el nombre completo del producto en vez del rótulo corto anterior

### Scenario: El encabezado del historial no cambia

**GIVEN** la ventana de historial abierta
**WHEN** el usuario mira su encabezado
**THEN** sigue mostrando el mismo texto de antes, sin el nombre completo del producto

## Acceptance Criteria

- [x] El encabezado del módulo de trabajo muestra el nombre completo del producto.
  Verificado: `grep -n "Work Tracker" src/components/CronometroAplicacion.vue` matchea
  dentro del `<h1 class="module-title">`, y `grep -n ">Work<"` ya no matchea.
- [x] El encabezado de la ventana de historial no cambia respecto a su texto actual.
  Verificado: `src/history/HistoryView.vue:5` (`"Days of Work"`) queda byte-idéntico —
  `git diff` sobre esa línea específica está vacío.

## Related

- [[unified-product-identity]] — esta spec extiende la consistencia de nombre que esa spec
  ya exige al instalador, al acceso directo y al título de ventana, cubriendo ahora también
  el encabezado visible dentro de la propia interfaz
