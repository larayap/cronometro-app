# Work Tracker

Es una aplicación de escritorio de **código abierto** que mide el tiempo de uso de otras aplicaciones, además de un temporizador pomodoro y manual.

Guarda sesiones de trabajo, personaliza tu pomodoro, asigna qué programas monitoreas y revisa el historial de uso de tus aplicaciones. Todo en la misma ventana, Work Tracker se ejecuta en segundo plano  y junto al inicio del sistema.

Work Tracker está dirigido a personas que quieran registrar sesiones de trabajo de distintas aplicaciones y programar descansos para largos periodos, como artistas y programadores

## Manual de uso

El [manual](docs/MANUAL.md) de uso explica las funciones más a detalle de cada uno de los módulos:

- Manual, cronómetro simple

- Work, selector de aplicaciones, grupos, sesiones e historial 

- Pomodoro, configuración de los tiempos y sonidos

## Instalación

Descarga el instalador (`.exe`) más reciente desde la sección
[Releases](https://github.com/larayap/work-tracker/releases) del repositorio y ejecútalo.

## Privacidad

Work Tracker no tiene servidor, ni cuenta de usuario, ni telemetría. Todo lo que registra —el
tiempo por aplicación, el historial, las preferencias y la lista de programas monitoreados— se
guarda solo en tu equipo, en el directorio de datos que Windows le asigna a la aplicación bajo
`%APPDATA%`. Nada de eso se envía a ningún servidor ni se comparte con terceros.

Para medir el tiempo de uso, la aplicación consulta cuál es la ventana en foco y enumera las
aplicaciones instaladas (para que puedas elegir cuáles monitorear, con su nombre e ícono). Esa
información se usa exclusivamente para lo anterior y no sale de tu equipo.

## Sistema operativo

**Solo Windows.** La detección de la ventana en foco, la enumeración de aplicaciones
instaladas y la extracción de íconos se apoyan en mecanismos específicos de Windows
(PowerShell, registro del sistema) concentrados en un único módulo del main process —
ver [ADR-0004](memory/adrs/0004-os-dependent-code-single-module.md). No hay soporte para
macOS ni Linux hoy.

## Compilar desde el código fuente

Requiere la versión de Node declarada en [`.nvmrc`](.nvmrc) (Node 16.20.2 — el bundle del
main process lo arma un webpack 4 anidado que no soporta versiones más nuevas de OpenSSL).

```bash
nvm use
npm ci
npm run electron:build
```

El instalador queda en `dist_electron/`. Para desarrollo con recarga en caliente:

```bash
npm run electron:serve
```

## Stack

- [Electron](https://www.electronjs.org/) 13
- [Vue](https://vuejs.org/) 3.2
- [Pinia](https://pinia.vuejs.org/) como store

## Sobre `memory/`

El directorio `memory/` en la raíz del repositorio no es código de la aplicación: es el
conocimiento acumulado del proyecto (specs, decisiones de arquitectura, historial de cambios)
que produce y consume el pipeline de desarrollo interno del equipo. Un colaborador externo
puede ignorarlo por completo. El detalle está en
[`CONTRIBUTING.md`](CONTRIBUTING.md#sobre-memory).

## Licencia

[MIT](LICENSE) — Copyright (c) 2026 larayap.
