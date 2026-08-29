---
type: capability-spec
title: "Pestaña Agregadas: revisar y quitar la selección guardada sin recorrer el listado completo"
capability: "app-installed-selector"
slug: "added-apps-review-tab"
domain: "feature"
delta_type: null
supersedes: null
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: medium
depends_on: ["[[deselect-from-saved-selection]]"]
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["1c8d4a8"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "Abrir la tercera vista del selector, con aplicaciones ya registradas, muestra únicamente esas aplicaciones"
  - "Escribir texto de búsqueda dentro de esta vista acota el listado igual que en las otras dos vistas del selector"
  - "Hacer click sobre una entrada de esta vista la quita de la selección guardada"
  - "Quitar la última aplicación registrada desde esta vista deja un mensaje explícito visible, sin cerrar el selector ni cambiar de vista"
  - "Abrir esta vista sin ninguna aplicación registrada todavía muestra el mismo mensaje explícito"
related: ["[[installed-apps-data-integrity]]", "[[selection-type-manual-vs-auto]]"]
affects: []
adrs: []
scope: ["src/components/AppSelectorModal.vue", "src/stores/monitoredApps.js"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Pestaña Agregadas: revisar y quitar la selección guardada sin recorrer el listado completo

## Purpose

Revisar qué aplicaciones ya están registradas hoy exige recorrer visualmente todo el listado
de instaladas buscando la marca de seleccionado. Esta spec agrega una tercera vista dentro
del mismo selector que muestra únicamente lo ya registrado, para que confirmar la selección
actual no dependa de examinar un listado de hasta un centenar de entradas.

## Requirements

- El sistema SHALL ofrecer, junto a las vistas de instaladas y de procesos abiertos del
  mismo selector, una tercera vista que muestra únicamente las aplicaciones que ya forman
  parte de la selección guardada.
- El sistema SHALL permitir al usuario acotar esa tercera vista escribiendo texto de
  búsqueda, de la misma manera que en las otras dos vistas del selector.
- El sistema SHALL quitar de la selección guardada, con el mismo efecto que la acción de
  desmarcar del selector, cualquier aplicación sobre la que el usuario haga click dentro de
  esta vista.
- El sistema SHALL mostrar un mensaje explícito cuando esta vista no tiene ninguna
  aplicación para mostrar, en vez de un espacio en blanco sin explicación.
- El sistema SHALL permanecer en esta misma vista, sin cerrar el selector ni cambiar de vista
  automáticamente, cuando el usuario quita la última aplicación registrada desde aquí.

## Scenarios

### Scenario: La vista muestra solo lo ya registrado

**GIVEN** una selección guardada con algunas aplicaciones ya registradas, dentro de un
listado de instaladas mucho más largo
**WHEN** el usuario abre la tercera vista del selector
**THEN** ve únicamente las aplicaciones ya registradas, sin el resto del listado de
instaladas

### Scenario: El buscador filtra también esta vista

**GIVEN** la tercera vista abierta con varias aplicaciones registradas
**WHEN** el usuario escribe texto de búsqueda
**THEN** la vista se acota a las aplicaciones registradas que coinciden con ese texto

### Scenario: Hacer click sobre una entrada la quita de la selección

**GIVEN** la tercera vista abierta con una aplicación registrada
**WHEN** el usuario hace click sobre esa entrada
**THEN** la aplicación deja de estar en la selección guardada y desaparece de esta vista

### Scenario: Quitar la última aplicación deja la vista vacía con un mensaje

**GIVEN** la tercera vista con una única aplicación registrada
**WHEN** el usuario la quita haciendo click sobre ella
**THEN** la vista queda sin ninguna entrada y muestra un mensaje explícito indicando que no
hay aplicaciones registradas, sin cerrar el selector ni cambiar a otra vista

### Scenario: Abrir la vista sin ninguna aplicación registrada todavía

**GIVEN** una selección guardada vacía
**WHEN** el usuario abre la tercera vista del selector
**THEN** ve el mismo mensaje explícito de que no hay aplicaciones registradas

## Acceptance Criteria

- [ ] Abrir la tercera vista del selector, con aplicaciones ya registradas, muestra
  únicamente esas aplicaciones. **No verificado en esta fase**: el computed `addedApps`
  filtra `monitoredApps.selection` (confirmado por lectura de código), pero ver el resultado
  renderizado exige abrir la app real (Tarea 4.4, `[manual]`), no ejecutable en este WSL2.
- [ ] Escribir texto de búsqueda dentro de esta vista acota el listado igual que en las otras
  dos vistas del selector. **No verificado en esta fase**, misma razón (Tarea 4.4, `[manual]`).
- [ ] Hacer click sobre una entrada de esta vista la quita de la selección guardada. **No
  verificado en esta fase**: `choose()` no se modificó y su guard (`isSelected` antes de
  `limitReached`) ya cubre este camino por diseño (D-3.5), pero confirmar el clic real
  requiere el mismo recorrido manual.
- [ ] Quitar la última aplicación registrada desde esta vista deja un mensaje explícito
  visible, sin cerrar el selector ni cambiar de vista. **No verificado en esta fase**, misma
  razón (Tarea 4.4, `[manual]`).
- [ ] Abrir esta vista sin ninguna aplicación registrada todavía muestra el mismo mensaje
  explícito. **No verificado en esta fase**, misma razón (Tarea 4.4, `[manual]`).

## Related

- [[deselect-from-saved-selection]] — provee la acción de quitar que esta vista reutiliza
  sobre cada entrada
- [[installed-apps-data-integrity]] — gobierna la calidad de los datos del mismo selector
  donde vive esta vista
- [[selection-type-manual-vs-auto]] — las entradas que esta vista muestra pueden ser de
  cualquiera de las dos modalidades, sin distinción especial
