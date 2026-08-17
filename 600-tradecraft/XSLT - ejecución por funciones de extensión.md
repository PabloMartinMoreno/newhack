---
tipo: tradecraft
clase: "[[CWE-94 - Improper Control of Generation of Code]]"
eje: capacidad-del-procesador
implementacion: "Llamar una función del lenguaje anfitrión desde la hoja de estilo cuando el procesador tiene las extensiones habilitadas"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Log de errores del servidor web]]", "[[Conexión saliente del servidor de aplicación]]"]
requisitos: [inyección-xslt, funciones-de-extensión-habilitadas]
coste: medio
alternativas: ["[[XSLT - lectura y SSRF]]", "[[SSTI - ejecución directa]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - XSLT RCE
  - extension functions
  - php:function
tags:
  - dominio/web
---

# XSLT - ejecución por funciones de extensión

## Cuándo lo elijo

Cuando la inyección de XSLT está confirmada y el procesador tiene habilitadas las **funciones de extensión** —el puente al lenguaje anfitrión—. Se reconoce probando una llamada de extensión del procesador identificado: si ejecuta, hay RCE. Es la capacidad más grave del dominio y la que lo vuelve peligroso.

Se llega acá desde [[XSLT - lectura y SSRF]] cuando aquella confirmó el procesador y el objetivo es ejecución, no solo lectura. Si las extensiones están deshabilitadas —lo más común en procesadores endurecidos—, esta rama no aplica y la lectura es el techo.

## Por qué funciona

Varios procesadores de XSLT permiten llamar funciones del lenguaje anfitrión desde la hoja de estilo, una característica pensada para que el desarrollador extienda las transformaciones. Si el atacante controla la hoja, llama lo que quiera:

**PHP (libxslt con `registerPHPFunctions`):**
```xml
<xsl:value-of select="php:function('system','id')"/>
<xsl:value-of select="php:function('file_get_contents','/etc/passwd')"/>
```

**Java (Xalan):**
```xml
<xsl:value-of select="java:java.lang.Runtime.exec(java:java.lang.Runtime.getRuntime(),'id')"/>
```

**.NET:**
```xml
<msxsl:script implements-prefix="user" language="C#">
  public string run(){ return System.Diagnostics.Process.Start("cmd","/c whoami").ToString(); }
</msxsl:script>
```

Cada procesador tiene su sintaxis, en [[XSLT payloads - matriz de referencia]]. El común es que la función del lenguaje anfitrión ejecuta con los privilegios del proceso, así que `system()`/`Runtime.exec()` es RCE directo.

Es primo de [[SSTI - ejecución directa]]: los dos abusan que un motor de plantilla/transformación exponga el lenguaje anfitrión. La diferencia es que en XSLT la ejecución depende de una configuración específica —`registerPHPFunctions`, las extensiones de Xalan— que está apagada más seguido que en las plantillas.

## Cómo falla

Falla cuando las **funciones de extensión están deshabilitadas**, que es la mitigación correcta y el valor por defecto en configuraciones endurecidas. Es lo que separa un XSLT de lectura de uno de ejecución, y hay que probarlo para saber cuál es.

Falla cuando el procesador no soporta extensiones —algunos son deliberadamente sin ellas— o cuando corre en un entorno restringido sin acceso al sistema.

Y falla si la identificación del procesador fue optimista: un payload de PHP contra un Xalan no hace nada más que ensuciar el registro de errores. Identificar bien con [[XSLT - matriz de identificación]] es lo que decide el payload.

## Coste

Medio. Confirmado el procesador y que las extensiones están activas, la ejecución es una expresión. El costo está en el paso previo: probar si las extensiones están habilitadas, que es una llamada por procesador candidato.

Conviene identificar el procesador primero y probar solo su sintaxis de extensión, en vez de tirar todas —cada fallo deja una excepción con el nombre del procesador en el registro de errores, que es la señal más clara para el defensor—.

## Huella esperada

La rama más visible del dominio, por la misma razón que casi todas las de ejecución: **nace un proceso hijo del servidor web**, la relación en la que ancla [[Intérprete de comandos como hijo del servidor web]]. Esa detección lo ve sin saber que hubo XSLT de por medio, igual que ve command injection, SSTI y deserialización.

- El proceso hijo lo cubre [[Intérprete de comandos como hijo del servidor web]].
- Si el payload descarga una segunda etapa, la conexión saliente la ven las reglas de SSRF sobre [[Conexión saliente del servidor de aplicación]].
- El reconocimiento fallido —llamadas de extensión de procesadores equivocados— llena [[Log de errores del servidor web]] de excepciones de XSLT, cada una con el nombre del procesador. La ráfaga es reconocimiento en curso y precede al intento que funciona, la misma asimetría que en SSTI y deserialización: lo fallido es más visible que lo exitoso.

Es la cara azul de command injection reutilizada, sin regla nueva. Con las de [[XSLT - lectura y SSRF]] —que reusan SSRF y XXE— el dominio entero se cierra con detecciones existentes. Anotado en [[MOC - XSLT injection]].
