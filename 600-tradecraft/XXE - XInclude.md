---
tipo: tradecraft
clase: "[[CWE-611 - XML External Entity]]"
eje: mecanismo
implementacion: "Incluir un recurso externo con XInclude, sin declarar DOCTYPE"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Conexión saliente del servidor de aplicación]]"]
requisitos: [xinclude-habilitado, entrada-dentro-de-xml-ajeno]
coste: bajo
alternativas: ["[[XXE - canal directo]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - XInclude
  - XXE sin DOCTYPE
tags:
  - dominio/web
---

# XXE - XInclude

## Cuándo lo elijo

Cuando se controla **parte** de un XML pero no el documento entero. Es la situación que rompe todos los demás canales: la aplicación toma un parámetro del usuario y lo inserta dentro de un XML que arma ella —una petición SOAP a un servicio interno, un documento de configuración, un mensaje a una cola—, así que no hay dónde poner un `DOCTYPE`.

La señal de que este es el caso: el parámetro no parece XML en absoluto. Llega por un formulario normal, o incluso por una petición con `Content-Type` de formulario. El XML aparece después, del lado del servidor, y el atacante nunca lo ve.

Por eso es la variante que **más se pasa por alto**: no hay ningún indicio de que haya XML de por medio hasta que se prueba.

## Por qué funciona

`XInclude` es un mecanismo distinto de las entidades: pertenece a otra especificación y se activa con un atributo de espacio de nombres sobre un elemento cualquiera. No necesita DTD, no necesita `DOCTYPE`, y por lo tanto sobrevive a la restricción de estar embebido dentro de un documento ajeno.

El precio es que hay que pedir la inclusión como texto en lugar de como XML: si se incluye un archivo que no es XML válido sin indicarlo, el parser falla al intentar interpretarlo.

Muchas configuraciones que deshabilitan entidades externas **dejan XInclude activo**, porque son opciones separadas en la mayoría de las bibliotecas. Esa es la razón práctica por la que esta variante sigue funcionando en 2026 donde el XXE clásico ya no.

## Cómo falla

- **El procesador de XInclude no está habilitado** — no viene por defecto en todos los parsers, y requiere que la aplicación lo active explícitamente en varias bibliotecas.
- **El archivo no es texto legible** — un binario incluido como texto rompe el documento.
- **El resultado no se refleja** — misma limitación que el canal directo: sin eco, hay inclusión y no hay lectura. La salida es un recurso remoto en vez de local, que convierte esto en SSRF y se confirma por la conexión entrante.
- **La entrada se escapa antes de insertarse** — si la app codifica correctamente el valor antes de meterlo en el XML, no se puede introducir un elemento nuevo. Es la mitigación correcta y la más frecuente cuando existe.
- **El espacio de nombres se filtra** — algunos WAF buscan la URL de la especificación de XInclude. Se evade codificando; ver [[XXE evasión - matriz de referencia]].

## Coste

Bajo. El payload es corto, cabe en un parámetro de formulario y no requiere infraestructura. Lo caro es **darse cuenta de que hay XML detrás**, que es trabajo de reconocimiento y no de explotación.

## Huella esperada

- [[Log de acceso del servidor web]] con un parámetro que contiene la URL del espacio de nombres de XInclude. A diferencia del XXE clásico, acá el payload **sí queda en el log** cuando viaja por GET o por formulario, porque no necesita un cuerpo XML.
- [[Conexión saliente del servidor de aplicación]] solo si el recurso incluido es remoto. Con `file://` no hay tráfico de red y la variante es invisible salvo por el parámetro.
- Sin proceso hijo, sin consulta DNS, sin error: cuando la inclusión es local y funciona, esta técnica no genera nada más que una línea de log de acceso que hay que estar mirando.

Los payloads están en [[XXE payloads - matriz de referencia]] § XInclude.
