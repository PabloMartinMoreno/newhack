---
tipo: meta
visibilidad: publica
creado: 2026-08-05
aliases:
  - Atajos
  - Cómo me muevo
tags:
  - meta/setup
---

# Recorrido del vault en nvim

## 0. Base
Los atajos y el orden en que se usan. La instalación y la configuración están en [[Puesta a punto de Obsidian]].

> [!tip] Los cinco que importan de verdad
> `<leader>oq` saltar a una nota · `z2` plegar y ver la estructura · `<CR>` seguir el link · `<C-o>` volver · `<leader>ob` quién me enlaza

> [!info]- Cómo se leen las teclas
> | Notación | Tecla |
> |---|---|
> | `<CR>` | Enter |
> | `<leader>` | Barra espaciadora |
> | `<C-o>` | Ctrl + o |
> | `<S-h>` | Shift + h |
> | `<M-x>` | Alt + x |
> | `<Esc>` | Escape |
>
> Lo que empieza con `<leader>` va **en secuencia**: `<leader>oq` es espacio, después o, después q. Lo que empieza con `<C-` va **simultáneo**: Ctrl apretado mientras tocás la otra tecla.

## 1. Entrar

```sh
vault
```

Abre kitty en el vault con [[Inicio]]. obsidian.nvim detecta el workspace por la ruta, que sale de `$OBSIDIAN_VAULT`.

Desde una terminal ya abierta alcanza con `cd` al vault y `nvim`, **siempre que sea kitty**: en st los íconos de heading salen como cajitas.

## 2. Encontrar la nota

Cuatro entradas, según qué recordás:

| Recordás | Tecla |
|---|---|
| El nombre o un alias | `<leader>oq` |
| Una frase del contenido | `<leader>oo` |
| El tag | `<leader>og` |
| Nada, querés mirar | `<leader>e` |

`<leader>oq` cubre casi todo. Busca por nombre **y por alias**, así que `time-based` llega a [[SQLi - canal temporal ciego]] aunque el archivo no se llame así. Por eso [[Convenciones de nombres]] exige el alias en el otro idioma.

Los de LazyVim siguen disponibles y a veces sirven más: `<leader>ff` archivos, `<leader>/` grep crudo, `<leader>fr` recientes, `<leader>,` buffers abiertos.

## 3. Leer

**Primero plegar.** Antes de leer nada, `z2`:

```
# SQLi - canal temporal ciego
## Cuándo lo elijo        ← se abre con za
## Por qué funciona
## Cómo falla
## Coste
```

Decidís si esa variante sirve en tres segundos en vez de leer sesenta líneas. En un MOC, `z2` es el temario.

| Tecla | Acción |
|---|---|
| `z1` … `z6` | Plegar a ese nivel de heading |
| `za` | Abrir/cerrar la sección del cursor |
| `zR` / `zM` | Abrir todo / cerrar todo |
| `]]` / `[[` | Heading siguiente / anterior |
| `<leader>oi` | Picker de headings, para saltar a uno lejano |

**Después, seguir enlaces.** Sobre un wikilink:

- `<CR>` — acción según contexto: sobre un link lo abre, sobre un checkbox lo marca
- `gf` — solo abre links

^seguir-enlaces

> [!important] `<C-o>` es la tecla más importante del vault
> `<C-o>` vuelve a la nota anterior, `<C-i>` avanza de nuevo. Un zettelkasten se recorre saltando y volviendo; sin esto te perdés a los cuatro saltos. Es nativa de vim y la jumplist recuerda la cadena entera, no solo el último salto.

**El grafo en las dos direcciones:**

- `<leader>ol` — a dónde apunta esta nota
- `<leader>ob` — **quién apunta a esta nota**

`<leader>ob` es el que da el valor real del modelo. Abrís [[Sysmon EID 10 - ProcessAccess]] y ves de un lado el tradecraft que la emite y del otro la detección que la consume: las dos caras en una pantalla. Es la bisagra de [[Estructura del vault]] hecha visible.

**Dos notas lado a lado** — el MOC a la izquierda, la técnica a la derecha:

```
<C-w>v        partir la ventana
<C-h> <C-l>   moverse entre paneles
<C-w>c        cerrar el panel
```

> [!note] Detalle de movimiento
> Con `wrap` activo, `j` y `k` bajan una línea **lógica**: saltan párrafos enteros. `gj` y `gk` bajan una línea **visual**. Por eso no se pisaron con navegación de headings, como sí hacen otras configs.

## 4. Ordenar lo abierto

Seguir enlaces abre buffers, y nvim no cierra ninguno solo. La barra de arriba no son pestañas: es bufferline mostrando todo lo que quedó abierto.

| Tecla | Acción |
|---|---|
| `<leader>bd` | Cerrar el buffer actual |
| `<leader>bo` | Cerrar **todos menos el actual** |
| `<leader>bl` / `<leader>br` | Cerrar los de la izquierda / derecha |
| `<S-h>` / `<S-l>` | Buffer anterior / siguiente |
| `<leader>,` | Picker de buffers abiertos |
| `:BufferLinePickClose` | Marca cada buffer con una letra y cerrás el que elijas |

> [!tip] No los cierres de a uno
> Acumular buffers es el uso normal: para volver está `<C-o>`, no la barra. Trabajás, se llenan veinte, y al cambiar de tema hacés `<leader>bo` y quedás con uno.

Si estás trabajando desde un MOC al que volvés todo el tiempo, fijalo y limpiá alrededor:

```
<leader>bp   fijar (pin) este buffer
<leader>bP   cerrar todos los NO fijados
```

## 5. Escribir

`<leader>on` crea una nota desde plantilla: pide cuál y el nombre, y completa `creado:` solo.

- Escribí `[[` y el autocompletado ofrece las notas existentes — así no nacen enlaces rotos
- `gsab` envuelve en `**negrita**`, `gsac` en `` `código` ``; `gsd` borra el delimitador y `gsr` lo reemplaza
- `<leader>os` prende el corrector con español e inglés juntos. `z=` sugerencias, `zg` agrega la palabra al diccionario
- `<C-s>` guarda

> [!warning] Nunca renombrar desde el explorer
> Usá `<leader>or`. Arrastra todos los wikilinks que apuntaban a esa nota. Renombrar a mano rompe el grafo en silencio, y las consultas dejan de ver la nota sin avisar.

## 6. Mantener

`<leader>oc` abre el menú de [[Consultas del vault]]. Las dos de rutina:

- **`revalidacion`** — tradecraft con más de seis meses sin probar. Es el backlog de laboratorio de [[Validación de tradecraft en laboratorio]].
- **`higiene`** — frontmatter inválido y enlaces rotos.

`<leader>om` apaga el render para ver el markdown crudo. `<leader>oz` es modo zen para escribir largo.

## Relacionadas

[[Puesta a punto de Obsidian]] · [[Estructura del vault]] · [[Convenciones de nombres]] · [[Consultas del vault]]
