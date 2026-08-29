# Work Tracker

Cronómetro de tiempo de uso de aplicaciones de escritorio para Windows, con historial,
pomodoro y selección de programas monitoreados.

## Qué hace

Work Tracker corre en la bandeja del sistema y mide cuánto tiempo pasas con cada aplicación
de escritorio abierta y en foco. Eliges qué programas monitorear, revisas el historial de uso
por día y por aplicación, y usas el temporizador Pomodoro integrado sin salir de la misma
herramienta.

## Manual de uso

El [manual](docs/MANUAL.md) recorre la aplicación entera con capturas: los tres módulos, el
selector de aplicaciones, los grupos, el historial, las opciones y la bandeja del sistema.

## Para quién es

Para cualquier persona que quiera entender en qué reparte su tiempo frente a aplicaciones de
escritorio en Windows: quien factura por horas, quien quiere poner límites a una app puntual,
o quien simplemente quiere datos en vez de intuición.

## Sistema operativo

**Solo Windows.** La detección de la ventana en foco, la enumeración de aplicaciones
instaladas y la extracción de íconos se apoyan en mecanismos específicos de Windows
(PowerShell, registro del sistema) concentrados en un único módulo del main process —
ver [ADR-0004](memory/adrs/0004-os-dependent-code-single-module.md). No hay soporte para
macOS ni Linux hoy.

## Instalación

Descarga el instalador (`.exe`) más reciente desde la sección
[Releases](https://github.com/larayap/work-tracker/releases) del repositorio y ejecútalo.

### Si vienes de una versión anterior (Workout)

Work Tracker se instala **junto a** la versión anterior en vez de reemplazarla. La primera vez
que lo abras, tu historial, tus preferencias y tu selección de programas se traspasan solos
desde la instalación vieja; no tienes que hacer nada. Los datos originales quedan intactos como
respaldo.

Una vez que compruebes que tu historial está completo, **desinstala la versión anterior**. Si
sigues abriendo las dos, cada una registra su propio historial por separado y el traspaso ya no
vuelve a ocurrir: terminarías con tu tiempo repartido entre dos aplicaciones.

## Firma de código

Los instaladores todavía no están firmados: al descargarlos, Windows muestra una advertencia de
SmartScreen, y al ejecutarlos aparece como «editor desconocido». No es una señal de que el
archivo esté alterado, sino de que no hay un certificado de firma detrás — y un certificado
comercial no es viable para un proyecto gratuito y sin ingresos.

## Privacidad

Work Tracker no tiene servidor, ni cuenta de usuario, ni telemetría. Todo lo que registra —el
tiempo por aplicación, el historial, las preferencias y la lista de programas monitoreados— se
guarda solo en tu equipo, en el directorio de datos que Windows le asigna a la aplicación bajo
`%APPDATA%`. Nada de eso se envía a ningún servidor ni se comparte con terceros.

Para medir el tiempo de uso, la aplicación consulta cuál es la ventana en foco y enumera las
aplicaciones instaladas (para que puedas elegir cuáles monitorear, con su nombre e ícono). Esa
información se usa exclusivamente para lo anterior y no sale de tu equipo.

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
