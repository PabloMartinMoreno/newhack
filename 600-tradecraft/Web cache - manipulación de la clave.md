---
tipo: tradecraft
clase: "[[CWE-349 - Acceptance of Extraneous Untrusted Data With Trusted Data]]"
eje: dirección
implementacion: "Abusar de cómo se normaliza o recorta la clave de caché para sacar de ella una entrada que influye, o meter el payload donde no se ve"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Registro del WAF]]"]
requisitos: [caché-con-normalización-o-recorte-de-clave-explotable]
coste: alto
alternativas: ["[[Web cache - envenenamiento por entrada sin clave]]", "[[Web cache - engaño de caché]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - cache key manipulation
  - cache parameter cloaking
  - fat GET
tags:
  - dominio/web
---

# Web cache - manipulación de la clave

## Cuándo lo elijo

Cuando la entrada que influye en la respuesta **sí** está en la clave de caché —así que [[Web cache - envenenamiento por entrada sin clave]] solo se afecta a uno mismo— pero la caché y el servidor no construyen la clave igual, y esa discrepancia se puede abusar.

Es la rama fina del dominio. Se llega acá cuando el envenenamiento directo no rindió porque el payload quedaba en la clave, y hay que encontrar una forma de que el payload afecte la respuesta **sin** cambiar la clave que la víctima va a pedir.

## Por qué funciona

La clave de caché no es la URL cruda: la caché la **normaliza** —recorta parámetros, decodifica, ordena, corta en algún delimitador—. El servidor de aplicación normaliza distinto. Cada diferencia entre las dos normalizaciones es una palanca:

- **Recorte de parámetros (cloaking).** Si la caché excluye ciertos parámetros de la clave pero el servidor los usa, se mete el payload en uno de esos: la clave queda limpia —la que pide la víctima— y la respuesta lleva el payload. Variantes con delimitadores raros —`;`, `,`— que una capa trata como separador y la otra no.
- **Fat GET.** El servidor lee el cuerpo de una petición `GET`; la caché no lo incluye en la clave. El payload va en el cuerpo, invisible para la clave.
- **Diferencias de normalización.** La caché decodifica `%2f` y el servidor no, o al revés; la caché ordena la query y el servidor toma el primer valor de un parámetro repetido. Cada una permite que dos peticiones con la misma clave produzcan respuestas distintas.
- **Puerto o esquema sin clave.** Meter el payload en una parte de la URL que el servidor usa y la clave descarta.

El catálogo de discrepancias está en [[Web cache entradas sin clave - matriz de referencia]]. Todas comparten el patrón de [[MOC - Request smuggling]]: **dos parsers de la misma cadena que no coinciden**, acá aplicado a la clave de caché.

## Cómo falla

Falla cuando la caché y el servidor normalizan la clave de forma idéntica, que es lo que garantiza una configuración coherente. Ahí no hay palanca.

Falla cuando la caché incluye la URL completa sin recortar nada en la clave: sin exclusiones no hay cloaking, sin lectura de cuerpo no hay fat GET.

Y falla, prácticamente, cuando ninguna de las discrepancias del catálogo coincide con este par caché/servidor. Es prueba y error, y puede agotarse sin resultado.

## Coste

Alto, el más alto del envenenamiento. Cada discrepancia es una hipótesis sobre cómo difieren dos normalizaciones que no se ven, y hay que probarlas una por una observando si la respuesta cambia sin que cambie la clave. Es delicado y lento, parecido al sondeo de TE.TE en [[Request smuggling - CL.TE y TE.CL]].

Conviene fijar presupuesto: si el envenenamiento directo no rindió y esta rama no da en diez o quince pruebas dirigidas, el dominio probablemente esté mitigado y hay que cambiar.

## Huella esperada

Menos firma que el envenenamiento directo, porque el payload va escondido justo donde la caché no mira —y a veces donde el registro tampoco—:

- El fat GET pone el payload en el **cuerpo de un `GET`**, que [[Log de acceso del servidor web]] no registra: solo lo ve [[Registro del WAF]] si inspecciona cuerpos, y un `GET` con cuerpo es en sí una anomalía que vale detectar.
- El cloaking con delimitadores raros deja URLs con `;` o `,` en posiciones inusuales, visibles en el log de acceso pero fáciles de pasar por alto.
- La señal de correlación es la misma que en la rama directa y el mismo hueco: una respuesta cacheada que no corresponde a la clave que la víctima pide.

El `GET` con cuerpo es la firma más aprovechable de esta rama, por la misma razón que en [[Request smuggling - desincronización del cliente]] el `POST` a un endpoint estático: es una combinación que no ocurre en tráfico legítimo. Depende de instrumentar el cuerpo, que es el hueco de fuente compartido con medio vault.
