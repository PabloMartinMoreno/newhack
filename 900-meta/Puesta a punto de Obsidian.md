---
tipo: meta
aliases:
  - Plugins
  - Setup
tags:
  - meta/setup
---

# Puesta a punto de Obsidian

> [!important] El cliente principal es nvim, no Obsidian
> Decisión de 2026-08-05: el vault se consume desde **nvim**. Nada de lo que sigue es requisito — el vault funciona con archivos planos y `rg`. Esta nota queda como referencia por si en algún momento se abre en Obsidian (grafo, Publish).
>
> Consecuencia dura: **sin Dataview no hay consultas**. Las cinco consultas cruzadas rojo/azul se implementan como script CLI sobre el frontmatter — ver [[Consultas del vault]]. Ese script no es un accesorio: es lo único que hace que fusionar los dos lados rinda.

## Setup en nvim — hecho

LazyVim. Specs en `~/.config/nvim/lua/plugins/obsidian.lua` y `render-markdown.lua`. Instalado y verificado el 2026-08-05 con `obsidian.nvim` v3.16.6 y nvim 0.12.4.

### Dos ajustes que no son opcionales

| Ajuste | Por qué |
|---|---|
| `frontmatter = { enabled = false }` | Por defecto `obsidian.nvim` **reescribe el frontmatter al guardar**: inyecta `id`, `aliases` y `tags`, y reordena las claves. Destruiría el esquema de [[Esquema de frontmatter]] nota por nota, en silencio. |
| `ui = { enable = false }` | `obsidian.nvim` y `render-markdown.nvim` renderizan los dos checkboxes, bullets y links. Con ambos activos se duplican. El render lo hace render-markdown. |

`note_id_func = builtin.title_id` — el nombre de archivo es el título, no un ID zettel numérico. Ver [[Convenciones de nombres]].

### Atajos

El flujo de trabajo y el orden en que se usan están en [[Recorrido del vault en nvim]]. Acá solo la lista.

| Tecla | Acción |
|---|---|
| `<leader>on` | Nota nueva **desde plantilla** (`999-plantillas`) |
| `<leader>oo` / `<leader>oq` | Buscar en el vault / saltar a nota |
| `<leader>ob` / `<leader>ol` | Backlinks / enlaces salientes |
| `<leader>og` | Tags |
| `<leader>or` | Renombrar arrastrando los enlaces |
| `<leader>oc` | **`consultas.py`** — menú de las consultas |
| `<leader>ot` `<leader>oi` `<leader>ox` | Plantilla acá · índice de la nota · alternar checkbox |
| `<leader>om` / `<leader>oz` | Render on/off · modo zen |
| `<leader>os` | Corrector es+en on/off. Sugerencias con `z=`, agregar palabra con `zg` |
| `gf` / `<CR>` | Seguir wikilink · acción según contexto (link o checkbox) |

### Leer una nota plegada

`z1` … `z6` pliegan al nivel de heading indicado; `zR` abre todo, `zM` cierra todo, `za` alterna el fold del cursor. Solo en markdown.

`z2` sobre una nota de tradecraft deja a la vista las cuatro secciones fijas y esconde el cuerpo — es la forma rápida de decidir si esa variante sirve. Sobre un MOC, `z2` es el temario.

Para moverse entre headings, `]]` y `[[`: los trae el ftplugin de markdown de nvim, no hay que configurar nada.

### Delimitadores

`mini.surround` con dos atajos propios: `gsab` envuelve en `**negrita**`, `gsac` en `` `código` ``. `gsd` borra el delimitador y `gsr` lo reemplaza.

### Render visual

Headings con barra de color a ancho completo, uno por nivel. Los colores **se derivan del colorscheme activo**, no son hex fijos: se leen de `@markup.heading.N.markdown`, se mezclan con el fondo de `Normal` y se recalculan solos en el autocmd `ColorScheme`. Cambiar de tema no rompe nada.

Además: tablas con borde redondeado y celdas alineadas (el vault es mayormente tablas), bloques de código con borde, bullets por nivel, callouts en español y `signcolumn` limpio.

`render_modes = { "n", "c", "t" }` — en modo insert no renderiza, así que el frontmatter y las tablas se editan crudos.

Completado de wikilinks: por LSP in-process, sin registrar source en `blink.cmp`.

### Búsqueda directa

El esquema de [[Esquema de frontmatter]] no depende de ningún plugin — son claves YAML planas justamente para que `rg` alcance:

```sh
rg -l '^opsec: quemado' 600-tradecraft/
rg -l 'Sysmon EID 10' 600-tradecraft/ 650-detecciones/
```

**Un solo workspace: `newhack`.** `Hack` no está declarado — desde nvim se usa únicamente este vault, y así el plugin no se activa al abrir markdown de cualquier otro lado. `Hack` se sigue consultando desde Obsidian o con `rg`.

## Plugins núcleo (activar solo si se usa Obsidian)

| Plugin | Para qué |
|---|---|
| **Plantillas** (Templates) | Carpeta de plantillas → `999-plantillas`. Atajo a `Ctrl+T`. |
| **Notas diarias** | Opcional. Si se usa, carpeta → `000-inbox`. |
| **Vista de grafo** | Filtrar por `tipo` para ver la bisagra de telemetría aislada. |
| **Enlaces salientes / entrantes** | Los backlinks son la mitad del valor de `550-telemetria`. |
| **Búsqueda** | — |

## Plugins comunitarios (requeridos)

| Plugin | Para qué | Sin él |
|---|---|---|
| **Dataview** | Todas las consultas de [[Consultas del vault]]. | El vault pierde la caducidad y las cuatro consultas de fusión. |
| **Templater** | Prompts al crear nota; fecha automática en `probado:`. | Se completa a mano. |

## Opcionales que valen

- **Excalidraw** — árboles de decisión de MOC dibujados. Alternativa gratis: bloques `mermaid`, que ya renderiza Obsidian nativo.
- **Advanced Tables** — las matrices de referencia son tablas grandes.
- **Homepage** — abrir siempre en [[Inicio]].
- **Style Settings** + un tema con soporte de callouts.

## Ajustes

- **Enlaces**: formato *Ruta más corta posible*, `Usar [[Wikilinks]]` activado. El vault depende de que Obsidian siga los renombres.
- **Archivos y enlaces**: carpeta de adjuntos → `900-meta/adjuntos` (no en la raíz).
- **Propiedades**: vista de propiedades visible; conviene fijar el orden `tipo`, `clase`/`tecnicas`, `telemetria`, `opsec`/`estado`, `probado`/`validada`, `visibilidad`.

## Vista de grafo — filtros útiles

```
tipo:telemetria OR tipo:tradecraft OR tipo:deteccion
```

Ese grafo es el que hay que mirar: si los nodos de telemetría no tienen aristas de los dos colores, la fusión todavía es nominal.

## Sincronización

- Este vault: repo privado. Es tradecraft anotado por OPSEC — no se publica.
- Vault de engagements: **nunca** en el mismo remoto, cifrado en disco.

## Relacionadas

[[Estructura del vault]] · [[Consultas del vault]] · [[Avances]]
