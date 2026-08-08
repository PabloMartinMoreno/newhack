---
tipo: moc
dominio: web
aliases:
  - MOC XXE
  - XML External Entity
tags:
  - dominio/web
---

# MOC - XXE

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-611 - XML External Entity]]. Los payloads, en las matrices de `900-meta/`. Acá vive **la decisión**.

XXE es el dominio donde el trabajo caro es **encontrarlo**, no explotarlo. Los payloads son cuatro y están escritos hace veinte años; lo que cuesta es darse cuenta de que hay un parser de XML detrás de algo que no parece XML. Por eso el orden de este mapa arranca por la superficie.

| Eje | Valores |
|---|---|
| Canal | directo · por error · fuera de banda |
| Mecanismo | entidad general · entidad de parámetro + DTD externa · XInclude |
| Formato de entrada | XML · SOAP · SVG · OOXML · SAML · embebido → matriz |
| Obstáculo | DTD deshabilitado · sin `DOCTYPE` · sin egress · el archivo rompe el XML |
| Impacto | lectura local · SSRF · listado de directorios · RCE · DoS |

## Árbol de decisión — ¿hay parser?

```
Entidad interna: <!ENTITY test "OK">  →  ¿se expande?
├─ Sí → el DTD está habilitado, seguir al árbol de canales
└─ No
   ├─ ¿La entrada va embebida en un XML ajeno? → [[XXE - XInclude]]
   └─ ¿Probaste cambiar el Content-Type a XML? → [[XXE formatos - matriz de referencia]] § 2
```

La prueba con entidad **interna** va primera porque no toca la red y separa dos cosas que se confunden todo el tiempo: "el DTD está deshabilitado" y "las entidades externas están deshabilitadas". Son opciones distintas y la segunda deja el canal por error abierto.

## Árbol de decisión — elegir canal

```
¿El valor de la entidad vuelve en la respuesta?
├─ Sí → [[XXE - canal directo]]
└─ No
   ├─ ¿Hay egress de red?
   │  ├─ Sí → [[XXE - canal fuera de banda]]
   │  └─ No
   │     ├─ ¿Vuelven errores detallados? → [[XXE - canal por error]]
   │     └─ No → sin canal: confirmar por interacción y reportar como ciego
   └─ ¿La app inserta tu entrada en un XML propio? → [[XXE - XInclude]]
```

Dos diferencias con [[MOC - SSRF]], que es el dominio más parecido:

**Sin red todavía queda dominio.** El canal directo y XInclude con `file://` leen archivos sin abrir una sola conexión. En SSRF, sin red no queda nada; acá el egress es una comodidad, no un requisito.

**El error es un canal de primera, no un consuelo.** Es la rama que salva el caso más endurecido —sin reflejo y sin egress— y depende de una condición que no es de red sino de configuración: que la app devuelva errores detallados.

## Árbol de decisión — obstáculos

```
¿Qué te está bloqueando?
├─ El archivo rompe el XML   → php://filter base64      → § El archivo rompe el XML
├─ DOCTYPE rechazado         → XInclude / UTF-16        → § DOCTYPE bloqueado
├─ Filtro de <!ENTITY        → PUBLIC / codificación    → § Filtro de cadena
├─ Sin egress                → directo / error / file:// → § Sin egress
└─ file:// filtrado          → netdoc: / jar: / php://   → § El esquema está filtrado
```

La primera rama es la que más tiempo hace perder, y no es un filtro: es que `/etc/passwd` funciona y cualquier archivo con `<` o `&` no. Se pide todo en base64 y desaparece el problema.

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[XXE formatos - matriz de referencia]] | Dónde hay XML: SOAP, SVG, OOXML, SAML, cambio de tipo de contenido, embebido |
| [[XXE payloads - matriz de referencia]] | Confirmación, canal directo, la DTD de exfiltración, por error, XInclude, impacto |
| [[XXE evasión - matriz de referencia]] | Base64, sin `DOCTYPE`, filtros de cadena, sin egress, esquemas alternativos |

## Orden de aprendizaje

1. [[CWE-611 - XML External Entity]] — qué es, y las tres piezas que no hay que mezclar
2. [[XXE formatos - matriz de referencia]] — encontrarlo, que acá es la mayor parte del trabajo
3. [[XXE - canal directo]] — el caso feliz, fija el modelo mental
4. [[XXE - canal fuera de banda]] — por qué hacen falta dos archivos, que es lo que cuesta entender
5. [[XXE - canal por error]] — el mismo mecanismo apuntando a una ruta local
6. [[XXE - XInclude]] — rompe la intuición de que sin `DOCTYPE` no hay dominio
7. Impacto: [[MOC - SSRF]] como continuación natural

El punto 4 es el cuello de botella conceptual del dominio. Hasta entender **por qué** la declaración anidada tiene que vivir en una DTD externa, el payload de exfiltración parece magia y no se sabe adaptar cuando falla.

## Relación con otros dominios

- [[MOC - SSRF]] — un parser con entidades externas es una máquina de SSRF, y en la práctica ese impacto suele valer más que la lectura de archivos. [[XXE payloads - matriz de referencia]] § 5 apunta directo a los destinos de aquel dominio.
- [[MOC - File upload]] — [[File upload - XXE por archivo]] es el cruce: SVG y los formatos de oficina son XML, y la subida es el vector más común del dominio.
- [[MOC - File inclusion]] — comparten el wrapper `php://filter` con el mismo propósito exacto: leer un archivo sin que su contenido rompa el contexto donde se inserta.
- [[MOC - Command injection]] — [[Proceso hijo del servidor web]] no ve nada de esto: XXE se resuelve **dentro** del intérprete y no crea procesos. Es el hueco que aquella nota de telemetría declara.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Canal directo, `file://` | — | **Ninguna por defecto.** Sin red, sin proceso, sin error |
| Canal directo, `http://` | [[Conexión saliente del servidor de aplicación]] | Petición saliente desde el proceso del parser |
| Fuera de banda | [[Conexión saliente del servidor de aplicación]] | **Dos conexiones seguidas**: la DTD y después el dato |
| Por error | [[Log de errores del servidor web]] | Excepción del parser citando una ruta que contiene un archivo del sistema |
| XInclude | [[Log de acceso del servidor web]] | La URL del espacio de nombres de XInclude en un parámetro |

La primera fila es el problema serio del dominio: **un XXE de lectura local no emite absolutamente nada** que las fuentes por defecto recojan. No hay conexión, no hay proceso hijo, no hay error. Detectarlo exige inspeccionar el cuerpo de la petición, que es justo lo que [[Log de acceso del servidor web]] no hace.

La cuarta fila compensa: el canal por error es de los indicadores más limpios que existen, porque ninguna operación legítima produce una excepción citando `/etc/passwd`.

## Huecos conocidos

- [x] Los tres canales — directo, error, fuera de banda
- [x] Mecanismo — entidades generales, de parámetro y [[XXE - XInclude]]
- [x] Formatos de entrada — en [[XXE formatos - matriz de referencia]]
- [x] Obstáculos — en [[XXE evasión - matriz de referencia]]
- [ ] **Cara azul sin escribir.** Tres artefactos de telemetría existen y ninguna detección los consume
- [ ] **Lectura local sin telemetría.** El hueco no es de contenido, es de fuente: no existe artefacto que vea un XXE con `file://`. Requeriría inspección del cuerpo de la petición o instrumentación del parser
- [ ] DoS por expansión de entidades — documentado como riesgo en [[XXE payloads - matriz de referencia]], sin nota propia por estar fuera de alcance en la práctica
