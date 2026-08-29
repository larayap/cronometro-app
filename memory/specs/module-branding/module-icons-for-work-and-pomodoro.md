---
type: capability-spec
title: "Los módulos Work Tracker y Pomodoro muestran su propio ícono"
capability: "module-branding"
slug: "module-icons-for-work-and-pomodoro"
domain: "feature"
delta_type: null
supersedes: null
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: low
depends_on: []
change_ref: "[[ui-branding-polish]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/ui-branding-polish"
feature_branch: "feature/ui-branding-polish"
commits: ["6dc14b1", "7402018"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "El selector de widgets de la barra de la ventana principal muestra un ícono propio para el módulo de trabajo y otro para el módulo Pomodoro, en vez de las letras sueltas de hoy"
  - "El encabezado del módulo de trabajo y el del módulo Pomodoro muestran el mismo ícono junto al título"
  - "Ninguno de los dos íconos se ve recortado dentro de su espacio, incluso siendo su arte original no cuadrado"
  - "El widget Manual y la pantalla de selección de widgets no muestran ningún ícono nuevo tras este cambio"
related: ["[[unified-product-identity]]", "[[app-icon-matches-pomodoro-artwork]]"]
affects: []
adrs: []
scope: ["src/components/TitleBar.vue", "src/components/CronometroAplicacion.vue", "src/components/CronometroPomodoro.vue", "src/assets/work_worktracker.webp", "src/assets/pomodoro_worktracker.webp"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Los módulos Work Tracker y Pomodoro muestran su propio ícono

## Purpose

Hoy el módulo de trabajo y el módulo Pomodoro se identifican en la interfaz solo con una
letra o con texto plano, sin ningún ícono propio. Esta spec les da a ambos un ícono
reconocible, en los mismos lugares donde el módulo Manual ya usa una imagen en vez de una
letra, sin recortar el arte original para que quepa en un espacio cuadrado.

## Requirements

- El sistema SHALL mostrar un ícono propio para el módulo de trabajo y otro para el módulo
  Pomodoro, en el selector de widgets de la barra de la ventana principal, en el mismo lugar
  donde hoy se muestra una letra suelta.
- El sistema SHALL mostrar el mismo ícono junto al encabezado de cada uno de esos dos
  módulos.
- El sistema SHALL encuadrar cada ícono dentro de su espacio disponible sin recortar ninguna
  parte del arte original, aceptando que el ícono se vea más pequeño que uno ya cuadrado
  antes que perder contenido de la imagen.
- El sistema SHALL NOT introducir un ícono para el widget Manual ni para la pantalla de
  selección de widgets: ambos mantienen su presentación actual sin cambios.

## Scenarios

### Scenario: El selector de widgets muestra los íconos nuevos

**GIVEN** la barra de la ventana principal con el selector de widgets visible
**WHEN** el usuario lo mira
**THEN** la tarjeta del módulo de trabajo y la del módulo Pomodoro muestran cada una su
propio ícono en vez de una letra suelta

### Scenario: El encabezado de cada módulo muestra su ícono

**GIVEN** el módulo de trabajo o el módulo Pomodoro abierto
**WHEN** el usuario mira su encabezado
**THEN** el ícono del módulo aparece junto al título

### Scenario: El ícono no recorta el arte original

**GIVEN** un ícono cuya imagen de origen no es cuadrada
**WHEN** se muestra en un espacio cuadrado de la interfaz
**THEN** se ve completo dentro de ese espacio, sin ninguna parte cortada, aunque se vea más
pequeño que un ícono ya cuadrado

### Scenario: El widget Manual y la pantalla de selección no cambian

**GIVEN** el widget Manual y la pantalla "Inicio" de selección de widgets
**WHEN** el usuario los mira tras este cambio
**THEN** siguen mostrando su presentación actual, sin ningún ícono nuevo

## Acceptance Criteria

- [ ] El selector de widgets de la barra de la ventana principal muestra un ícono propio
  para el módulo de trabajo y otro para el módulo Pomodoro, en vez de las letras sueltas de
  hoy. **No verificado en esta fase**: confirmado por grep que las letras `W`/`P` desaparecen
  y los `<img>` con `src`/`alt` correctos están en su lugar, pero ver el resultado renderizado
  exige `npm run electron:serve` (Tarea 5.4, `[manual]`), no ejecutable en este WSL2.
- [ ] El encabezado del módulo de trabajo y el del módulo Pomodoro muestran el mismo ícono
  junto al título. **No verificado en esta fase**, misma razón (Tarea 5.4, `[manual]`).
- [ ] Ninguno de los dos íconos se ve recortado dentro de su espacio, incluso siendo su arte
  original no cuadrado. **No verificado en esta fase**: `object-fit: contain` está aplicado
  en `.option-icon`/`.module-icon` en los tres archivos, pero la confirmación de que se ve
  "comparable" al de Manual es un juicio visual (Tarea 5.4, `[manual]`).
- [x] El widget Manual y la pantalla de selección de widgets no muestran ningún ícono nuevo
  tras este cambio. Verificado: `git diff --stat` sobre `CronometroManual.vue` y `Menu.vue`
  no muestra ningún cambio.

## Related

- [[unified-product-identity]] — comparte el propósito de presentar el producto y sus
  módulos de forma reconocible
- [[app-icon-matches-pomodoro-artwork]] — usa el arte hermano de Pomodoro para el ícono de la
  aplicación a nivel de sistema operativo, mientras esta spec lo usa dentro de la interfaz
