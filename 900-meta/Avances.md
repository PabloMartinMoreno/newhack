---
tipo: meta
aliases:
  - Progreso
  - Bitácora
tags:
  - meta/avances
---

# Avances

Bitácora de construcción del vault. Decisiones y pendientes, no changelog de archivos.

## Estado actual

| Capa | Estado |
|---|---|
| Estructura de carpetas | Completa |
| Documentación de administración (`900-meta/`) | Completa |
| Plantillas (`999-plantillas/`) | 11 tipos, completas |
| Notas semilla | Un ciclo rojo↔azul completo + un dominio web completo a nivel MOC |
| Contenido real | Sin empezar |
| Cliente | **nvim/LazyVim**, configurado y verificado. Obsidian y sus plugins descartados |
| Consultas cruzadas | `900-meta/consultas.py`, siete comandos |
| Vault de engagements | Sin crear |

## Bitácora

### 2026-08-05 — Fundación

Creada la estructura completa con 14 carpetas y el modelo de dos bisagras.

**Decisiones tomadas:**

- **Vault único, no dos.** La fusión se justifica solo por las cuatro consultas cruzadas de [[Consultas del vault]]. Si esas no se usan, el vault fusionado no aporta nada sobre dos vaults separados.
- **`telemetria:` unificado** en tradecraft y detecciones, en vez de `huella:`/`fuentes-log:`. Simplifica toda consulta futura.
- **`450-superficies/` separada de `400-entidades/`.** La estructura fusionada original las unía; se separan porque la superficie es la puerta de entrada de la cadena roja y la entidad es una hoja del grafo. Mezclarlas rompe la consulta "qué técnicas aplican a esta tecnología".
- **`750-hallazgos/` conservada** aunque no estaba en la estructura fusionada. La biblioteca de findings tiene retorno propio e independiente del resto.
- **`visibilidad:` desde la primera nota.** Barato ahora, carísimo con 400 notas.
- **`800-engagements/` NO existe acá.** Vault aparte, cifrado.

**Notas semilla escritas** — demuestran el patrón, no son contenido definitivo:

- Ciclo rojo↔azul completo: [[LSASS - volcado vía comsvcs.dll MiniDump]] → [[Sysmon EID 10 - ProcessAccess]] ← [[Acceso a LSASS desde proceso no firmado]], con [[T1003.001 - LSASS Memory]] como bisagra taxonómica.
- Dominio web: [[MOC - SQL injection]] con árbol de decisión, [[SQLi - canal temporal ciego]] con las cuatro secciones fijas, [[Dialectos SQL - matriz de referencia]] como referencia pura, [[La latencia como canal de datos]] como zettel conceptual.
- [[Inyección SQL en parámetro de búsqueda]] como modelo de hallazgo reutilizable.

### 2026-08-05 — El cliente es nvim

Decidido: el vault se consume desde **nvim**, no desde Obsidian. Sin plugins.

Consecuencia: Dataview queda fuera y con él las cinco consultas cruzadas, que son la única justificación de tener rojo y azul en el mismo vault. Se reemplazan por `900-meta/consultas.py` sobre el frontmatter — ver [[Consultas del vault]] § Implementación CLI. **Mientras ese script no exista, el vault fusionado no rinde más que dos vaults separados.** Es el pendiente de mayor prioridad, por encima de cualquier contenido.

Lo que **no** cambia: el vault sigue **fusionado**. nvim mata a Dataview, no a la fusión. `consultas.py` da las mismas respuestas sin depender de un plugin, y encima es versionable y ejecutable en CI. Separar rojo y azul por no tener Dataview sería tirar la bisagra de telemetría por un problema de herramienta.

Efecto lateral favorable: refuerza la elección de NewHack sobre `Hack` para el día a día. Los hubs de `Hack` dependen de bloques ```` ```tabs ```` y de embeds `![[nota#^anchor]]`, que en un buffer de nvim son texto plano y links que no expanden. NewHack es YAML + markdown y se lee igual en cualquier lado.

### 2026-08-05 — Idioma de las nomenclaturas

Fijada la **regla del corpus externo** en [[Convenciones de nombres]]: el idioma no se elige por gusto sino por quién escribió el término. Si aparece literal en una fuente que vas a volver a leer, inglés; si es tuyo, español. Los aliases son la costura entre ambos.

Renombres aplicados, con el nombre en español convertido en alias:

| Antes | Ahora |
|---|---|
| `CWE-89 - Inyección SQL` | [[CWE-89 - SQL Injection]] |
| `T1003.001 - Volcado de memoria de LSASS` | [[T1003.001 - LSASS Memory]] |
| `Registro de consultas lentas de MySQL` | [[MySQL - slow query log]] |

`SQLi - canal temporal ciego` **no** se renombró: "canal de extracción" es descomposición propia por ejes, no terminología de PortSwigger.

### 2026-08-06 — Fuera `visibilidad:` y `creado:`

Se quitaron los dos campos de todas las notas, plantillas, el esquema y el `consultas.py`.

- **`creado:`** — redundante: git guarda la fecha de creación con más precisión y sin mantenerla a mano. Ninguna consulta lo usaba.
- **`visibilidad:`** — existía para un export filtrado a alumnos que se descartó. El repo es privado y uniforme, así que el campo no hacía nada. Cae la regla 5 del `CLAUDE.md`. Revierte la decisión de la fundación ("visibilidad desde la primera nota"); el argumento "barato ahora, caro después" no se sostiene si el export nunca sucede.

### 2026-08-06 — Dominio XSS

Taxonomía fijada por brainstorming antes de escribir (regla del vault). Cinco ejes ortogonales, paralelos a SQLi:

| Eje | Valores |
|---|---|
| Tipo / entrega | reflejado · almacenado · DOM-based |
| Contexto de salida | HTML body · atributo · `<script>` · URL · CSS ← el eje clave |
| Sink (solo DOM) | innerHTML · document.write · eval · location · setAttribute |
| Obstáculo | filtro chars/tags · WAF · CSP |
| Impacto | robo de sesión · keylogger · CSRF-vía-XSS · account takeover · worm |

Decisión: el sink de DOM va en **matriz propia** (no sub-sección), siguiendo el principio del usuario "ante la duda, más notas atómicas". CSP es obstáculo pero por su peso en XSS moderno tiene nota de criterio + matriz de bypass propias.

Escrito: [[CWE-79 - Cross-site Scripting]], [[MOC - Cross-site scripting]] (dos árboles + índice de cheatsheets), tres tipos como tradecraft, [[XSS - CSP]], y seis matrices (contextos, sources/sinks, evasión, bypass CSP, impacto). Pendiente: mXSS, dangling markup, telemetría de violación de CSP.

## Pendientes

### Inmediatos

- [x] `900-meta/consultas.py` — las siete consultas corriendo, verificadas contra las notas semilla
- [x] Setup nvim: `obsidian.nvim` v3.16.6 + `render-markdown.nvim` sobre LazyVim ([[Puesta a punto de Obsidian]])
- [ ] Crear el vault de engagements, cifrado, fuera de este árbol (decidir ubicación y método: gocryptfs / LUKS / repo con git-crypt)

### Contenido

- [ ] Completar los ejes de SQLi que faltan (ver huecos en [[MOC - SQL injection]])
- [ ] Telemetría web: una nota por artefacto que emiten los canales de SQLi — hoy solo existe [[MySQL - slow query log]]
- [ ] [[MOC - Active Directory]]: delegaciones y ADCS
- [ ] Telemetría de Kerberos: `4768`, `4769`, `4662`, `5145`

### Decisiones abiertas

- **Cuál se usa día a día.** Sin decidir. `Hack` **se queda como está** — no se toca, no se migra en bloque. Los dos modelos son incompatibles por diseño: acá los cheatsheets **no** son notas.
  - Postura recomendada: NewHack como vault de conocimiento; `Hack` congelado como capa de comandos que se consulta y no se edita. Cuando se trabaja un tema acá, se destila de `Hack` lo que corresponda — la decisión al zettel, la sintaxis a una matriz de `900-meta/`. Migración por demanda, nunca big-bang.
  - Lo que `Hack` gana: velocidad de recall durante un examen o engagement. Lo que NewHack gana: escala, caducidad modelada, consultas cruzadas y temario para clase.
- **Publicación para alumnos.** Descartada (2026-08-06). No hay plan de export, así que se quitó el campo `visibilidad:` de todas las notas — ver la entrada de bitácora de esa fecha.
