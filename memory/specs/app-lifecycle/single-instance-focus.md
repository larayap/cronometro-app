---
type: capability-spec
title: "Instancia única: un segundo arranque enfoca la ventana existente"
capability: "app-lifecycle"
slug: "single-instance-focus"
domain: "feature"
delta_type: null
supersedes: null
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: critical
depends_on: []
change_ref: "[[windows-autostart-single-instance]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/windows-autostart-single-instance"
feature_branch: "feature/windows-autostart-single-instance"
commits: ["dec815d"]
mr: "https://github.com/larayap/work-tracker/pull/6"
acceptance_criteria:
  - "La aplicación permite como máximo una instancia corriendo a la vez"
  - "Ejecutar la aplicación mientras ya está corriendo enfoca la ventana de la instancia existente en vez de abrir una segunda"
  - "Ejecutar la aplicación mientras la ventana de la instancia existente está minimizada la restaura y la enfoca"
  - "La instancia que se cierra por encontrar otra ya corriendo no altera el historial de actividad registrado"
related: ["[[judgment-fixes-iteration-1]]", "[[startup-visibility-preference]]", "[[sessions-json-persistence]]"]
affects: []
adrs: ["[[0002-main-process-owns-monitoring-state]]"]
scope: ["src/background.js"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Instancia única: un segundo arranque enfoca la ventana existente

## Purpose

Hoy nada impide que la aplicación se ejecute más de una vez al mismo tiempo: cada ejecución
del instalable abre una instancia nueva, y todas cuentan sobre el mismo historial de
actividad guardado, compitiendo por escribirlo. Esta spec asegura que la aplicación corra
como una única instancia: si ya hay una corriendo, ejecutarla de nuevo no abre una instancia
competidora, sino que trae al frente la ventana de la que ya está en marcha.

## Requirements

- El sistema SHALL permitir como máximo una instancia de la aplicación corriendo a la vez.
- El sistema SHALL, cuando la aplicación se ejecuta mientras ya hay una instancia corriendo,
  traer al frente y enfocar la ventana de esa instancia existente, mostrándola sin importar
  la preferencia de visibilidad al arrancar: es una acción explícita de quien intenta abrir
  la aplicación de nuevo.
- El sistema SHALL restaurar la ventana de la instancia existente si estaba minimizada, antes
  de enfocarla.
- El sistema SHALL cerrar la instancia recién ejecutada sin registrar ninguna actividad ni
  alterar el historial guardado por la instancia que ya estaba corriendo.

## Scenarios

### Scenario: Ejecutar la aplicación mientras ya está corriendo enfoca la ventana existente

**GIVEN** la aplicación ya corriendo, con o sin su ventana visible
**WHEN** la persona vuelve a ejecutar la aplicación
**THEN** no se abre una instancia nueva; la ventana de la instancia que ya estaba corriendo
pasa al frente y queda enfocada

### Scenario: Ejecutar la aplicación mientras la ventana existente está minimizada

**GIVEN** la aplicación ya corriendo con su ventana minimizada
**WHEN** la persona vuelve a ejecutar la aplicación
**THEN** la ventana existente se restaura desde el estado minimizado y queda enfocada al
frente

### Scenario: El segundo arranque no daña el historial de actividad

**GIVEN** la aplicación ya corriendo con actividad en curso siendo registrada
**WHEN** la persona vuelve a ejecutar la aplicación
**THEN** el historial de actividad registrado por la instancia que ya estaba corriendo queda
intacto, sin entradas duplicadas ni perdidas por causa del segundo arranque

## Acceptance Criteria

- [ ] La aplicación permite como máximo una instancia corriendo a la vez.
- [ ] Ejecutar la aplicación mientras ya está corriendo enfoca la ventana de la instancia
  existente en vez de abrir una segunda.
- [ ] Ejecutar la aplicación mientras la ventana de la instancia existente está minimizada la
  restaura y la enfoca.
- [ ] La instancia que se cierra por encontrar otra ya corriendo no altera el historial de
  actividad registrado.

Ningún criterio de esta spec es verificable desde WSL2 (todos requieren dos procesos Electron
reales corriendo a la vez) — diferidos en bloque a `sdd-verify` (W1). Ver
`[[windows-autostart-single-instance/observations]]`.

## Related

- [[judgment-fixes-iteration-1]] — ya establece que la aplicación crea exactamente una
  ventana principal por arranque dentro de un mismo proceso; esta spec extiende esa garantía
  a través de procesos distintos
- [[startup-visibility-preference]] — gobierna la visibilidad en un arranque normal; el
  enfoque ante un segundo arranque es una excepción deliberada que siempre muestra la ventana
- [[sessions-json-persistence]] — establece que salir de la aplicación registra el historial
  de las filas abiertas; esta spec exige que la instancia redundante se cierre sin disparar
  ese registro, para no escribir sobre el historial de la instancia en marcha
