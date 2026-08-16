---
tipo: tradecraft
clase: "[[CWE-113 - Improper Neutralization of CRLF Sequences in HTTP Headers]]"
eje: alcance
implementacion: "Inyectar un doble \\r\\n para cerrar las cabeceras y escribir un cuerpo de respuesta completo, controlado"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Registro del WAF]]", "[[Informe de violación de CSP]]"]
requisitos: [entrada-reflejada-en-cabecera, sin-filtro-de-doble-crlf]
coste: medio
alternativas: ["[[CRLF - inyección de cabecera]]", "[[XSS - reflejado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - response splitting
  - división de respuesta
tags:
  - dominio/web
---

# CRLF - división de respuesta

## Cuándo lo elijo

Cuando la inyección de CRLF confirmada permite meter no una cabecera sino un **doble `\r\n`** —que cierra las cabeceras y empieza el cuerpo—. Es el escalón de mayor impacto del dominio: en vez de agregar una cabecera, se escribe una **respuesta entera controlada**, con su cuerpo.

Se elige después de [[CRLF - inyección de cabecera]] cuando el filtro deja pasar el doble salto de línea y el objetivo es XSS o envenenamiento de caché, no solo fijar una cookie.

## Por qué funciona

Un `\r\n\r\n` separa las cabeceras del cuerpo en HTTP. Inyectarlo cierra las cabeceras de la respuesta legítima y deja que lo que sigue sea el **cuerpo**, escrito por el atacante:

```
/redir?url=x%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>
```

El resultado es una respuesta con un cuerpo HTML controlado, que el navegador de la víctima renderiza:

- **XSS reflejado** sin necesitar un sink de HTML en la página: el cuerpo entero es del atacante. Es [[XSS - reflejado]] por otro camino, y evade filtros que buscan el payload en el contenido de la página porque el payload **es** la página.
- **Envenenamiento de caché** si hay una caché delante: la respuesta partida se guarda y se sirve a todos —el smuggling y el CRLF convergen acá, los dos entregan una respuesta envenenada a [[MOC - Web cache]]—.
- **Falsificación de contenido**: mostrar una página de phishing en el dominio legítimo.

La técnica fina es controlar dónde termina la respuesta legítima —con un `Content-Length: 0` inyectado— para que el cuerpo propio no quede pegado a basura. Las construcciones están en [[CRLF impacto - matriz de referencia]].

## Cómo falla

Falla contra el mismo filtro que la rama de cabecera —rechazar `\r\n`—, y además contra filtros que permiten un `\r\n` pero bloquean el **doble**, que algunos aplican específicamente contra la división.

Falla cuando el servidor reserva el `Content-Length` de la respuesta original y no deja que el cuerpo inyectado lo reemplace, dejando la respuesta malformada en vez de partida.

Y falla sobre HTTP/2 de extremo a extremo, como toda la clase.

## Coste

Medio. Confirmar la división es más delicado que la inyección de una cabecera: hay que cerrar bien la respuesta legítima y armar el cuerpo para que el navegador lo tome. Son varios intentos ajustando `Content-Length` y el orden de las cabeceras.

Con caché delante sube el valor —una respuesta envenenada persiste— pero también el cuidado, porque envenenar la caché afecta a usuarios reales, con la misma advertencia de [[MOC - Web cache]].

## Huella esperada

La rama más ruidosa del dominio, con la firma más gruesa:

- La entrada lleva **`%0d%0a` repetido** —el doble salto de línea— más fragmentos de una respuesta HTTP (`HTTP/1.1`, `Content-Type`) dentro de un parámetro. Es una firma inconfundible sobre la petición, que ven [[Registro del WAF]] y [[Log de acceso del servidor web]] si viaja en la URL.
- El XSS resultante dispara [[Informe de violación de CSP]] en el navegador de la víctima si hay política, la misma detección de efecto que cubre el XSS venga de donde venga.
- Si envenena la caché, hereda la telemetría de [[MOC - Web cache]] —y el mismo hueco: el momento del envenenamiento solo lo ve el WAF, el efecto se ve aguas abajo.

Es de las técnicas más detectables por firma del vault, porque el payload lleva estructura de respuesta HTTP en la entrada, que no tiene forma legítima. Refuerza, con la rama de cabecera, el candidato transversal de detección de metacaracteres de estructura. Anotado en [[MOC - CRLF injection]].
