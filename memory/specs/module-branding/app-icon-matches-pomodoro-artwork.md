---
type: capability-spec
title: "El ícono de la aplicación —ventana, bandeja e instalador— usa el arte de Pomodoro"
capability: "module-branding"
slug: "app-icon-matches-pomodoro-artwork"
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
commits: ["af1824e"]
mr: "https://github.com/larayap/work-tracker/pull/7"
acceptance_criteria:
  - "El ícono de la ventana de la aplicación muestra el arte de Pomodoro"
  - "El ícono de la aplicación en la bandeja del sistema muestra el arte de Pomodoro"
  - "El ícono del instalador y del acceso directo que instala muestran el arte de Pomodoro"
  - "El arte se ve completo dentro de cada ícono, sin ninguna parte recortada"
related: ["[[unified-product-identity]]", "[[module-icons-for-work-and-pomodoro]]"]
affects: []
adrs: ["[[0004-os-dependent-code-single-module]]", "[[0014-single-build-toolchain-and-pinned-node]]"]
scope: ["src/background.js", "public/icon-work-256.png", "public/img/icon-work.png", "vue.config.js"]
verified_at: null
created: "2026-08-09"
updated: "2026-08-09"
tags: [capability-spec]
---

# El ícono de la aplicación —ventana, bandeja e instalador— usa el arte de Pomodoro

## Purpose

El ícono que hoy identifica a la aplicación en su ventana, en la bandeja del sistema y en el
instalador no está relacionado con ninguno de los dos íconos de módulo que este cambio
introduce. Esta spec reemplaza ese ícono por el arte de Pomodoro, encuadrado en un fondo
cuadrado transparente para no perder contenido de la imagen, en cada uno de los lugares
donde el sistema operativo lo muestra.

## Requirements

- El sistema SHALL mostrar el arte de Pomodoro como ícono de la ventana de la aplicación.
- El sistema SHALL mostrar el arte de Pomodoro como ícono de la aplicación en la bandeja del
  sistema.
- El sistema SHALL mostrar el arte de Pomodoro como ícono del instalador y del acceso directo
  que ese instalador crea.
- El sistema SHALL encuadrar el arte de Pomodoro en un fondo cuadrado transparente antes de
  usarlo como ícono, sin recortar ninguna parte de la imagen original.

## Scenarios

### Scenario: La ventana de la aplicación muestra el nuevo ícono

**GIVEN** la aplicación abierta
**WHEN** el usuario mira el ícono de su ventana
**THEN** ve el arte de Pomodoro en vez del ícono anterior

### Scenario: La bandeja del sistema muestra el nuevo ícono

**GIVEN** la aplicación minimizada a la bandeja del sistema
**WHEN** el usuario mira el ícono en la bandeja
**THEN** ve el arte de Pomodoro en vez del ícono anterior

### Scenario: El instalador y el acceso directo muestran el nuevo ícono

**GIVEN** una persona que descarga e instala la aplicación
**WHEN** mira el instalador y el acceso directo que este crea
**THEN** ambos muestran el arte de Pomodoro

## Acceptance Criteria

- [x] El ícono de la ventana de la aplicación muestra el arte de Pomodoro. Verificado
  inspeccionando `public/icon-work-256.png` con Pillow (256×256 RGBA, arte de
  `pomodoro_worktracker.webp` paddeado a cuadrado transparente) y confirmando que
  `src/background.js:67` lo lee vía `__static`.
- [x] El ícono de la aplicación en la bandeja del sistema muestra el arte de Pomodoro.
  Verificado inspeccionando `public/img/icon-work.png` con Pillow (32×32 RGBA, mismo
  lienzo); `src/background.js:31` (Tray) sigue leyendo este archivo sin cambios.
- [ ] El ícono del instalador y del acceso directo que instala muestran el arte de Pomodoro.
  **No verificado en esta fase** (ver `## Observations`): exige compilar el paquete de
  Windows, que WSL2 no ejecuta.
- [ ] El arte se ve completo dentro de cada ícono, sin ninguna parte recortada. **Parcialmente
  no verificado**: el `bbox` de alfa de los dos PNG regenerados confirma que el arte llena el
  lienzo cuadrado sin recorte para ventana y bandeja, pero este criterio abarca también el
  instalador y el acceso directo (no verificados), así que queda sin marcar como un todo —
  ver `## Observations`.

## Observations

Los primeros dos criterios (ventana y bandeja) son verificables en este entorno porque
resultan de un archivo regenerado que se puede inspeccionar directamente. Los dos últimos
—el ícono embebido en el instalador NSIS y en el acceso directo que crea— requieren compilar
el paquete de Windows para observarse de punta a punta; esta fase no ejecuta esa compilación
(WSL2 no compila para `windows-latest`), así que quedan sin verificar hasta que se generen en
el entorno de build/verificación de Windows ya disponible para el proyecto. No se marcan como
cumplidos por adelantado ni se disfraza esta limitación como criterio satisfecho.

## Related

- [[unified-product-identity]] — misma superficie de identidad del producto (instalador,
  ventana), con el ícono como el atributo que esta spec agrega
- [[module-icons-for-work-and-pomodoro]] — usa el arte hermano de Work para los íconos dentro
  de la interfaz, mientras esta spec usa el arte de Pomodoro para el ícono de la aplicación
