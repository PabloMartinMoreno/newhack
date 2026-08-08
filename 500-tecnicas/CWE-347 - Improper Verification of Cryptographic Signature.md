---
tipo: tecnica
taxonomia: cwe
identificador: CWE-347
wstg: WSTG-SESS-10
tacticas: []
aliases:
  - CWE-347
  - JWT
  - Firma no verificada
tags:
  - dominio/web
---

# CWE-347 - Improper Verification of Cryptographic Signature

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Gestión de sesión]]; la variante, en [[Sesión - falsificación de JWT]]; los ataques concretos, en [[JWT - matriz de referencia]].

## Qué es

La aplicación acepta datos firmados sin comprobar la firma correctamente. En web esto es, casi siempre, JWT.

## Por qué JWT concentra el problema

Porque **el token declara cómo debe verificarse a sí mismo**. Ese es el defecto de diseño del que se derivan casi todos los ataques del formato: la cabecera lleva el algoritmo, y a veces la clave o la URL de la clave, y una implementación ingenua obedece esas instrucciones.

Es equivalente a un cerrojo que acepta que la llave le indique qué tipo de cerrojo es.

De ahí salen las tres familias:

- **Algoritmo `none`.** El token dice que no está firmado. Una biblioteca que respete la cabecera lo acepta sin verificar nada.
- **Confusión de algoritmo.** El token dice `HS256` donde el servidor esperaba `RS256`. Si la implementación elige el algoritmo según el token y usa "la clave" sin distinguir tipo, verifica un HMAC usando como secreto la **clave pública** — que es pública.
- **Clave controlada por el atacante.** Las cabeceras que apuntan a la clave (`jwk`, `jku`, `x5u`, `kid`) permiten que el token diga con qué clave verificarse. Si el servidor la busca donde el token indica, el atacante firma con la suya.

## El problema que no es de firma

Un JWT con firma perfectamente verificada sigue siendo inseguro si no se validan las **afirmaciones**: vencimiento, emisor, destinatario. Un token válido de otro entorno, o de otra aplicación del mismo proveedor de identidad, es un token válido.

Y hay una confusión que conviene desarmar en cualquier informe: **el contenido de un JWT no está cifrado**. Es base64, legible por cualquiera. Firmar garantiza integridad, no confidencialidad. Meter datos sensibles en las afirmaciones es un hallazgo propio, independiente de la firma.

## La mitigación real

**Fijar el algoritmo en el servidor** y rechazar cualquier token que declare otro. Nunca derivar el algoritmo ni la clave de la cabecera del token. Lista blanca de identificadores de clave, resueltos contra un conjunto local; jamás contra una URL que venga en el token.

Y validar siempre vencimiento, emisor y destinatario, que es donde falla la mitad de las implementaciones que sí verifican bien la firma.

## Referencias canónicas

- [CWE-347](https://cwe.mitre.org/data/definitions/347.html)
- [CWE-345](https://cwe.mitre.org/data/definitions/345.html) — verificación insuficiente de autenticidad de datos
- WSTG-SESS-10
