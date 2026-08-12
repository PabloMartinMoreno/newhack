---
tipo: tradecraft
clase: "[[CWE-444 - Inconsistent Interpretation of HTTP Requests]]"
eje: primitiva-de-desincronización
implementacion: "Abusar de que el frente reescribe mal las cabeceras de largo al degradar HTTP/2 a HTTP/1.1 hacia el back"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]", "[[Log de errores del servidor web]]"]
requisitos: [front-http2-que-degrada-a-http1-en-el-back]
coste: medio
alternativas: ["[[Request smuggling - CL.TE y TE.CL]]", "[[Request smuggling - desincronización del cliente]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - H2.CL
  - H2.TE
  - HTTP/2 downgrade
tags:
  - dominio/web
---

# Request smuggling - degradación de HTTP2

## Cuándo lo elijo

Cuando el frente habla HTTP/2 con el cliente pero **degrada a HTTP/1.1** para hablar con el back — que es la configuración por defecto de casi todos los CDN y balanceadores modernos. Se reconoce porque la conexión del cliente es HTTP/2 (lo dice el propio protocolo) y el sitio está detrás de un CDN.

Es la rama de mayor rendimiento hoy, porque el HTTP/1.1 clásico está cada vez más mitigado pero la degradación reintroduce el problema en cadenas que se creen seguras por usar HTTP/2. Se prueba cuando la conexión es H2; si es H1 puro, la rama es [[Request smuggling - CL.TE y TE.CL]].

## Por qué funciona

HTTP/2 no tiene el problema de `Content-Length` contra `Transfer-Encoding`: lleva el largo del cuerpo en la estructura del protocolo, de forma no ambigua. El agujero aparece cuando el frente **reconstruye** una petición HTTP/1.1 para el back y tiene que generar las cabeceras de largo a partir de esa estructura.

Si al degradar el frente **confía en las cabeceras que el atacante puso dentro del mensaje HTTP/2** en vez de recalcular el largo real, esas cabeceras pasan al back:

- **H2.CL**: el atacante declara un `Content-Length` dentro del mensaje H2. HTTP/2 lo ignora —usa su propio largo—, pero el frente lo copia tal cual al HTTP/1.1 que arma. El back lo obedece y se desincroniza.
- **H2.TE**: igual con `Transfer-Encoding: chunked`. HTTP/2 lo ignora; el frente lo arrastra al back, que empieza a leer chunked.

La ventaja sobre el HTTP/1.1 clásico es doble. Primero, **el frente cree que está a salvo** porque HTTP/2 es no ambiguo, así que a menudo no normaliza. Segundo, hay una superficie extra que el HTTP/1.1 no tiene: **inyección de cabeceras y de la línea de petición** por caracteres que HTTP/2 permite en los nombres o valores de cabecera —saltos de línea, dos puntos— y que al degradarse se convierten en estructura HTTP/1.1. Con eso se parte una cabecera en dos, o se inyecta una petición entera.

Las construcciones y los caracteres que sobreviven a la degradación están en [[Request smuggling - matriz de sondeo]].

## Cómo falla

Falla cuando el frente valida el mensaje HTTP/2 antes de degradar: rechaza cabeceras con caracteres prohibidos, y **recalcula** el largo en vez de copiar el que vino. Es lo que hacen las implementaciones corregidas después de que esta clase se documentara alrededor de 2021.

Falla, obviamente, cuando la cadena usa HTTP/2 de extremo a extremo y no degrada — que es la mitigación de fondo.

Y falla cuando el CDN normaliza agresivamente, cosa que varios empezaron a hacer por defecto tras la ola de hallazgos.

## Coste

Medio. Detectar si el frente degrada y confía en las cabeceras internas son pocas peticiones, pero requiere una herramienta que hable HTTP/2 **crudo** y permita meter cabeceras malformadas — los clientes normales las corrigen o las rechazan antes de enviarlas. Sin esa herramienta la rama no se puede ni probar.

La inyección de cabeceras por degradación es más barata de explotar que el desync de largo una vez que se confirma, porque no depende de calcular largos al byte: se inyecta estructura directamente.

## Huella esperada

Ruidosa y con firma, como la rama clásica, pero la firma vive en un lugar distinto.

- [[Registro del WAF]] es de nuevo la fuente primaria, si el WAF inspecciona HTTP/2. Muchos WAF viejos solo miran HTTP/1.1 y son ciegos justo para esta rama — que es parte de por qué rinde.
- La petición degradada que llega al back **sí** tiene la anomalía HTTP/1.1 clásica —doble cabecera de largo, o una petición inyectada—, así que [[Log de acceso del servidor web]] del back la ve como una petición extra o malformada, aunque el frente no registró nada raro. El desajuste de conteo entre las dos capas vuelve a ser la señal de correlación, y el mismo hueco que en [[Request smuggling - CL.TE y TE.CL]].
- Los caracteres inyectados por degradación —saltos de línea en cabeceras— dejan errores de parseo en [[Log de errores del servidor web]] del back cuando no calzan.

El punto defensivo que este caso deja claro, y que va en el informe: **un WAF que solo entiende HTTP/1.1 no protege una cadena que habla HTTP/2 al cliente**. Es un punto ciego de fuente, no de regla.
