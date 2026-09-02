---
tipo: tradecraft
clase: "[[CWE-113 - Improper Neutralization of CRLF Sequences in HTTP Headers]]"
eje: alcance
implementacion: "Inyectar un \\r\\n en un valor reflejado en una cabecera para agregar una cabecera de respuesta propia"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Registro del WAF]]"]
requisitos: [entrada-reflejada-en-una-cabecera-de-respuesta]
coste: bajo
alternativas: ["[[CRLF - división de respuesta]]", "[[CWE-601 - URL Redirection to Untrusted Site]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - header injection
  - Set-Cookie injection
tags:
  - dominio/web
---

# CRLF - inyección de cabecera

## Cuándo lo elijo

Es el caso base del dominio y el primero a probar. Se reconoce cuando la entrada se refleja en una **cabecera de respuesta** —el `Location` de una redirección, un `Set-Cookie` construido con un parámetro, una cabecera de idioma o de rastreo—. Se confirma inyectando `%0d%0a` con una cabecera de prueba y viendo si aparece en la respuesta.

El objetivo es agregar **una** cabecera propia, no partir la respuesta entera —eso es [[CRLF - división de respuesta]], que necesita más control—. Con una cabecera alcanza para varios impactos según cuál sea.

## Por qué funciona

Las cabeceras se separan con `\r\n`. Si el valor reflejado no filtra esa secuencia, inyectarla cierra la cabecera actual y empieza una nueva:

```http
GET /redir?url=/inicio%0d%0aSet-Cookie:%20sesion=fijada HTTP/1.1
```

Respuesta:
```http
HTTP/1.1 302 Found
Location: /inicio
Set-Cookie: sesion=fijada        ← inyectada
```

Lo que se inyecta decide el impacto:

- **`Set-Cookie`** → fija una sesión conocida en el navegador de la víctima → [[CWE-384 - Session Fixation]]. El atacante conoce la cookie, así que después entra a la sesión de la víctima.
- **Cabeceras de CORS** —`Access-Control-Allow-Origin: atacante.com` con credenciales— → habilita el robo de [[CORS - reflejo del origen con credenciales]].
- **Manipular el `Location`** cuando la entrada cae antes del destino → redirección a un dominio propio, [[CWE-601 - URL Redirection to Untrusted Site]].
- **Cabeceras de seguridad al revés** —desactivar `X-Frame-Options`, aflojar la política de contenido— para habilitar otro ataque.

Las codificaciones del `\r\n` que pasan según el filtro, y las variantes de bypass, están en [[CRLF inyección - matriz de referencia]]. La más común es `%0d%0a`, pero según dónde se decodifique la entrada sirven `%0a` solo, la doble codificación, o los caracteres unicode que algunos parsers normalizan a salto de línea.

## Cómo falla

Falla cuando la aplicación **filtra o rechaza** `\r` y `\n` en la entrada que va a la cabecera. Es la mitigación directa y la que traen los frameworks modernos por defecto —por eso la clase decayó, pero sigue viva en construcción de cabeceras a mano.

Falla cuando la cabecera se arma con una API que serializa y escapa los saltos de línea, en vez de concatenar.

Y falla sobre HTTP/2 de extremo a extremo, donde las cabeceras no se delimitan con `\r\n` —aunque la degradación a HTTP/1.1 lo reintroduce, como en [[MOC - Request smuggling]].

## Coste

Bajo, el más bajo del dominio. Confirmar es una petición con `%0d%0a` y una cabecera canario. La cadena de impacto —fijar una cookie, aflojar CORS— son pocas peticiones más.

El reconocimiento es barato: probar el `%0d%0a` en cada parámetro que se refleje en una cabecera, empezando por los de redirección, que son los que más veces caen.

## Huella esperada

Firma clara sobre la petición, la misma familia que las inyecciones:

- La entrada lleva **`%0d%0a` o sus variantes** en un parámetro. Un salto de línea codificado en un valor no aparece en tráfico legítimo, así que es una firma de buena fidelidad, que ve [[Registro del WAF]] y también [[Log de acceso del servidor web]] si el CRLF viaja en la URL —a diferencia de otras inyecciones, esta suele ir en la query de una redirección, que el log sí registra.
- La respuesta con la cabecera inyectada —un `Set-Cookie` de más, un `Location` raro— es la confirmación, visible si se auditan las cabeceras de respuesta.

Es de las inyecciones más detectables por firma, porque el `%0d%0a` es inconfundible y a menudo viaja en la URL, no en el cuerpo. Sumado a las firmas de las cuatro hermanas de inyección y del Host, refuerza el candidato transversal de una regla de firma de metacaracteres de estructura en la entrada. Anotado en [[MOC - CRLF injection]].
