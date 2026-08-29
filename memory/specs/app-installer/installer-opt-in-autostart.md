---
type: capability-spec
title: "Autoarranque con Windows, opt-in desde el instalador"
capability: "app-installer"
slug: "installer-opt-in-autostart"
domain: "feature"
delta_type: null
supersedes: null
superseded_by: null
status: completed
assigned_agent: "sdd-apply"
priority: high
depends_on: []
change_ref: "[[windows-autostart-single-instance]]"
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/windows-autostart-single-instance"
feature_branch: "feature/windows-autostart-single-instance"
commits: ["710767f"]
mr: "https://github.com/larayap/work-tracker/pull/6"
acceptance_criteria:
  - "La instalación limpia ofrece la opción de inicio automático con Windows, sin marcar por defecto"
  - "Marcar la opción al instalar deja la aplicación iniciando automáticamente en el siguiente inicio de sesión de Windows"
  - "No marcar la opción al instalar deja la aplicación sin iniciar automáticamente"
  - "Reinstalar sobre una instalación con el arranque automático activo presenta la opción ya marcada"
  - "Actualizar la aplicación conserva el arranque automático que ya estaba activado"
  - "Desinstalar la aplicación quita el arranque automático, si estaba activado"
related: ["[[startup-visibility-preference]]", "[[unified-product-identity]]"]
affects: []
adrs: []
scope: ["build/installer.nsh", "vue.config.js"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Autoarranque con Windows, opt-in desde el instalador

## Purpose

El instalador no ofrece hoy ninguna forma de que la aplicación se inicie automáticamente al
iniciar sesión en Windows: quien lo desea debe configurarlo por fuera de la aplicación, a
mano. Esta spec agrega, durante la instalación, una opción para registrar el arranque
automático con el inicio de sesión de Windows, con un comportamiento coherente a través de
instalaciones limpias, reinstalaciones, actualizaciones y desinstalaciones.

## Requirements

- El sistema SHALL ofrecer, durante la instalación, una opción para iniciar la aplicación
  automáticamente al iniciar sesión en Windows.
- El sistema SHALL dejar esa opción sin marcar por defecto en una instalación limpia.
- El sistema SHALL, al reinstalar sobre una instalación existente, presentar la opción
  marcada o sin marcar según el estado de arranque automático ya configurado en esa
  instalación.
- El sistema SHALL registrar el arranque automático con Windows cuando la opción queda
  marcada al finalizar la instalación.
- El sistema SHALL NOT dejar registrado ningún arranque automático cuando la opción queda
  sin marcar al finalizar la instalación.
- El sistema SHALL conservar el arranque automático ya configurado a través de una
  actualización de la aplicación a una versión nueva.
- El sistema SHALL quitar el arranque automático registrado cuando la aplicación se
  desinstala, siempre que la desinstalación no sea parte de una actualización.

## Scenarios

### Scenario: Instalación limpia con la opción marcada

**GIVEN** una persona instala la aplicación por primera vez
**WHEN** marca la opción de inicio automático con Windows antes de finalizar la instalación
**THEN** la aplicación queda registrada para iniciar automáticamente la próxima vez que esa
persona inicie sesión en Windows

### Scenario: Instalación limpia sin marcar la opción

**GIVEN** una persona instala la aplicación por primera vez
**WHEN** no marca la opción de inicio automático con Windows
**THEN** la aplicación no inicia automáticamente al iniciar sesión en Windows

### Scenario: Reinstalar conserva el estado ya elegido

**GIVEN** una instalación existente con el arranque automático ya activado
**WHEN** la persona vuelve a ejecutar el instalador sobre esa instalación
**THEN** la opción de inicio automático aparece marcada, reflejando el estado ya configurado

### Scenario: Actualizar la aplicación no apaga el arranque automático

**GIVEN** una instalación existente con el arranque automático activado
**WHEN** la aplicación se actualiza a una versión nueva
**THEN** el arranque automático con Windows sigue activo después de la actualización

### Scenario: Desinstalar la aplicación quita el arranque automático

**GIVEN** una instalación con el arranque automático activado
**WHEN** la persona desinstala la aplicación
**THEN** la aplicación deja de iniciar automáticamente con Windows

## Acceptance Criteria

- [ ] La instalación limpia ofrece la opción de inicio automático con Windows, sin marcar
  por defecto.
- [ ] Marcar la opción al instalar deja la aplicación iniciando automáticamente en el
  siguiente inicio de sesión de Windows.
- [ ] No marcar la opción al instalar deja la aplicación sin iniciar automáticamente.
- [ ] Reinstalar sobre una instalación con el arranque automático activo presenta la opción
  ya marcada.
- [ ] Actualizar la aplicación conserva el arranque automático que ya estaba activado.
- [ ] Desinstalar la aplicación quita el arranque automático, si estaba activado.

Ningún criterio de esta spec es verificable desde WSL2 (todos requieren compilar el
instalador NSIS real e instalar/reinstalar/actualizar/desinstalar en Windows) — diferidos en
bloque a `sdd-verify` (W1). Ver `[[windows-autostart-single-instance/observations]]` para el
detalle de lo verificado localmente (revisión estática del `.nsh`, V3).

## Related

- [[startup-visibility-preference]] — gobierna si la ventana aparece o queda en la bandeja
  en cada arranque, incluido el arranque que dispara esta opción
- [[unified-product-identity]] — el nombre de producto que identifica la entrada de arranque
  automático es el mismo que la persona ve en el instalador y en la ventana
