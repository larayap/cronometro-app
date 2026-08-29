---
type: capability-spec
title: "Preferencia de visibilidad al arrancar: ventana visible o solo en bandeja"
capability: "app-settings"
slug: "startup-visibility-preference"
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
commits: ["9c4ca3a"]
mr: "https://github.com/larayap/work-tracker/pull/6"
acceptance_criteria:
  - "El panel de configuración ofrece elegir si la aplicación arranca mostrando la ventana o solo en la bandeja"
  - "Elegir que la ventana se muestre hace que la ventana aparezca en todo arranque siguiente, manual o automático"
  - "Elegir que la aplicación quede solo en bandeja hace que la ventana no aparezca en ningún arranque siguiente, manual o automático"
  - "La preferencia elegida se mantiene después de cerrar y volver a abrir la aplicación"
  - "Un usuario que nunca eligió la preferencia ve la ventana al arrancar"
related: ["[[configurable-time-format-preference]]", "[[installer-opt-in-autostart]]", "[[single-instance-focus]]", "[[judgment-fixes-iteration-1]]"]
affects: []
adrs: ["[[0006-userdata-json-persistence]]"]
scope: ["src/background.js", "src/main/ipc-handlers.js", "src/stores/settings.js", "src/components/OpcionesPanel.vue"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# Preferencia de visibilidad al arrancar: ventana visible o solo en bandeja

## Purpose

Hoy la aplicación no ofrece ninguna forma de elegir qué pasa con la ventana al arrancar.
Esta spec agrega, en el panel de configuración, una preferencia que decide si la ventana
aparece o si la aplicación queda solo en la bandeja al iniciar, y hace que esa preferencia
gobierne **todo** arranque de la aplicación —tanto cuando la persona la abre a mano como
cuando arranca automáticamente con el inicio de sesión de Windows— sin distinción de origen.

## Requirements

- El sistema SHALL ofrecer, en el panel de configuración, una preferencia para elegir si la
  ventana se muestra o si la aplicación arranca solo en la bandeja.
- El sistema SHALL aplicar la preferencia elegida en todo arranque de la aplicación, sin
  distinguir si el arranque lo inició la persona a mano o si ocurrió automáticamente con el
  inicio de sesión de Windows.
- El sistema SHALL recordar la preferencia elegida entre reinicios de la aplicación.
- El sistema SHALL mostrar la ventana al arrancar para un usuario que nunca cambió la
  preferencia.

## Scenarios

### Scenario: Elegir que la ventana se muestre al arrancar

**GIVEN** el panel de configuración abierto
**WHEN** el usuario elige que la ventana se muestre al arrancar
**THEN** la ventana aparece en todo arranque siguiente de la aplicación

### Scenario: Elegir que la aplicación arranque solo en bandeja

**GIVEN** el panel de configuración abierto
**WHEN** el usuario elige que la aplicación arranque solo en la bandeja
**THEN** la ventana no aparece en ningún arranque siguiente de la aplicación, y la aplicación
queda accesible desde la bandeja

### Scenario: La preferencia aplica igual sin importar el origen del arranque

**GIVEN** la preferencia fijada en "solo bandeja" y el arranque automático con Windows
activado
**WHEN** la persona inicia sesión en Windows y la aplicación arranca automáticamente
**THEN** la aplicación queda solo en la bandeja, igual que si la persona la hubiera abierto a
mano con esa misma preferencia

### Scenario: La preferencia se mantiene entre reinicios

**GIVEN** una preferencia de visibilidad al arrancar ya elegida
**WHEN** el usuario cierra y vuelve a abrir la aplicación
**THEN** el arranque siguiente respeta la preferencia elegida

### Scenario: Un usuario que nunca eligió tiene la ventana visible por defecto

**GIVEN** una instalación de la aplicación en la que nunca se cambió la preferencia
**WHEN** la aplicación arranca
**THEN** la ventana aparece

## Acceptance Criteria

- [ ] El panel de configuración ofrece elegir si la aplicación arranca mostrando la ventana
  o solo en la bandeja.
- [ ] Elegir que la ventana se muestre hace que la ventana aparezca en todo arranque
  siguiente, manual o automático.
- [ ] Elegir que la aplicación quede solo en bandeja hace que la ventana no aparezca en
  ningún arranque siguiente, manual o automático.
- [ ] La preferencia elegida se mantiene después de cerrar y volver a abrir la aplicación.
- [ ] Un usuario que nunca eligió la preferencia ve la ventana al arrancar.

Ningún criterio de esta spec es verificable end-to-end desde WSL2 (todos requieren un proceso
Electron real corriendo, con o sin ventana visible) — diferidos en bloque a `sdd-verify` (W1).
`V2` (`sdd-apply`) sí verificó localmente, con un stub de `electron`, la pieza de la que
depende el último criterio: `readSettings()` devuelve `startupVisibility: 'window'` tanto sin
`settings.json` como con uno existente que no tiene la clave — la mitad determinista del
comportamiento, no la mitad que requiere Electron real (agendar o no `.show()`). Ver
`[[windows-autostart-single-instance/observations]]`.

## Related

- [[configurable-time-format-preference]] — preferencia hermana del mismo panel de
  configuración, con el mismo mecanismo de persistencia y de valor por defecto
- [[installer-opt-in-autostart]] — habilita el arranque automático con Windows; esta
  preferencia decide qué se ve en ese arranque y en cualquier otro
- [[single-instance-focus]] — el enfoque de la ventana existente ante un segundo arranque es
  una acción explícita del usuario y siempre muestra la ventana, sin consultar esta
  preferencia
- [[judgment-fixes-iteration-1]] — ya establece que ocultar la ventana no la destruye y que
  puede volver a mostrarse desde la bandeja; esta preferencia decide el estado inicial con el
  que arranca
