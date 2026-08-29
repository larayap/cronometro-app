---
type: capability-spec
title: "Toda la superficie del bloque de agrupar acepta el arrastre, no solo una franja angosta"
capability: "session-groups"
slug: "full-surface-drop-target-for-grouping"
domain: "feature"
delta_type: MODIFY
supersedes: "[[group-composition-and-drag]]"
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: high
depends_on: []
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["78ac4c4", "d7567cf"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "Soltar una fila sobre cualquier punto visible del bloque de agrupar de un grupo nuevo —incluido el texto de la invitación a agrupar— la incorpora al grupo"
  - "Soltar una fila sobre cualquier punto visible de un grupo ya existente —incluida su cabecera con nombre— la suma al grupo"
  - "El reloj individual, la entrada de historial independiente y el total sumado de cada grupo siguen comportándose igual que antes de esta corrección"
related: ["[[group-composition-and-drag]]"]
affects: []
adrs: ["[[0008-sessions-and-groups-as-entry-metadata]]"]
scope: ["src/components/CronometroAplicacion.vue"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Toda la superficie del bloque de agrupar acepta el arrastre, no solo una franja angosta

## Purpose

Arrastrar una fila hacia el bloque de agrupar —sea un grupo nuevo o uno que ya existe— hoy
solo se reconoce cuando el cursor pasa sobre una franja angosta puntual dentro del bloque,
aunque visualmente todo el bloque se vea como una sola zona de destino. Esta spec corrige
esa mecánica: cualquier punto dentro del bloque visible de agrupar acepta el arrastre, sin
exigir que el usuario apunte a un área más chica que la que ve.

## Requirements

- El sistema SHALL reconocer el arrastre de una fila como una acción de agrupar en cualquier
  punto de la superficie visible del bloque de agrupar, tanto para un grupo nuevo como para
  uno ya existente.
- El sistema SHALL NOT exigir que el cursor pase sobre un texto o una franja puntual dentro
  del bloque para que el arrastre se reconozca: toda la superficie visible del bloque cuenta
  como destino válido.
- El sistema SHALL mantener sin cambios el resto del comportamiento de agrupar ya
  establecido: cada fila conserva su propio reloj y su propia entrada de historial, y el
  total del grupo sigue siendo la suma de sus filas.

## Scenarios

### Scenario: Soltar sobre cualquier parte del bloque de un grupo nuevo agrupa la fila

**GIVEN** dos o más filas sueltas en el listado visible
**WHEN** el usuario arrastra una de ellas y la suelta sobre cualquier punto visible del
bloque de agrupar, incluido su título
**THEN** esa fila pasa a formar parte de un grupo nuevo

### Scenario: Soltar sobre cualquier parte de un grupo existente agrupa la fila

**GIVEN** un grupo ya existente con al menos una fila
**WHEN** el usuario arrastra otra fila suelta y la suelta sobre cualquier punto visible de
ese grupo, incluida su cabecera con nombre
**THEN** esa fila se suma al grupo

### Scenario: El resto del comportamiento de agrupar no cambia

**GIVEN** dos filas ya agrupadas
**WHEN** el usuario consulta su reloj individual, su entrada de historial y el total del
grupo
**THEN** los tres se comportan exactamente igual que antes de esta corrección

## Acceptance Criteria

- [ ] Soltar una fila sobre cualquier punto visible del bloque de agrupar de un grupo nuevo
  —incluido el texto de la invitación a agrupar— la incorpora al grupo. **No verificado en
  esta fase**: `.group-strip` se movió al slot `#header` del `<draggable>` de `dragNewGroup`
  (confirmado por grep y por el análisis de `vuedraggable` en `design.md § D-6.5` — el header
  no lleva `data-draggable`), pero el arrastre real con mouse exige `npm run electron:serve`
  (Tarea 8.1b, `[manual]`), no ejecutable en este WSL2.
- [ ] Soltar una fila sobre cualquier punto visible de un grupo ya existente —incluida su
  cabecera con nombre— la suma al grupo. **No verificado en esta fase**, misma razón
  (Tarea 8.2b, `[manual]`).
- [ ] El reloj individual, la entrada de historial independiente y el total sumado de cada
  grupo siguen comportándose igual que antes de esta corrección. **No verificado en esta
  fase**: por lectura de código, ningún handler, guarda de arrastre ni camino de IPC se tocó
  (el cambio es exclusivamente de plantilla, D-6.6), pero la confirmación en vivo de los
  cuatro flujos de arrastre es responsabilidad de la Tarea 8.3 (`[manual]`).

## Related

- [[group-composition-and-drag]] — spec original que esta corrección extiende; el resto de
  la mecánica de agrupar (relojes independientes, totales, extinción del grupo vacío) sigue
  vigente sin cambios
