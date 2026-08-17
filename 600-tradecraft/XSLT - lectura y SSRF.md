---
tipo: tradecraft
clase: "[[CWE-94 - Improper Control of Generation of Code]]"
eje: capacidad-del-procesador
implementacion: "Usar document() y unparsed-text() para leer archivos locales o alcanzar destinos internos desde la transformación"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Consulta DNS saliente]]", "[[Log de errores del servidor web]]"]
requisitos: [inyección-en-una-transformación-xslt, document-habilitado]
coste: bajo
alternativas: ["[[XSLT - ejecución por funciones de extensión]]", "[[XXE - canal directo]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - XSLT file read
  - XSLT SSRF
tags:
  - dominio/web
---

# XSLT - lectura y SSRF

## Cuándo lo elijo

Es la rama a probar primero después de confirmar la inyección de XSLT, porque es la de menor requisito: no necesita que las funciones de extensión estén habilitadas, solo que el procesador permita `document()` o `unparsed-text()` —que muchos traen activos por defecto—. Se reconoce con las pruebas de [[XSLT - matriz de identificación]]: si `system-property('xsl:vendor')` devuelve el nombre del procesador, hay inyección.

El objetivo es leer archivos del servidor o alcanzar destinos internos. Si el procesador expone funciones de extensión y el objetivo es ejecución, la rama es [[XSLT - ejecución por funciones de extensión]].

## Por qué funciona

XSLT tiene funciones para incorporar recursos externos a la transformación, pensadas para componer documentos, y el atacante las apunta a lo que quiere:

**Lectura de archivos:**
```xml
<xsl:value-of select="unparsed-text('/etc/passwd')"/>
<xsl:copy-of select="document('file:///etc/passwd')"/>
```

`unparsed-text()` lee texto plano; `document()` lee y parsea XML. Con ellas se leen archivos de configuración, claves, código fuente — es lectura arbitraria, y cruza con [[MOC - XXE]] porque los dos abusan que un parser de XML lea recursos locales.

**SSRF:**
```xml
<xsl:value-of select="document('http://169.254.169.254/latest/meta-data/')"/>
<xsl:value-of select="document('http://interno:8080/')"/>
```

`document()` con una URL hace que el servidor la pida, así que es SSRF, y se sigue por [[MOC - SSRF]] con su misma economía: metadatos de instancia primero, red interna después.

**Divulgación de versión**, para saber qué procesador y qué capacidades hay:
```xml
<xsl:value-of select="system-property('xsl:vendor')"/>
<xsl:value-of select="system-property('xsl:version')"/>
```

Los payloads por procesador están en [[XSLT payloads - matriz de referencia]]. `document()` funciona casi en todos; `unparsed-text()` necesita XSLT 2.0.

## Cómo falla

Falla cuando el procesador tiene **deshabilitado el acceso a recursos externos** —`document()` y `unparsed-text()` bloqueados—, que es la mitigación correcta y cada vez más el valor por defecto en procesadores endurecidos.

Falla cuando el procesador es XSLT 1.0 y solo se quería `unparsed-text()` —que es 2.0—; ahí queda `document()` para XML.

Y el SSRF falla si el egress está restringido, igual que cualquier SSRF, dejando solo la lectura local.

## Coste

Bajo. Confirmada la inyección, leer un archivo o disparar el SSRF es una expresión. La divulgación de versión es la primera petición y decide todo lo demás —qué procesador, qué capacidades—.

Es la rama de mejor relación coste/valor del dominio: sin necesitar extensiones, se llega a lectura arbitraria y a SSRF, que ya son impacto alto. La ejecución es el escalón siguiente y más caro.

## Huella esperada

Ruidosa cuando toca la red, silenciosa en la lectura local —igual que [[MOC - XXE]] y [[MOC - SSRF]], de los que hereda la telemetría—:

- El SSRF por `document('http://...')` hace que el servidor se conecte al destino, que ve [[Conexión saliente del servidor de aplicación]] y cubren [[Barrido de puertos internos desde el servidor de aplicación]] y [[Petición al servicio de metadatos de instancia]] según a dónde apunte.
- Con canal ciego queda [[Consulta DNS saliente]].
- El reconocimiento fallido —expresiones XSLT mal formadas— deja excepciones del procesador en [[Log de errores del servidor web]].
- La **lectura local con `file://` no emite nada**, mismo hueco de fuente que el XXE local: sin conexión, sin proceso, ninguna fuente lo ve.

Es la cara azul de SSRF y XXE reutilizada, sin nada nuevo: la lectura es ciega, el SSRF se detecta por la conexión. Anotado en [[MOC - XSLT injection]].
