---
type: adr
title: "Los colores compartidos entre las dos ventanas viven en una capa de tokens CSS importada por cada entry"
status: accepted
supersedes: null
superseded_by: null
amends: null
created: "2026-08-09"
change_ref: "[[ui-branding-polish]]"
capability: "design-tokens"
tags: [adr]
---

# Los colores compartidos entre las dos ventanas viven en una capa de tokens CSS importada por cada entry

## Context

La aplicación se renderiza en **dos bundles webpack independientes** declarados en
`vue.config.js.pages`: `index` (`src/main.js`, la ventana de trabajo, siempre abierta) y
`history` (`src/history/main.js`, la ventana de historial, que se abre a demanda). Dos ADRs
previos fijaron qué **no** cruza esa frontera: ADR-0010 confina la librería de gráficos al
bundle de historial, y ADR-0012 establece que ese bundle no monta Pinia —importar
`@/stores/settings` arrastraría `howler` y cinco audios precargados a una ventana muda— y que
las preferencias viajan por IPC.

Ninguna decisión cubría la dirección de la **presentación**: cómo comparten las dos ventanas
una constante visual. El estado hasta hoy es que no la comparten. Ningún archivo declara
variables CSS; cada componente hardcodea sus propios hex, con bloques repetidos palabra por
palabra en cuatro componentes (`.modal-overlay`, `.modal-content`, `.close-btn` en
`AppSelectorModal.vue`, `OpcionesPanel.vue`, `TitleBar.vue` y `history/TitleBar.vue`).

`ui-branding-polish` fuerza la decisión porque introduce el primer color que **tiene que ser
idéntico en las dos ventanas por requisito explícito**: el indicador de foco de teclado
(`shared-accent-colors-across-windows` — "el color del indicador de foco se ve igual en la
ventana de trabajo y en la ventana de historial", y "cambiar el tono en un único lugar"). El
mismo cambio agrega los grises del resaltado de rango del calendario, que consume solo la
ventana de historial pero cuyos valores se eligen en relación con el anillo de foco y entre
sí.

Sin un lugar único, el resultado más probable es el mismo hex duplicado en once archivos de
dos bundles: el patrón que el proyecto ya paga cuatro veces con `.modal-overlay`.

Un dato del entorno acota la forma: el propio entry de historial ya importa una hoja de
estilos suelta (`import 'v-calendar/style.css'`), así que la mecánica está probada en el
bundle que más restricciones tiene.

## Decision

Los colores que las dos ventanas comparten viven en **`src/styles/tokens.css`**, un archivo de
**CSS puro** con un bloque `:root` de custom properties, importado explícitamente **como
primer import de cada entry** (`src/main.js` y `src/history/main.js`).

El archivo puede contener, además de las custom properties, las **reglas transversales que las
consumen y que valen por igual en las dos ventanas**. La primera y única de este cambio es el
anillo de foco de teclado:

```css
:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}
```

La alternativa —solo variables en el archivo y la regla duplicada en el `<style>` no-scoped de
`App.vue` y de `HistoryView.vue`— reintroduce un nivel más arriba la duplicación que el archivo
existe para evitar.

Cuatro reglas acotan el patrón:

1. **CSS puro, sin excepción.** No un store Pinia, no un módulo JS con dependencias, no un
   plugin de Vue. Es la única forma que atraviesa la frontera de ADR-0012 sin arrastrar nada al
   bundle de historial.
2. **Un import por entry, explícito.** No hay inyección automática ni configuración de webpack
   que lo agregue: agregar una ventana nueva implica agregar su import. El costo de olvidarlo no
   es visible de inmediato: las tres reglas que consumen el token (`tokens.css:24`,
   `TitleBar.vue:276`, `HistoryView.vue:310`) lo hacen sin valor de respaldo — `var(--focus-ring)`
   a secas —, así que con el token indefinido la declaración queda inválida en tiempo de valor
   computado y se comporta como `unset`: el `outline` cae a `outline-style: none` y el
   `box-shadow` a `none`. El resultado no es otro color, es ningún indicador de foco, y en
   silencio: no se nota hasta que alguien navega con teclado.
3. **Solo entra lo compartido, o lo que se define en relación con lo compartido.** El archivo
   no es un tema ni una paleta del producto: los hex ya hardcodeados en los componentes **no**
   se migran. Migrarlos es un cambio con su propio alcance y su propia verificación visual.
4. **Nombres semánticos en kebab-case sobre `:root`, sin prefijo de proyecto.** Las variables
   de librería conservan su propio namespace (`--vc-*` de v-calendar) y no hay ninguna otra
   librería que declare custom properties en este proyecto, así que un prefijo `--wt-` no
   compra nada hoy.

Con esto, el conjunto de decisiones sobre la frontera entre bundles queda completo y sin
solapamiento:

```
ADR-0010  qué código NO cruza hacia el bundle siempre abierto  (graficado)
ADR-0012  cómo cruza el DATO de preferencia                    (IPC, pull, sin Pinia)
ADR-0015  cómo cruza la CONSTANTE DE PRESENTACIÓN              (CSS puro, un import por entry)
```

## Consequences

**Positivas:**

- Un color compartido se cambia en un lugar y se ve reflejado en las dos ventanas, que es
  literalmente lo que pide `shared-accent-colors-across-windows` en su requisito SHOULD.
- El bundle de historial no incorpora ni Pinia ni ninguna dependencia nueva: una hoja de estilos
  es lo más barato que puede cruzar, y su import ya tiene precedente en ese entry.
- La regla transversal de foco existe una sola vez para toda la aplicación, así que un control
  nuevo hereda el indicador correcto sin que nadie se acuerde de declararlo. El inventario
  manual de controles focables ya había fallado una vez: `exploration.md` contó 19 selectores y
  el barrido de `sdd-design` encontró cinco controles más.
- El archivo es un lugar obvio donde mirar: la próxima persona que quiera ajustar un tono
  compartido no tiene que hacer grep de un hex por todo `src/`.
- La regla 3 evita que el archivo se convierta en un refactor de tema encubierto dentro de un
  cambio de UI.

**Trade-offs:**

- **El archivo mezcla dos cosas**: declaraciones de tokens y una regla que los consume. El
  nombre `tokens.css` no lo anticipa, y se sostiene con el comentario de cabecera. Es el precio
  de no duplicar la regla en dos bundles.
- **Nada en el build impone el import.** Un entry nuevo sin él compila igual y falla solo de
  forma visual. Es la misma clase de invariante sostenida por documentación que ADR-0010 y
  ADR-0012 ya aceptan.
- **Convivencia de dos regímenes de color.** Mientras los hex existentes no se migren, el
  proyecto tiene colores tokenizados y colores hardcodeados a la vez, y hay que saber cuáles son
  cuáles. Es deliberado: la alternativa es un refactor visual sin verificación automatizada en
  un proyecto sin tests.
- **Una regla global de foco alcanza a todo elemento focable**, incluidos los que vengan de una
  librería. La convivencia se resuelve por cascada, no por enumeración: el CSS de v-calendar
  (`.vc-container *:focus { outline: none }`, especificidad (0,2,0)) le gana a la regla global
  (0,1,0), de modo que dentro del calendario manda el indicador propio de la librería. Es un
  acoplamiento implícito a la especificidad del CSS de terceros, verificado para
  `v-calendar@3.1.2` y sujeto a revisión si esa hoja cambia.
- **`:root` es global por construcción**: un token con nombre poco específico puede colisionar
  con una librería futura que también declare custom properties en `:root`. La regla 4 lo acepta
  con cuatro tokens y sin prefijo; si aparece una segunda librería con custom properties, la
  decisión se revisa.

## Alternatives Considered

- **Un store Pinia o un módulo JS con la paleta, consumido por los componentes**: es lo que haría
  un proyecto sin la restricción de ADR-0012. Se descarta porque el bundle de historial no monta
  Pinia y un módulo JS de paleta obligaría a inyectar valores desde JS a CSS
  (`style` inline o `CSSStyleDeclaration.setProperty`) para algo que CSS resuelve solo.
- **Duplicar la regla y los hex en el `<style>` no-scoped de `App.vue` y de `HistoryView.vue`**:
  cero archivos nuevos, cero imports. Se descarta porque es exactamente la duplicación que el
  proyecto ya paga con `.modal-overlay` y porque el requisito de la spec es "cambiar el tono en
  un único lugar".
- **Un `<link>` a la hoja en `public/index.html` y `public/history.html`** en vez de un import
  por entry: evita tocar los entries. Se descarta porque saca el archivo del grafo de módulos:
  webpack deja de versionarlo con hash, deja de fallar el build si la ruta se rompe, y el estilo
  llega por un camino distinto del de todo el resto del CSS del proyecto.
- **Inyectar el import automáticamente** (`chainWebpack` con `style-resources-loader` o un
  `prependData`): garantiza que ninguna página se lo olvide. Se descarta por YAGNI y por
  transparencia: son dos entries, el import es una línea en cada uno, y un import visible se lee
  mejor que una inyección invisible en la configuración de build.
- **Migrar de una toda la paleta existente a tokens** en este mismo cambio: dejaría el proyecto
  con un solo régimen de color. Se descarta porque `proposal.md` lo excluye explícitamente y
  porque toca todos los componentes visibles sin un solo test que respalde el resultado.
- **Un prefijo de proyecto en los nombres (`--wt-*`)**: defensa contra colisión en `:root`. Se
  descarta hoy por KISS con cuatro tokens y ninguna colisión observada; queda como la corrección
  natural si el proyecto suma una librería que declare custom properties.
