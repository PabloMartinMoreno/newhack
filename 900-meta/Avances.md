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
| Contenido rojo — web | Siete dominios cerrados: SQLi, XSS, file inclusion, file upload, command injection, SSRF, XXE |
| Contenido rojo — infra | Sin empezar. [[MOC - Active Directory]] es semilla |
| Contenido azul | **Una sola detección, y es de Windows.** Cero del lado web — ver Pendientes |
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

### 2026-08-06 — Dominios File inclusion + File upload

El usuario pidió "file upload / inclusion". Se **separó en dos dominios** (CWE y ejes distintos, no comparten taxonomía) que se **encadenan** (LFI + upload = RCE):

- **File inclusion** (CWE-98 / CWE-22). Ejes: tipo (path traversal · LFI · RFI) × wrapper PHP × vía a RCE × obstáculo. Distinción clave: traversal **lee**, inclusion **ejecuta**.
- **File upload** (CWE-434). Ejes: validación evadida (extensión/MIME/magic bytes/contenido) × ejecución × payload × impacto.

Escrito (inclusion): [[CWE-98 - File Inclusion]], [[MOC - File inclusion]] (dos árboles + índice), tradecraft [[Path traversal]] · [[LFI - inclusión local]] · [[LFI - de lectura a RCE]] · [[RFI - inclusión remota]], y tres matrices (path traversal, wrappers, LFI a RCE).

Escrito (upload): [[CWE-434 - Unrestricted File Upload]], [[MOC - File upload]] (dos árboles + índice), tradecraft [[File upload - bypass de validación]] · [[Webshell]] · [[File upload + LFI]], y dos matrices (bypass de validación, webshells). El **combo** [[File upload + LFI]] es el nodo que une los dos dominios: cada MOC referencia al otro. Pendiente en upload: SVG-XSS y XXE vía archivo.

### 2026-08-06 — Dominio Command injection

Taxonomía fijada antes de escribir. Cinco ejes, paralelos a SQLi donde el paralelo es real:

| Eje | Valores |
|---|---|
| Canal de extracción | directo · ciego · temporal · fuera de banda |
| Ruptura del contexto | separador · sustitución · newline · escape de comillas · sin ruptura |
| Shell | `sh`/`bash` · `cmd` · PowerShell · sin shell |
| Obstáculo | espacios · barras · palabras clave · lista blanca · WAF |
| Impacto | lectura · shell interactiva · webshell · pivote |

**Decisión: dos CWE en un MOC.** [[CWE-78 - OS Command Injection]] y [[CWE-88 - Argument Injection]] comparten [[MOC - Command injection]] porque la misma pregunta las separa —¿hay shell?— y esa pregunta es el nodo raíz del árbol de decisión. Separarlas en dos MOC obligaría a duplicar ese nodo en ambos y a que cada uno terminara mandando al otro. Es el mismo criterio que unió upload e inclusion por [[File upload + LFI]], pero más fuerte: acá no es un combo, es una bifurcación.

**Divergencias deliberadas respecto de SQLi**, no descuidos:

- **No hay eje de canal `UNION`/error.** El shell no devuelve datos estructurados: o hay `stdout` o no hay nada. El canal directo absorbe ambos.
- **`2>&1` es un nodo del árbol de canales, no un truco de la matriz.** Mueve casos enteros de ciego a directo sin cambiar nada más, y es lo más barato del árbol.
- **El canal temporal puede dar falso negativo.** Con ejecución asíncrona no hay retardo aunque haya ejecución; fuera de banda es el único canal que cubre ese caso. En SQLi el problema no se plantea.
- **La ruptura del contexto no genera notas de tradecraft**, igual que el contexto de inyección en SQLi: va entera a matriz. La única excepción es el valor "sin ruptura", que **es** [[Argument injection - abuso de flags]].

**Telemetría: primer artefacto web granular.** [[Proceso hijo del servidor web]]. Hasta ahora todo el lado web colgaba de [[Log de acceso del servidor web]], que no ve el cuerpo de la petición ni lo que el servidor ejecuta — o sea, no veía este dominio en absoluto. Es el primer paso para deshacer el problema de fondo: veinte variantes de tradecraft apuntando a un único artefacto genérico no son una bisagra, son una etiqueta.

**Hueco declarado:** [[Argument injection - abuso de flags]] es la única variante del vault cuya huella en el árbol de procesos es **indistinguible de la operación normal**. Está anotada como tal en el MOC y en la nota de telemetría; detectarla exige línea base por aplicación, no una regla portable.

### 2026-08-06 — Dominio SSRF

Cinco ejes: retorno × destino × esquema × bypass del filtro × impacto.

**Decisión: la superficie no es eje, es matriz.** Dónde nace el SSRF —parámetro, cabecera, webhook, renderizador de PDF, descubrimiento de OAuth— se evaluó como sexto eje y se rechazó: es catálogo de reconocimiento, no criterio de decisión. Subirlo a eje habría multiplicado notas por combinación, que es lo que prohíbe la regla 2. Vive entero en [[SSRF superficies - matriz de referencia]].

**Decisión: el árbol de destino va antes que el de canal.** Es el único dominio del vault donde se invierte el orden, y el motivo es de rentabilidad, no de taxonomía: [[SSRF - metadatos de instancia cloud]] cuesta una petición y termina el trabajo, mientras que [[SSRF - escaneo de la red interna]] cuesta cientos y devuelve topología. Barrer antes de probar `169.254.169.254` es el error caro del dominio, y el MOC lo dice explícito.

**Decisión: la nube no se separa.** Se evaluó sacar los metadatos de instancia a un dominio propio —los tres proveedores tienen endpoints, defensas y cadenas de escalada distintas— y se descartó: partiría el impacto más jugoso fuera del MOC que lo produce. Las diferencias por proveedor son sintaxis, y la sintaxis va a matriz. La escalada **posterior** con las credenciales sí es otro dominio, y queda anotada como hueco.

**Ciego no implica bajo impacto**, al revés que en SQLi y command injection. Con `gopher`, un SSRF sin retorno llega a RCE: escribir en Redis no necesita ver la respuesta. Está marcado en los dos árboles porque contradice la intuición que dejan los dominios anteriores.

**Telemetría:** [[Conexión saliente del servidor de aplicación]], segundo artefacto web granular. Cubre el punto que [[Consulta DNS saliente]] no ve — el SSRF a destino interno no genera consulta DNS ni cruza el perímetro, así que la telemetría de borde es ciega justo para el caso más grave.

**Deuda declarada:** el MOC enlaza `CWE-611 - XML External Entity`, que todavía no existe. Es enlace roto a propósito, igual que `T1558.003 - Kerberoasting` en el MOC de AD: marca el hueco en el grafo en vez de esconderlo.

### 2026-08-06 — Dominio XXE

Cuatro ejes: canal × mecanismo × obstáculo × impacto. El formato de entrada va a matriz, mismo criterio que la superficie en SSRF.

**El mecanismo sí es eje, el formato no.** Entidad general, entidad de parámetro y XInclude no son sintaxis distinta de lo mismo: cambian qué se puede hacer y bajo qué condiciones. XInclude en particular funciona sin `DOCTYPE`, que es justo lo que queda cuando la app inserta la entrada en un XML propio, y por eso tiene nota de criterio propia. El formato de entrada —SOAP, SVG, OOXML, SAML— es catálogo de reconocimiento y va entero a matriz.

**Deuda taxonómica saldada.** [[File upload - XXE por archivo]] pasó de `CWE-434` a [[CWE-611 - XML External Entity]]. Era el caso que hizo explícita la regla: **la `clase:` es la vulnerabilidad, no el vector de entrada**. La subida es cómo llega el XML; la vulnerabilidad es que el parser resuelve entidades. El MOC de upload lo sigue indexando —la navegación no depende de la taxonomía— y ahora ambos MOC se referencian.

Queda la otra mitad de esa deuda: [[LFI - phar deserialization]] sigue colgando de `CWE-98` y le corresponde `CWE-502`, que necesita el dominio de deserialización.

**Telemetría:** [[Log de errores del servidor web]], tercer artefacto web granular. Es el par complementario del log de acceso —uno registra qué se pidió, el otro qué se rompió— y es donde vive todo el reconocimiento fallido, que es la mayor parte de un ataque.

**Hueco de fuente, no de contenido.** Un XXE de lectura local con `file://` **no emite nada**: sin conexión de red, sin proceso hijo, sin error. Ninguna fuente por defecto lo ve. Es el primer caso del vault donde el hueco defensivo no se cierra escribiendo una detección, porque no hay artefacto que consumir — haría falta inspección del cuerpo de la petición o instrumentación del parser. Anotado como tal en el MOC.

## Pendientes

### Inmediatos

- [x] `900-meta/consultas.py` — las siete consultas corriendo, verificadas contra las notas semilla
- [x] Setup nvim: `obsidian.nvim` v3.16.6 + `render-markdown.nvim` sobre LazyVim ([[Puesta a punto de Obsidian]])
- [ ] Crear el vault de engagements, cifrado, fuera de este árbol (decidir ubicación y método: gocryptfs / LUKS / repo con git-crypt)

### Contenido

- [ ] **Cara azul de web — el pendiente de fondo.** Veinte variantes de tradecraft emiten [[Log de acceso del servidor web]] y ninguna detección lo consume: `consultas.py huecos` lo canta. Dos trabajos distintos: granular la telemetría web (empezado con [[Proceso hijo del servidor web]]; faltan log de errores, log de queries, WAF, `report-uri` de CSP, auditoría de escritura en la raíz web) y escribir las detecciones. Mientras esto no exista, la regla 3 del `CLAUDE.md` no se cumple y el vault fusionado no rinde más que dos separados
- [ ] Completar los ejes de SQLi que faltan (ver huecos en [[MOC - SQL injection]])
- [ ] Dominios web que siguen, por orden: control de acceso/IDOR → autenticación y sesión → deserialización → CSRF → SSTI
- [ ] **Deuda taxonómica:** [[LFI - phar deserialization]] cuelga de `CWE-98` y le corresponde `CWE-502`. La `clase:` apunta al vector de entrada, no a la vulnerabilidad. Se corrige cuando exista el dominio de deserialización. La mitad de XXE ya está saldada
- [ ] [[MOC - Active Directory]]: delegaciones y ADCS
- [ ] Telemetría de Kerberos: `4768`, `4769`, `4662`, `5145`

### Decisiones abiertas

- **Cuál se usa día a día.** Sin decidir. `Hack` **se queda como está** — no se toca, no se migra en bloque. Los dos modelos son incompatibles por diseño: acá los cheatsheets **no** son notas.
  - Postura recomendada: NewHack como vault de conocimiento; `Hack` congelado como capa de comandos que se consulta y no se edita. Cuando se trabaja un tema acá, se destila de `Hack` lo que corresponda — la decisión al zettel, la sintaxis a una matriz de `900-meta/`. Migración por demanda, nunca big-bang.
  - Lo que `Hack` gana: velocidad de recall durante un examen o engagement. Lo que NewHack gana: escala, caducidad modelada, consultas cruzadas y temario para clase.
- **Publicación para alumnos.** Descartada (2026-08-06). No hay plan de export, así que se quitó el campo `visibilidad:` de todas las notas — ver la entrada de bitácora de esa fecha.
