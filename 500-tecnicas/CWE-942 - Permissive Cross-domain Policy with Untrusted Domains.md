---
tipo: tecnica
taxonomia: cwe
identificador: CWE-942
wstg: WSTG-CLNT-07
tacticas: []
aliases:
  - CWE-942
  - CORS misconfiguration
  - CORS mal configurado
  - política de dominio cruzado permisiva
tags:
  - dominio/web
---

# CWE-942 - Permissive Cross-domain Policy with Untrusted Domains

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - CORS]]; las variantes en `600-tradecraft/`; los payloads en [[CORS bypass de origen - matriz de referencia]].

## Qué es

El navegador prohíbe que una página lea la respuesta de una petición a otro origen. CORS es el mecanismo que **relaja** esa prohibición: el servidor declara, con la cabecera `Access-Control-Allow-Origin`, desde qué orígenes se puede leer su respuesta.

El fallo aparece cuando esa declaración es demasiado amplia o se calcula mal: el servidor termina autorizando a un origen del atacante a leer respuestas que llevan datos del usuario.

## Qué protege y qué no — la confusión que ordena el dominio

CORS se lee mal todo el tiempo porque se lo cruza con CSRF, y son opuestos:

| | CSRF | CORS mal configurado |
|---|---|---|
| Qué abusa | Que el navegador **manda** la petición con cookies | Que el atacante **lee** la respuesta |
| CORS lo previene | No, es irrelevante | Es el fallo mismo |
| Sirve para | Escribir a ciegas | **Leer** datos de la víctima |

CSRF escribe sin ver; CORS mal configurado lee. Confundirlos lleva al error clásico: "hay CORS abierto, entonces hay CSRF", que es falso — un `Access-Control-Allow-Origin` permisivo no habilita ningún CSRF, y a veces lo estorba.

## Por qué la validación falla tanto

Autorizar orígenes exige comparar el `Origin` que llega contra una lista, y esa comparación se hace mal de las mismas maneras que en [[CWE-601 - URL Redirection to Untrusted Site]]:

- **Se refleja el `Origin` sin validar.** El servidor copia la cabecera recibida a `Access-Control-Allow-Origin`, con lo cual **todo** origen queda autorizado, uno por uno.
- **Se compara por subcadena.** `Origin` que contenga el dominio, o que empiece o termine con él, pasa.
- **Se confía en `null`.** Un valor especial que varios contextos producen y que el atacante puede forzar.

El agravante que convierte cualquiera de esas en crítica es `Access-Control-Allow-Credentials: true`: le dice al navegador que mande las cookies **y** deje leer la respuesta. Sin esa cabecera, un origen reflejado solo lee lo que ya es público.

## Por qué la mitigación no es un comodín inteligente

`Access-Control-Allow-Origin: *` es seguro para datos públicos y el navegador **prohíbe** combinarlo con credenciales, así que no es el problema. El problema es el reflejo dinámico que imita un comodín pero con credenciales encendidas.

La mitigación es una **lista blanca de orígenes exactos**, comparados completos —esquema, host y puerto—, sin comodines de subdominio y sin partes calculadas. Y no reflejar `null` nunca.

## Referencias canónicas

- [CWE-942](https://cwe.mitre.org/data/definitions/942.html)
- [CWE-346](https://cwe.mitre.org/data/definitions/346.html) — Origin Validation Error, la clase vecina
- WSTG-CLNT-07
- Fetch Standard § CORS protocol
