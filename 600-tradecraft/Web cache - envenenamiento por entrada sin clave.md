---
tipo: tradecraft
clase: "[[CWE-349 - Acceptance of Extraneous Untrusted Data With Trusted Data]]"
eje: dirección
implementacion: "Encontrar una cabecera o parámetro fuera de la clave de caché que se refleje, y guardar una respuesta con payload"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Registro del WAF]]"]
requisitos: [caché-delante, entrada-sin-clave-que-influye-en-la-respuesta]
coste: medio
alternativas: ["[[Web cache - manipulación de la clave]]", "[[Web cache - engaño de caché]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - unkeyed header poisoning
  - X-Forwarded-Host poisoning
tags:
  - dominio/web
---

# Web cache - envenenamiento por entrada sin clave

## Cuándo lo elijo

Es el caso base del envenenamiento y el primero a probar cuando hay una caché delante. Se busca una entrada —casi siempre una cabecera— que **no** forma parte de la clave de caché pero **sí** cambia la respuesta, se le mete un payload, y se confirma que la respuesta envenenada quedó guardada.

Si la entrada que influye sí está en la clave, envenenarla solo se afecta a uno mismo, y hay que ir a [[Web cache - manipulación de la clave]] para sacarla de la clave o encontrar una discrepancia. Si el objetivo es robar datos de la víctima en vez de empujar contenido, el dominio es el opuesto: [[Web cache - engaño de caché]].

## Por qué funciona

La clave de caché es method + host + path, casi siempre sin las cabeceras. Muchos frameworks, en cambio, **usan** ciertas cabeceras para construir la respuesta: `X-Forwarded-Host` para armar URLs absolutas, `X-Forwarded-Scheme` para decidir redirecciones, cabeceras de idioma para el contenido. Esas cabeceras influyen en la respuesta y no están en la clave: son el hueco.

El trabajo es de dos pasos, y el orden importa por seguridad:

1. **Encontrar la entrada sin clave que se refleja**, con un `cache buster` —un parámetro único— para no envenenar a nadie mientras se prueba. Se manda `X-Forwarded-Host: canario.com` con `?cb=1234` y se mira si `canario.com` vuelve en la respuesta.
2. **Confirmar que se cachea**: quitar el cache buster, mandar el payload, y volver a pedir sin las cabeceras para ver si la respuesta envenenada se sirve igual.

El catálogo de cabeceras sin clave está en [[Web cache entradas sin clave - matriz de referencia]]. El payload depende de qué se pueda reflejar —un `X-Forwarded-Host` que arma una etiqueta `<script src>` da importación de JavaScript; uno que arma una redirección da redirección abierta masiva—, y por eso la severidad se decide cruzando la entrada con lo que refleja.

> [!danger] Envenenar afecta a todos los usuarios de esa entrada
> Una vez que la respuesta envenenada se cachea, **todos** los que pidan ese recurso la reciben hasta que la entrada expira o se purga. Durante las pruebas hay que usar siempre el cache buster para no tocar la entrada real, y solo envenenar la entrada de producción con un payload inocuo y de forma acordada. Ver la advertencia de [[Web cache - matriz de sondeo]].

## Cómo falla

Falla cuando la caché incluye en la clave todas las cabeceras que influyen —o cuando no cachea respuestas que dependan de ellas—. Es la mitigación correcta.

Falla cuando la aplicación no refleja ninguna cabecera sin clave: sin reflejo no hay payload que guardar. Es un resultado frecuente y legítimo, y se confirma probando el catálogo entero antes de descartar.

Y falla cuando la entrada que influye **sí** está en la clave: ahí envenenar solo se afecta a uno mismo, y hay que pasar a sacarla de la clave con [[Web cache - manipulación de la clave]].

## Coste

Medio. El sondeo con cache buster es barato y seguro; el trabajo está en probar el catálogo de cabeceras y en calcular cuándo la caché guarda —el momento exacto, la ventana de expiración, qué la purga—. La herramienta Param Miner de Burp automatiza el descubrimiento de entradas sin clave, y sin ella el catálogo se prueba a mano.

Lo caro de verdad es acertar la ventana en producción sin dañar a nadie, que es más restricción operativa que técnica.

## Huella esperada

Firma razonable, porque la petición envenenadora lleva **una cabecera con un valor anómalo sobre una respuesta que se va a cachear**:

- [[Registro del WAF]] ve la cabecera con el payload —un host externo en `X-Forwarded-Host`, un `<script>` reflejado—, que es la fuente primaria porque mira las cabeceras que [[Log de acceso del servidor web]] no registra.
- La señal de correlación más fuerte, y no cubierta, es **una respuesta cacheada cuyo contenido no corresponde a la petición que la generó**: la petición pedía `/` con una cabecera rara, y ahora todos reciben esa versión. Detectarlo exige comparar el contenido servido contra lo esperado, que ninguna fuente del vault modela.
- Si el payload cacheado es un XSS, se dispara además [[Violación de CSP por script inline]] en los navegadores de las víctimas — una detección existente que ve el efecto sin saber que vino de la caché.

Ese último punto es el que salva la cara azul del dominio: el envenenamiento a XSS lo delata la telemetría de XSS, aguas abajo. Lo que no se ve es el momento del envenenamiento en sí, anotado como hueco en [[MOC - Web cache]].
