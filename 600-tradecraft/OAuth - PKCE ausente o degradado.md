---
tipo: tradecraft
clase: "[[CWE-287 - Improper Authentication]]"
eje: fase-del-flujo
implementacion: "Canjear un código interceptado porque no hay verificador, o forzar el método plano para deducirlo"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [cliente-publico, codigo-interceptable]
coste: alto
alternativas: ["[[OAuth - redirect_uri mal validado]]", "[[OAuth - flujo implícito y token no verificable]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - PKCE
  - code interception
tags:
  - dominio/web
---

# OAuth - PKCE ausente o degradado

## Cuándo lo elijo

Cuando el cliente es público —una aplicación móvil, de escritorio o de página única, que no puede guardar un secreto— y ya hay una forma de ver el código de autorización: una redirección abierta encadenada, un esquema de aplicación que otra aplicación puede reclamar, un registro del navegador, o el `Referer` de la página de retorno.

Es la rama que **depende de otra vulnerabilidad**, y por eso va última en el orden de trabajo. Sin una primitiva para ver el código, no hay nada que canjear y la rama no aplica.

Contra un cliente confidencial —con secreto del lado del servidor— tampoco aplica: el secreto ya cumple la función que cumpliría PKCE.

## Por qué funciona

PKCE existe para que un código robado no sirva. El cliente genera un secreto al azar, manda su resumen al pedir autorización, y presenta el original al canjear; quien intercepte el código no tiene el original y el canje falla.

Dos formas de que eso no proteja:

- **No está.** El servidor de autorización no lo exige y el cliente no lo manda. El código canjea solo, y cualquiera que lo vea entra a la cuenta. Sigue siendo el caso mayoritario en integraciones viejas.
- **Está degradado.** El parámetro admite `plain` como método, donde el verificador y su resumen son el mismo valor. Si el atacante ve el código, ve también el desafío, y el desafío **es** el verificador. Peor: algunos servidores aceptan un canje sin `code_verifier` aunque la autorización lo haya pedido, o no comparan que el método usado sea el que se declaró.

La degradación se prueba cambiando `code_challenge_method=S256` por `plain`, o quitando `code_verifier` del canje. Es una petición cada una.

Conviene ser claro sobre qué protege PKCE, porque se confunde seguido con [[OAuth - redirect_uri mal validado]]: **PKCE protege el código en tránsito, no la dirección a la que se manda**. Un desvío de la redirección hacia un cliente que el atacante controla puede seguir funcionando con PKCE puesto, porque en ese caso el atacante genera el par completo.

## Cómo falla

Falla contra un servidor de autorización que exige PKCE con `S256`, rechaza `plain` y comprueba que el método del canje coincida con el de la autorización. Es lo que pide RFC 9700 y lo que ya hacen los proveedores grandes.

Falla, sobre todo, cuando no hay forma de ver el código. Ese es el filtro real: sin la primitiva previa esta rama es teórica, y perseguirla sin ella es el error de orden del dominio.

Y falla cuando el código está atado al cliente y a la dirección, que es una defensa independiente y bastante común.

## Coste

Alto, y engañoso: las pruebas de degradación cuestan tres peticiones, pero conseguir ver el código puede costar todo un trabajo de reconocimiento. El coste está casi entero en el prerrequisito.

Recomendación de orden: probar la degradación temprano —es barato y documenta un hallazgo de configuración aunque no se explote— y volver a esta rama solo si aparece la primitiva.

## Huella esperada

Poca, porque el ataque es un canje de código que del lado del servidor se ve legítimo. De ahí el `opsec: limpio`.

Las dos señales aprovechables están en [[Log de autenticación de la aplicación]] del proveedor:

- **Peticiones de autorización con `code_challenge_method=plain`** cuando el cliente normalmente usa `S256`. Es un desajuste con el comportamiento propio del cliente, no una firma — o sea que necesita línea base, ver [[Sin línea base no hay anomalía]].
- **Un canje desde una dirección de red distinta de la que pidió la autorización.** Es el indicio más directo de código interceptado, y solo lo ve el proveedor.

Del lado del cliente auditado prácticamente no hay nada: en [[Log de acceso del servidor web]] queda una petición de retorno normal. Es un dominio donde la telemetría útil está en el otro extremo del flujo, que casi nunca es el sistema que se está monitoreando — y esa asimetría vale anotarla en el informe.
