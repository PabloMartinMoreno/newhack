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
| Contenido rojo — web | Catorce dominios cerrados: SQLi, XSS, file inclusion, file upload, command injection, SSRF, XXE, control de acceso, autenticación, sesión, deserialización, CSRF, SSTI, OAuth |
| Contenido rojo — AD | Cerrado el núcleo: 8 técnicas ATT&CK, 8 tradecraft. Cada uno enlaza su artefacto de Windows |
| Contenido azul — web | 16 detecciones sobre 12 artefactos, todas en `estado: idea` |
| Contenido azul — fundamentos | 8 zettels + [[MOC - Fundamentos de detección]] |
| Contenido azul — Windows | 14 artefactos, 6 detecciones de AD. `huecos` vuelve a dar **cero** con AD adentro |
| Cheatsheets | 57 matrices: 48 web, 5 AD, 4 azules. Indexadas desde el MOC de su dominio |
| Validación en laboratorio | **Nada.** 82 tradecraft en `probado: nunca`, 22 detecciones en `estado: idea`. Es el cuello de botella real |
| Cliente | **nvim/LazyVim**, configurado y verificado. Obsidian y sus plugins descartados |
| Consultas cruzadas | `900-meta/consultas.py`, siete comandos. `higiene` valida además alias duplicados, MOC sin indexar y `forma:` de las detecciones |
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

### 2026-08-06 — Dominio Broken access control

Tres CWE en un MOC: [[CWE-639 - Authorization Bypass Through User-Controlled Key]] (IDOR), [[CWE-862 - Missing Authorization]] (vertical y `forced browsing`) y [[CWE-915 - Improperly Controlled Modification of Dynamically-Determined Object Attributes]] (mass assignment). Comparten lo único que importa a efectos operativos: **el mismo método de prueba**. La matriz actor × objeto × operación las encuentra a las tres, y separarlas obligaría a repetir ese método en tres mapas.

**El dominio no tiene payloads, y eso cambia la forma del MOC.** Es la primera divergencia estructural real desde que se fijó el patrón con SQLi. En los seis dominios anteriores la matriz principal es de sintaxis; acá es de **método**, porque no hay nada que romper: la petición es válida, la sesión legítima y la respuesta `200`. Lo único fuera de lugar es quién la manda. Consecuencia: [[Control de acceso - matriz de pruebas]] es la nota central del dominio y va antes que cualquier técnica en el orden de aprendizaje, al revés que en todos los demás.

**Los identificadores no predecibles no son mitigación**, y está escrito explícito en el MOC y en la CWE. Es la confusión más común del dominio: si el hallazgo se cierra cambiando un entero por un UUID, no se cerró — el control sigue ausente y el identificador se filtra igual.

**Telemetría:** [[Log de auditoría de la aplicación]], cuarto artefacto web y el primero que **no se activa: se construye**. Ninguna configuración lo enciende. Y hay un segundo problema encima: la mayoría de las implementaciones registran actor y acción pero no el **dueño del objeto** ni los **campos modificados**, que son justo los dos campos de los que depende toda la cara azul del dominio. Sin ellos queda un historial, no una detección.

**Hueco de tipo nuevo, otra vez.** [[Control de acceso - salto de contexto]] no se detecta con una regla sobre un evento sino verificando un invariante sobre una **secuencia** de eventos. El vault no modela ese tipo de detección: el esquema de `deteccion` asume una regla sobre un artefacto. Queda anotado; si aparece un segundo caso, habrá que revisar el esquema.

### 2026-08-08 — Dominio Autenticación

Se separó de **Gestión de sesión** en dos dominios encadenados, mismo precedente que file inclusion / file upload. Los ejes no se solapan: uno va de credenciales, el otro de tokens, y juntos serían un MOC de veinte notas con dos juegos de ejes que no se cruzan. Autenticación termina en el momento en que se emite la sesión; ahí empieza el otro.

**Organizado por fase del ciclo de vida, no por técnica.** Las fases se encadenan —lo que da una es el insumo de la siguiente— y saltearse la primera multiplica el costo de todas. Por eso el árbol raíz es una secuencia numerada y no una bifurcación, cosa que ningún otro MOC del vault hace.

Cuatro CWE, cada una con tradecraft propio: [[CWE-204 - Observable Response Discrepancy]], [[CWE-307 - Improper Restriction of Excessive Authentication Attempts]], [[CWE-287 - Improper Authentication]], [[CWE-640 - Weak Password Recovery Mechanism for Forgotten Password]].

**Spraying y stuffing son valores distintos del eje vector, no sinónimos.** La elección entre ellos depende de un solo dato —si hay corpus de credenciales filtradas— y las huellas son opuestas: spraying genera cientos de fallos, stuffing acierta a la primera y no genera ninguno. Esa oposición es lo que justifica dos notas en vez de una.

**Telemetría:** [[Log de autenticación de la aplicación]], quinto artefacto web. A diferencia de [[Log de auditoría de la aplicación]], este casi siempre existe; el problema es que nadie lo agrega.

**Tercer caso de detección sobre agregados.** Acá la señal no está nunca en el evento: un fallo de acceso no es nada, y la proporción de fallos contra cuentas inexistentes lo es todo. Sumado a [[Control de acceso - salto de contexto]] —que necesita invariantes sobre secuencias— ya son suficientes casos para decidir si el esquema de `deteccion` necesita distinguir reglas puntuales de funciones sobre ventana. Pendiente explícito, ver abajo.

Y un detalle que no encaja en ninguna tabla: en [[Autenticación - abuso de recuperación de contraseña]] el mejor detector **no es un artefacto de telemetría**, es una persona avisando que recibió un correo que no pidió. Es el único caso así en el vault.

### 2026-08-08 — Dominio Gestión de sesión

Cierra el par con [[MOC - Autenticación]]. Cinco CWE: [[CWE-384 - Session Fixation]], [[CWE-330 - Use of Insufficiently Random Values]], [[CWE-613 - Insufficient Session Expiration]], [[CWE-522 - Insufficiently Protected Credentials]], [[CWE-347 - Improper Verification of Cryptographic Signature]].

**El árbol se ordena por independencia de la víctima**, no por impacto ni por coste. Es el criterio que decide la viabilidad real: falsificar un JWT y predecir un token no necesitan a nadie —y el primero da cualquier cuenta, incluidas las administrativas—; robar necesita otra vulnerabilidad; fijar necesita que la víctima se autentique después, lo que implica ingeniería social y una ventana de tiempo. Ordenarlo por impacto habría puesto el robo primero, que es justo el que menos se sostiene solo.

**Segundo árbol, y no da acceso: da permanencia.** La rama de expiración se prueba siempre aunque el acceso venga de otro lado, porque responde una pregunta distinta — si el compromiso sobrevive a la reacción de la víctima. El caso del cambio de contraseña que no invalida sesiones es el que hay que destacar en un informe: anula la acción defensiva más elemental **en silencio**.

**Sin telemetría nueva, y eso es una señal buena.** Es el primer dominio que se cierra reutilizando artefactos existentes: todo cuelga de [[Log de autenticación de la aplicación]]. La contracara es que lo vuelve el punto único de fallo defensivo más claro del vault — vale correr `consultas.py spof` cuando existan las detecciones.

**Cuarto caso de detección que no es una regla sobre un evento.** [[Sesión - expiración insuficiente]] necesita verificar un invariante: ninguna sesión activa después del evento que la termina. Con cuatro casos en cinco dominios, revisar el esquema de `deteccion` deja de ser opcional y pasa a bloquear la primera detección web.

Y una asimetría que conviene recordar: en [[Sesión - token predecible]] la recolección es ruidosa y el uso es **invisible** — un token predicho es indistinguible de uno legítimo. Si la detección no está sobre la fase de pedir muchas sesiones, no está en ningún lado.

### 2026-08-08 — La cara azul de web, y el campo que la desbloqueó

`consultas.py huecos` daba **cero detecciones contra treinta emisores** al abrir la sesión. Ahora da `sin huecos`. Es el pendiente que estuvo arriba de todo desde la fundación, porque era el único que ponía en duda la fusión del vault.

**Primero hubo que arreglar el esquema.** Cuatro dominios seguidos —control de acceso, autenticación, sesión, y el agregado de todo el lado web— pidieron detecciones que no son una regla sobre un evento suelto, que era lo único que `deteccion` contemplaba. Se agregó `forma:` con cuatro valores y `ventana:` para los dos que la necesitan:

| Valor | Qué evalúa |
|---|---|
| `evento` | un registro en aislamiento |
| `correlacion` | dos o más registros que hay que unir |
| `agregado` | una función sobre una ventana: tasa, cardinalidad, proporción |
| `invariante` | una condición que nunca debería violarse sobre una secuencia |

No es taxonomía: cambia el lenguaje (Sigma alcanza para `evento`, no para `correlacion` ni `invariante`), cambia el coste (una ventana necesita estado) y cambia cómo se valida — **un disparo único valida una regla de `evento` y no dice nada de una de `agregado`**, que necesita volumen y línea base. `higiene` ahora lo verifica.

**Once detecciones nuevas**, cubriendo los siete artefactos web y las cuatro formas.

Lo que se aprendió escribiéndolas, y vale más que las reglas:

**Las detecciones que valen son de efecto, no de firma.** [[Intérprete de comandos como hijo del servidor web]] y [[Petición al servicio de metadatos de instancia]] son de altísima fidelidad porque anclan en una relación que no tiene explicación legítima. [[Payload de inyección en parámetros de la URL]] es la única de firma del vault, tiene `fidelidad: baja` declarada, y su propia nota dice que **no se despliega para alertar sino para cazar hacia atrás** — cualquier evasión de las matrices la anula, y mandar el payload por POST la evade sin saber nada.

**Tres reglas dependen de un campo que casi nunca está instrumentado.** [[Acceso a un objeto de otro usuario]] necesita el dueño del objeto; [[Cambio de privilegio fuera del flujo administrativo]] necesita los campos modificados; [[Fallos de acceso contra cuentas inexistentes]] necesita el motivo del fallo. Sin ellos las reglas no son difíciles: **son imposibles de escribir**. Las tres notas lo dicen en una sección propia, porque la recomendación defensiva de mayor retorno no es la regla sino instrumentar el campo.

**Dos técnicas rojas quedan sin detección posible y está declarado.** [[Argument injection - abuso de flags]] no produce ninguna anomalía en el árbol de procesos, y un XXE de lectura local con `file://` no emite absolutamente nada. No son huecos de contenido: son límites de las fuentes disponibles.

Todas quedan en `estado: idea` y sin `validada:`. Ninguna se probó en laboratorio, y eso es lo que ese campo significa.

### 2026-08-08 — Los tres artefactos que faltaban, y el hueco que `huecos` no veía

**Al ir a escribir la telemetría pendiente apareció un problema peor.** Tres notas de XSS —[[XSS - DOM-based]], [[XSS - mutation XSS]], [[XSS - CSP]]— tenían `telemetria: []` **vacío**. Es la regla 3 del `CLAUDE.md` incumplida, y `huecos` no lo veía por construcción: esa consulta recorre artefactos y pregunta quién los consume, así que una nota que no declara **ningún** artefacto es invisible para ella.

`higiene` ahora falla si un tradecraft no declara telemetría. El check que faltaba no era una mejora: era el que verifica la bisagra.

El vacío era honesto, además, y ahí está lo interesante: **XSS DOM-based no toca el servidor**. La carga viaja en el fragmento de la URL o se construye en el navegador, así que ninguna fuente del lado del servidor la ve. No había artefacto que declarar hasta ahora.

**Tres artefactos nuevos:**

- [[Informe de violación de CSP]] — el único del vault que **no lo emite un sistema propio** sino el navegador de la víctima. Es la única fuente que ve el lado del cliente, y por lo tanto la única que ve DOM-based y mXSS. Sus límites vienen de ahí: la emite un cliente no confiable, y el ruido de las extensiones del navegador puede sepultarla.
- [[Escritura de archivo en la raíz web]] — el de mejor relación coste/valor del vault. Barato de encender y difícil de evadir, porque es el **efecto compartido** de seis técnicas que no comparten ni payload ni vector: webshell, upload, LFI a RCE, `INTO OUTFILE` de SQLi, gopher a Redis, y el canal ciego de command injection.
- [[Registro del WAF]] — cubre el punto ciego estructural del lado web: [[Log de acceso del servidor web]] **no registra el cuerpo**, así que todo payload por POST era invisible. Es la única fuente que lo tapa sin instrumentar la aplicación. Vale como contexto, no como detección primaria: hereda todos los límites de las firmas.

**Cuatro detecciones más**, hasta 16. Dos hallazgos de escribirlas:

[[Archivo ejecutable nuevo en la raíz web]] cubre **seis técnicas con una sola regla** porque todas convergen en el mismo efecto. Es el mejor argumento del vault a favor de detectar efecto en vez de firma, y quedó escrito ahí.

[[Puntaje de anomalía alto sin bloqueo]] apunta a algo que se lee mal todo el tiempo: un WAF en modo detección produce **los mismos registros** que uno que bloquea. Sin distinguir el campo de acción, se leen como ataques frustrados cosas que llegaron enteras a la aplicación.

### 2026-08-08 — Dominio Deserialización

Cierra [[CWE-502 - Deserialization of Untrusted Data]], que había quedado como paraguas sin MOC al saldar la deuda del `phar`.

**El formato va a matriz, no a eje.** Decidido por precedente y sin brainstorming: es el mismo criterio que el motor en [[MOC - SQL injection]] y la shell en [[MOC - Command injection]]. PHP, Java, `pickle`, Ruby y .NET cambian el formato, las cadenas y la herramienta — no cambian ninguna decisión. Lo que decide es si hay gadget, si hay firma, y si alcanza con manipular sin ejecutar.

**El árbol está ordenado contra la fama del dominio.** "Deserialización" evoca `ysoserial` y RCE, y esa asociación hace descartar casos explotables. La rama que más veces resuelve —[[Deserialización - manipulación de objeto]]— no necesita ninguna cadena: un objeto de sesión con un campo de rol adentro es escalada completa. Por eso [[Deserialización - cadena de gadgets]] va **última** en el orden de aprendizaje, al revés de como suele enseñarse.

**Tres formatos ejecutan por diseño** —`pickle`, YAML con cargador inseguro, `node-serialize`— y no necesitan que ninguna biblioteca sea vulnerable. Buscar cadenas ahí es perder el tiempo, y está marcado en el árbol.

**Segundo dominio que se cierra sin escribir una sola detección.** [[Intérprete de comandos como hijo del servidor web]] lo detecta sin saber que hubo deserialización de por medio, y [[Cambio de privilegio fuera del flujo administrativo]] cubre la manipulación. Es la mejor evidencia acumulada de que detectar **efecto** en vez de firma paga: las reglas cubren técnicas que no existían cuando se escribieron.

Y una inversión incómoda para el defensor, anotada en el MOC: **lo fallido es más visible que lo exitoso**. Una cadena que no funciona lanza excepción; la que funciona, no. La ráfaga de excepciones de deserialización precede al intento que sale bien, y es la ventana de detección real.

### 2026-08-08 — Andamiaje azul: fundamentos y Windows

Cambio de propósito respecto de todo lo anterior. Hasta acá cada nota azul nació como contracara de una técnica roja concreta. Estas nacieron **primero**, para que haya dónde colgar lo que se aprenda en un curso.

**El diagnóstico que lo motivó:** el vault tenía once dominios web y dieciséis detecciones, y `100-notas/` tenía **una sola nota, de rojo**. No había ningún lugar para un concepto. `550-telemetria/` tenía doce artefactos y once eran web.

**Ocho zettels de fundamentos.** Ninguno es resumen de material externo: cada uno está destilado de algo con lo que este vault se chocó al construirse. `forma:` existe porque cuatro dominios seguidos lo pidieron; [[Un log sin identidad es un historial, no una detección]] existe porque tres reglas resultaron imposibles de escribir por falta de un campo; [[Ausencia de alertas no es ausencia de ataque]] existe porque dos técnicas rojas quedaron declaradas como no detectables.

**Catorce artefactos de Windows.** Sysmon (1, 3, 7, 8, 10, 11, 13, 22), Security (4624, 4625, 4688, 4768, 4769, 4662, 5145) y PowerShell 4104.

**Están declarados como andamiaje, y el MOC lo dice en un callout.** El campo *Quién lo emite* está en pendiente en casi todas, porque el lado rojo de Windows sigue siendo una sola nota. La instrucción explícita es **no rellenarlo de memoria**: una nota de telemetría que declara emisores que nadie observó es la misma clase de mentira que `probado:` existe para evitar.

**Dos MOC nuevos que no son de una tecnología ni de una clase de vulnerabilidad**, que es una forma que el vault no tenía: [[MOC - Fundamentos de detección]] ordena los conceptos como secuencia de lectura y da dos árboles —por dónde empezar a detectar algo, y qué revisar cuando una regla no sirve—; [[MOC - Telemetría de Windows]] ordena las fuentes por relación valor/coste y responde "quiero ver X, qué fuente".

Un detalle que quedó anotado en el segundo y vale la pena: **el único ciclo rojo↔azul cerrado del vault sigue siendo el de LSASS**. Es el único lugar donde se puede seguir una técnica, ver qué artefacto emite y leer la detección que lo consume. Ese recorrido es el modelo del vault funcionando, y hay exactamente uno.

### 2026-08-08 — El lado rojo de Active Directory

Corrección de rumbo pedida por el usuario: **no le toca a él completar campos**. El error fue tratar "qué técnica emite qué artefacto" como si fuera `probado:` —una observación personal que no se puede inventar— cuando en realidad es conocimiento documentado, o sea la nota que me toca escribir a mí. Lo que faltaba no eran campos para que él llene: era el **lado rojo de Windows** entero.

Ocho técnicas ATT&CK y ocho tradecraft, organizados por **lo que tenés** —nada, una credencial, admin local, admin de dominio— y no por técnica, porque en AD cada nivel de acceso abre unas ramas y cierra otras.

Con esto, [[Sysmon EID 10 - ProcessAccess]] deja de sostener una sola técnica: ahora los catorce artefactos de Windows que antes eran andamiaje tienen emisores reales declarados, escritos y no supuestos. El campo *Quién lo emite* se llenó solo al escribir el rojo, que es como tenía que ser.

Tres lecciones del dominio quedaron en el MOC, y son las que más enseñan de detección:

**Ataque fuera de línea → se detecta la petición, no el ataque.** Roasting rompe el material sin conexión; la única ventana es pedir los tickets.

**Uso invisible → se detecta el paso anterior.** Pasar el ticket es Kerberos legítimo; lo que se ve es robarlo de memoria, que es el mismo acceso a LSASS que ya tiene detección. Es el mismo principio que en [[Sesión - token predecible]] del lado web.

**Fidelidad altísima puede no dejar rastro si la fuente está mal configurada.** [[DCSync]] no emite nada si la auditoría no está sobre el objeto raíz del dominio — el segundo paso que nadie hace. Es el caso más claro de [[Ausencia de alertas no es ausencia de ataque]] en todo el vault.

**`huecos` ahora marca los artefactos de Windows**, y está bien: el rojo de AD existe y las detecciones azules no. Es el mismo estado que tenía el web antes de escribir su cara azul, y el trabajo que HTB va a alimentar directamente.

### 2026-08-08 — La cara azul de Active Directory

Cerrada igual que la de web: escribir las detecciones que consumen los artefactos que el rojo de AD dejó emitiendo. `huecos` volvió a dar cero, ahora con AD dentro de la cuenta.

Seis detecciones. Lo que enseñan sobre por qué las fuentes de Kerberos importan tanto:

**Dos de alta fidelidad y forma `evento`**, porque su condición casi no ocurre legítimamente: [[Solicitud de TGT sin preautenticación]] (AS-REP roasting) y [[Replicación de directorio desde un origen no autorizado]] (DCSync). No se evaden bajando el volumen — no dependen del volumen.

**La de DCSync tiene el requisito previo más severo del vault.** Depende de que la auditoría esté configurada **sobre el objeto raíz del dominio**, no solo habilitada. Sin ese segundo paso, la técnica de mayor fidelidad del dominio no emite nada. La nota lo pone en un callout: verificar que el evento se genera es el primer paso, no escribir la lógica.

**La de golden ticket llega tarde por diseño**, y quedó escrito. Cuando el ticket forjado se usa, el compromiso que consiguió la clave ya ocurrió. La regla detecta el uso —un ticket de servicio sin ticket inicial previo, forma `invariante`— pero la prevención está aguas arriba, en el robo de la clave.

Dos artefactos secundarios del volcado de LSASS —creación de proceso y del archivo de volcado— se cerraron **sin regla nueva**: se agregaron como telemetría corroborante a la detección de acceso a LSASS que ya existía, que es lo que son. Inventar dos reglas débiles habría sido peor que declarar la corroboración.

Queda una técnica de AD sin detección **a propósito**: [[Enumeración LDAP del directorio]]. Es el punto ciego del dominio —tráfico legítimo indistinguible— y está declarado como hueco en el MOC, no escondido. Mismo criterio que argument injection y el XXE local del lado web: nombrar lo que no se detecta es parte del trabajo.

### 2026-08-10 — El campo que mentía, y los cheatsheets que faltaban

Sesión de revisión, no de contenido nuevo. Salieron tres cosas y las tres eran de honestidad del vault, no de cobertura.

**`probado:` mentía en 63 de 67 notas.** Cuarenta y dos decían `2026-08-06` y veintiuna `2026-08-08`: exactamente los días en que se escribieron. Ninguna técnica del vault se corrió nunca en un laboratorio. El campo existe para que el conocimiento caduco se vea, y relleno con la fecha de escritura hacía lo contrario — `revalidacion` daba "sin backlog" y en febrero de 2027 iba a escupir 63 falsos de golpe.

Las 67 pasaron a `probado: nunca`, que es el valor honesto y ahora el que trae la plantilla. Tres consecuencias en la herramienta:

- `higiene` rechaza un `probado:`/`validada:` que no sea `nunca` ni fecha ISO pasada. Sin ese control, una fecha mal escrita caía en el mismo hueco que "nunca probado" y no se distinguía de una nota recién nacida.
- `revalidacion` **resume** las nunca probadas en una línea y las lista con `--nunca`. A 67 filas la consulta dejaba de leerse, y el backlog que exige trabajo es el de las que sí tienen fecha y venció.
- Mientras `probado:` sea `nunca`, `contexto:` es el entorno **contra el que hay que probarla** — plan de laboratorio, no registro. Queda escrito en el esquema.

**Doce checkboxes de "Huecos conocidos" estaban vencidos.** Seis MOCs web decían "Cara azul sin escribir" dos días después de escribirla; [[MOC - Active Directory]] decía que no había ninguna detección de AD cuando hay seis; [[MOC - Telemetría de Windows]] daba el lado rojo por inexistente. Es el mismo desfase que ya había tenido esta bitácora, ahora en la capa de navegación, que es peor: el MOC es lo primero que se lee. Barridos y reemplazados por lo que de verdad falta, que en casi todos los casos es **validación en laboratorio**, no contenido.

**Los cheatsheets estaban repartidos mal.** Cuarenta y una matrices y **cuarenta eran de web**: cero de AD, cero del lado azul. El usuario aclaró que el producto que usa es la matriz, así que el desbalance no era cosmético — era la mitad de lo que usa, faltando.

Nueve matrices nuevas. Cinco de AD, ordenadas por la misma pregunta que ordena su MOC —qué tengo—: [[AD enumeración - matriz de referencia]], [[AD roasting - matriz de referencia]], [[AD volcado de credenciales - matriz de referencia]], [[AD movimiento lateral - matriz de referencia]], [[AD persistencia - matriz de referencia]].

Cuatro azules, que es la novedad de forma: **es la primera vez que el vault tiene sintaxis del lado defensivo**. [[Sigma - matriz de referencia]], [[KQL - matriz de referencia]], [[Sysmon - matriz de configuración]] y [[Detección por forma - matriz de referencia]].

La última es la que importa y no existía en ningún corpus externo: traduce cada valor de `forma:` a una consulta concreta. Escribirla dejó explícito algo que estaba implícito desde que se agregó el campo — **Sigma no puede expresar `invariante`**. No hay tipo de correlación que diga "esto no debería existir sin aquello", y las tres reglas de esa forma van obligatoriamente en KQL con `leftanti`. Es la razón concreta por la que `logica:` es un campo por detección y no una constante del vault.

### 2026-08-10 — Dominios CSRF y SSTI

Los dos siguientes del roadmap de web. Ninguno necesitó telemetría ni detección nueva, y eso ya no es casualidad: son el tercero y el cuarto que se cierran reutilizando reglas existentes.

**CSRF — el dominio que parece muerto y no lo está.** Lo que mató `SameSite` por defecto fue el `POST` de origen cruzado, que era la única forma que se enseñaba. Quedaron vivas cuatro, y son las que aparecen en aplicaciones modernas: acciones por `GET`, cookies con `SameSite=None` explícito, peticiones desde subdominios —que para las cookies no son otro sitio— y API con sesión por cookie.

El eje que genera notas es **qué defensa hay que romper**, y solo ese. La entrega —`GET`, autoenvío, `text/plain`, multipart— va entera a matriz por el mismo criterio que la shell en command injection: cambia el HTML, no cambia la decisión. Cinco tradecraft, uno por defensa.

Dos cosas que quedaron escritas en el MOC y valen más que las técnicas:

- **La primera pregunta descarta el dominio entero.** Si la sesión viaja en una cabecera y no en una cookie, el navegador no adjunta nada solo y no hay CSRF. Una petición para saberlo.
- **La severidad va de informativa a crítica con la misma vulnerabilidad.** Es el dominio donde esa distancia es mayor, y por eso tiene un segundo árbol que no es de técnica sino de impacto. El CSRF de inicio de sesión es el que más se pasa por alto: no le saca nada a la víctima, la deja operando en la cuenta del atacante.

**SSTI — se enseña al revés.** La imagen de "SSTI igual a RCE" produce dos errores caros: tirar payloads antes de identificar el motor, y abandonar el hallazgo cuando no se llega a ejecutar. El árbol está ordenado contra las dos: identificar es obligatorio y **pedir el contexto va antes que escalar**, porque cuesta una petición y devuelve la clave de firma con frecuencia suficiente. Con la clave se falsifican sesiones sin tocar el sistema operativo — o sea que la rama "sin ejecución" es toma de cuenta, no un consuelo.

El eje es la **capacidad del motor** —ejecución directa, entorno restringido, sin lógica, del lado del cliente—, no el motor. Fue la decisión más difícil del dominio: el motor cambia el payload por completo, que es justo el argumento que lo haría parecer eje. No lo es, porque no cambia la decisión; lo que decide es qué capacidad expone. Mismo precedente que el motor de base de datos en [[MOC - SQL injection]].

**Una ventaja defensiva rara, anotada en el MOC.** En casi todos los dominios el atacante puede saltear el reconocimiento si ya sabe lo que busca. En SSTI no: identificar el motor exige provocar errores, y cada payload equivocado deja una excepción con el nombre de la plantilla. La ventana de detección es **anterior** al ataque exitoso, no simultánea — y la cubre [[Ráfaga de errores del servidor desde un mismo origen]], que ya existía.

**Un límite de fuente nuevo:** [[SSTI - lectura sin ejecución]] no emite absolutamente nada. No nace proceso, no sale conexión, no hay excepción. Es el tercer caso del vault —con el XXE local y [[Argument injection - abuso de flags]]— donde el hueco no se cierra escribiendo una detección porque no hay artefacto que consumir.

Cuatro matrices nuevas: [[CSRF entrega - matriz de referencia]], [[CSRF bypass - matriz de referencia]], [[SSTI - matriz de identificación]] y [[SSTI payloads - matriz de referencia]].

### 2026-08-11 — Dominio OAuth, y el primero sin CWE propia

El siguiente del roadmap, y el que puso a prueba la regla 7 del `CLAUDE.md` de verdad.

**OAuth no es una vulnerabilidad, así que no tiene nota paraguas.** Es un protocolo con seis puntos donde se rompen cosas distintas, y cada nota cuelga de la clase que le corresponde: `CWE-601` la redirección, `CWE-352` la falta de `state`, `CWE-287` el flujo implícito y PKCE, `CWE-347` el `id_token`, `CWE-918` el registro dinámico. **Cinco de las seis ya existían** por otros dominios; hubo que escribir una sola técnica nueva.

Es el mejor caso acumulado a favor de que la `clase:` sea la vulnerabilidad y no el vector. La navegación no sufre —se llega por el MOC— y a cambio `cobertura` sigue diciendo la verdad: no aparecen seis técnicas nuevas con una nota cada una, aparecen seis notas más colgando de clases que ya tenían contenido.

**El eje es la fase del flujo que se rompe.** El flujo en sí —código, implícito, híbrido— va a matriz por el mismo criterio que el motor en SQLi: cambia qué parámetros hay y por dónde vuelven los datos, no cambia qué se decide.

**El árbol se ordena por requisito, no por impacto**, y es la primera vez que se hace así. Las ramas que no necesitan víctima —flujo implícito, y el SSRF contra el proveedor— van antes que las de mayor impacto, porque las que dependen de que alguien abra un enlace tienen un techo de severidad que hay que reflejar en el informe. Ordenar por impacto lleva a construir cadenas que después no se pueden demostrar.

Tres cosas que quedaron escritas y valen más que las técnicas:

**PKCE no protege lo que la gente cree.** Protege el código en tránsito, no la dirección a la que se manda. Sin una primitiva previa para ver el código, esa rama es teórica — y por eso va última con una condición explícita.

**La redirección abierta del propio cliente vale tanto como una validación laxa de `redirect_uri`.** El código llega a la dirección registrada y el cliente lo reenvía. Nadie la busca porque no está en la implementación de OAuth, y en aplicaciones grandes es la vía que más veces resuelve.

**Primer dominio donde la mejor telemetría pertenece a un tercero.** Cuatro de las siete firmas viven en el registro del proveedor de identidad, que casi nunca es el sistema auditado. Sin acceso a esos registros, la mitad del dominio es ciega por construcción, y el informe tiene que decirlo en vez de recomendar una regla que nadie puede desplegar.

Y una vuelta de tuerca sobre [[Un log sin identidad es un historial, no una detección]]: tres ramas se detectarían registrando el sujeto del token junto al usuario autenticado. Si la aplicación distinguiera esos dos valores **no sería vulnerable** — la ausencia del campo es a la vez la vulnerabilidad y el motivo por el que no se detecta. Es la forma más pura de ese zettel que apareció hasta ahora.

Quinto dominio consecutivo que se cierra sin telemetría ni detección nueva. Tres matrices: [[OAuth - matriz de reconocimiento]], [[OAuth redirect_uri - matriz de referencia]] y [[OAuth tokens - matriz de referencia]].

## Pendientes

### Inmediatos

- [x] `900-meta/consultas.py` — las siete consultas corriendo, verificadas contra las notas semilla
- [x] Setup nvim: `obsidian.nvim` v3.16.6 + `render-markdown.nvim` sobre LazyVim ([[Puesta a punto de Obsidian]])
- [ ] Crear el vault de engagements, cifrado, fuera de este árbol (decidir ubicación y método: gocryptfs / LUKS / repo con git-crypt)

### Contenido

- [x] ~~Cara azul de web~~ — cerrada el 2026-08-08. `huecos` da `sin huecos`. La regla 3 del `CLAUDE.md` se cumple y la fusión del vault se justifica
- [ ] **Laboratorio — el cuello de botella, y ahora el único.** 67 tradecraft en `probado: nunca` y 22 detecciones en `estado: idea`. Empezar por las **7 detecciones de `forma: evento`**: se validan con un disparo. Las 10 de `agregado` necesitan volumen **y línea base**, que es el trabajo caro, y las 3 de `invariante` necesitan reproducir una secuencia entera. Pasar a `borrador` y poner `validada:` lo que se pruebe
- [x] ~~Telemetría web que falta~~ — [[Registro del WAF]], [[Informe de violación de CSP]] y [[Escritura de archivo en la raíz web]], escritos el 2026-08-08
- [x] ~~Cheatsheets de AD y del lado azul~~ — nueve matrices el 2026-08-10. Era el desbalance más grande del vault: 40 de 41 matrices eran de web
- [ ] Completar los ejes de SQLi que faltan (ver huecos en [[MOC - SQL injection]])
- [x] ~~CSRF y SSTI~~ — cerrados el 2026-08-10, sin telemetría ni detección nueva
- [x] ~~OAuth/OIDC~~ — cerrado el 2026-08-11. Primer dominio sin CWE propia: cada nota cuelga de su clase real
- [ ] Dominios web que siguen, por orden: prototype pollution (`CWE-1321`) → CORS mal configurado → SAML → Expression Language de Java
- [x] ~~Revisar el esquema de `deteccion`~~ — resuelto con `forma:` y `ventana:` el 2026-08-08
- [x] ~~Deuda taxonómica~~ — saldada. [[File upload - XXE por archivo]] → `CWE-611`, [[LFI - phar deserialization]] → `CWE-502`. En ambos casos la `clase:` apuntaba al vector de entrada y ahora apunta a la vulnerabilidad; el MOC de origen los sigue indexando
- [ ] [[MOC - Active Directory]]: delegaciones, confianzas y relay NTLM. ADCS existe como técnica y como matriz, falta el resto de las plantillas abusables
- [ ] Ocho artefactos de Windows siguen sin emisor ni detección: Sysmon 3, 7, 8, 13, 22, PowerShell 4104, Windows 4625 y 4688
- [ ] **Carpetas que existen y no se usan**: `750-hallazgos/` (1 nota, y es la de mayor retorno en un engagement), `400-entidades/` (1, mientras ysoserial, BloodHound, mimikatz y responder aparecen 20 veces como texto plano), `450-superficies/` (1, ninguna web), `200-fuentes/` (3, todas de un mismo sitio)

### Decisiones abiertas

- **Cuál se usa día a día.** Sin decidir. `Hack` **se queda como está** — no se toca, no se migra en bloque. Los dos modelos son incompatibles por diseño: acá los cheatsheets **no** son notas.
  - Postura recomendada: NewHack como vault de conocimiento; `Hack` congelado como capa de comandos que se consulta y no se edita. Cuando se trabaja un tema acá, se destila de `Hack` lo que corresponda — la decisión al zettel, la sintaxis a una matriz de `900-meta/`. Migración por demanda, nunca big-bang.
  - Lo que `Hack` gana: velocidad de recall durante un examen o engagement. Lo que NewHack gana: escala, caducidad modelada, consultas cruzadas y temario para clase.
- **Publicación para alumnos.** Descartada (2026-08-06). No hay plan de export, así que se quitó el campo `visibilidad:` de todas las notas — ver la entrada de bitácora de esa fecha.
