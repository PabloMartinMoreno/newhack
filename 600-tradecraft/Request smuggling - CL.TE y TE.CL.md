---
tipo: tradecraft
clase: "[[CWE-444 - Inconsistent Interpretation of HTTP Requests]]"
eje: primitiva-de-desincronización
implementacion: "Enviar una petición con Content-Length y Transfer-Encoding que el frente y el back interpretan distinto"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Registro del WAF]]", "[[Log de errores del servidor web]]"]
requisitos: [cadena-http1-con-front-y-back-distintos]
coste: medio
alternativas: ["[[Request smuggling - degradación de HTTP2]]", "[[Request smuggling - desincronización del cliente]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - CL.TE
  - TE.CL
  - TE.TE
tags:
  - dominio/web
---

# Request smuggling - CL.TE y TE.CL

## Cuándo lo elijo

Es el caso clásico y el primero a probar cuando la cadena habla HTTP/1.1 entre el frente y el back. Se reconoce con las pruebas de tiempo de [[Request smuggling - matriz de sondeo]]: una petición construida para desincronizar hace que el servidor **espere** bytes que no llegan, y ese retardo es la señal.

Si la conexión del cliente al frente es HTTP/2, la rama es [[Request smuggling - degradación de HTTP2]], que suele rendir más porque el frente confía en su propia reconstrucción. Si no hay un back distinto del frente pero sí hay caché o conexión reutilizada, [[Request smuggling - desincronización del cliente]].

## Por qué funciona

Los tres sabores son la misma idea —front y back miden el cuerpo distinto— con el desacuerdo puesto en un lugar distinto:

- **CL.TE**: el frente usa `Content-Length` y el back usa `Transfer-Encoding`. El frente reenvía lo que el `Content-Length` dice; el back, que sigue el chunked, termina la petición en el trozo de tamaño cero y considera **el resto** como una petición nueva.
- **TE.CL**: al revés. El frente sigue el chunked, el back cuenta bytes. Lo que el frente manda como un trozo más, el back lo corta según su `Content-Length` y deja el resto colgando.
- **TE.TE**: los dos soportan `Transfer-Encoding`, así que hay que **ofuscar** la cabecera para que uno la procese y el otro no —un espacio de más, una tabulación, un guion, una segunda cabecera—. El que la ignora cae a `Content-Length`.

En los tres, el sobrante que un servidor no consumió queda **antepuesto a la siguiente petición** de la conexión. Con eso se envenena la petición de otro usuario, se saltea un control del frente, o se captura la petición de la víctima. El qué se hace está en [[Request smuggling - matriz de explotación]]; las construcciones exactas, en la de sondeo.

La ofuscación de TE.TE es donde vive casi todo el trabajo fino, porque cada servidor tolera variantes distintas y hay que encontrar la que uno acepta y el otro no.

## Cómo falla

Falla cuando el frente **normaliza** las peticiones ambiguas: rechaza las que traen `Content-Length` y `Transfer-Encoding` a la vez, o reescribe el cuerpo antes de reenviarlo. Es la mitigación correcta y la que aplican los proxies modernos bien configurados.

Falla cuando front y back son el mismo software con la misma interpretación, aunque eso es raro en una cadena real con un CDN o un WAF de por medio.

Y falla, en el sentido de que se vuelve delicado, sobre conexiones que no se reutilizan: si cada petición abre una conexión nueva al back, el sobrante no llega a contaminar la de nadie. La reutilización de conexión es una precondición que conviene confirmar.

> [!danger] Esto envenena a usuarios reales
> El sobrante se antepone a la **siguiente** petición que pase por esa conexión del back, y esa petición puede ser de un usuario legítimo. Una prueba mal calibrada le sirve a alguien una respuesta que no pidió, o rompe su sesión. En producción hay que apuntar el sobrante a algo inocuo y acordar la ventana. Ver la advertencia de [[Request smuggling - matriz de sondeo]].

## Coste

Medio. Detectar el sabor con las pruebas de tiempo son pocas peticiones, pero construir el ataque es delicado: el `Content-Length` tiene que ser exacto al byte, el chunked bien formado, y los saltos de línea son `\r\n` literales que las herramientas gráficas a veces alteran. Un byte de más y la petición se rechaza por otra razón, lo que confunde el diagnóstico.

Herramienta ayuda mucho —la extensión HTTP Request Smuggler de Burp automatiza el sondeo y el cálculo de largos—, y sin ella el coste sube bastante. Conviene desactivar cualquier reajuste automático de `Content-Length` del proxy antes de empezar.

## Huella esperada

Es de las pocas técnicas del vault con una **firma de petición fuerte y legítima de detectar**: una petición que trae `Content-Length` **y** `Transfer-Encoding` a la vez viola la especificación y no aparece en tráfico normal. Lo mismo un `Transfer-Encoding` ofuscado con espacios raros o cabeceras duplicadas.

- [[Registro del WAF]] la ve entera, porque mira las cabeceras y el cuerpo. Es la fuente primaria del dominio.
- [[Log de acceso del servidor web]] la ve parcialmente: registra la petición como la interpretó **su** servidor, así que el frente y el back registran cosas distintas de la misma conexión. Ese desajuste —**una conexión donde el frente contó N peticiones y el back contó N+1**— es la señal de correlación más fuerte, y no existe detección en el vault que la explote porque exige unir los registros de dos servidores por identificador de conexión.
- El reconocimiento fallido deja peticiones rechazadas y tiempos de espera anómalos en [[Log de errores del servidor web]].

La firma de cabeceras duplicadas es un caso donde detectar por firma sí paga, por el mismo motivo que en [[MOC - Prototype pollution]]: la anomalía no tiene forma legítima. El desajuste de conteo entre front y back queda anotado como el hueco de correlación del dominio en [[MOC - Request smuggling]].
