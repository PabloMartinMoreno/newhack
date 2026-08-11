---
tipo: tradecraft
clase: "[[CWE-352 - Cross-Site Request Forgery]]"
eje: defensa
implementacion: "Fijar la cookie del token desde un subdominio y mandar el mismo valor en el parámetro"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [token-en-cookie-propia, primitiva-de-escritura-de-cookie]
coste: medio
alternativas: ["[[CSRF - token ausente o no ligado]]", "[[CSRF - bypass de SameSite]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - double submit cookie
  - cookie tossing
tags:
  - dominio/web
---

# CSRF - double submit y cookie inyectada

## Cuándo lo elijo

Cuando el token existe, se valida, y la comprobación es **que el parámetro coincida con una cookie** en vez de con algo guardado del lado del servidor. Se reconoce mirando el tráfico: hay una cookie cuyo valor es idéntico al campo oculto del formulario.

Es el patrón que eligen las aplicaciones sin estado, porque evita guardar tokens. La contrapartida es que traslada toda la seguridad a una premisa: que el atacante no pueda escribir cookies en el dominio de la víctima. Esa premisa es más débil de lo que parece.

Si el token está ligado a la sesión del lado del servidor, esta rama no aplica y el dominio se termina acá salvo que la defensa real sea la cookie — ahí va [[CSRF - bypass de SameSite]].

## Por qué funciona

La validación compara dos valores que **controla el mismo actor**. Si se pueden fijar los dos, la comprobación se satisface sola: se manda `csrf=X` en el cuerpo y `csrf=X` en la cookie, y coinciden.

Todo depende entonces de conseguir escribir una cookie en el dominio, y hay cuatro caminos, en orden de frecuencia:

- **Desde cualquier subdominio.** Una cookie fijada en `blog.objetivo.com` sin atributo de dominio viaja igual a `www.objetivo.com`: para las cookies, el ámbito es el dominio registrable, no el origen. Un subdominio olvidado, un servicio de terceros o un XSS en cualquier punto del dominio alcanzan.
- **Por inyección de encabezado de respuesta**, si algún endpoint refleja entrada en `Set-Cookie`.
- **Desde HTTP sin cifrar**, si el atacante está en la red y la cookie no es `__Host-`.
- **Por desbordamiento del frasco de cookies**: se escriben cientos de cookies hasta que el navegador expulsa las viejas, y la aplicación reemite la suya en un estado controlado.

La confusión que hace posible todo esto es que **las cookies no respetan el mismo origen**. El resto de la política del navegador razona en orígenes; las cookies razonan en dominios, y esa asimetría es el fallo estructural que se abusa acá.

## Cómo falla

Falla contra el prefijo `__Host-` en el nombre de la cookie: obliga a `Secure`, a `Path=/` y a **no** tener atributo `Domain`, con lo cual ningún subdominio puede fijarla ni sobrescribirla. Es la mitigación correcta y la que hay que recomendar en el informe, porque arregla la causa en vez de agregar otra comprobación.

Falla también cuando el valor de la cookie está firmado o cifrado con una clave del servidor: se puede fijar la cookie pero no producir un valor que verifique.

Y falla, más prosaicamente, cuando no hay ningún subdominio bajo control ni primitiva de escritura de cookies. Es la parte cara de esta rama: el ataque es trivial una vez que se puede escribir la cookie, y conseguir eso puede ser todo el trabajo.

## Coste

Medio, y muy bimodal. Con una primitiva de escritura de cookies ya disponible, son dos peticiones. Sin ella, hay que salir a buscarla —enumerar subdominios, encontrar un XSS en cualquiera de ellos, revisar reflejos en `Set-Cookie`— y eso es un trabajo de reconocimiento entero que puede no dar nada.

Conviene decidir temprano si vale la pena: si la acción objetivo no es de alto impacto, no se justifica el rodeo.

## Huella esperada

La petición del ataque no se distingue de una legítima: el token coincide, porque el atacante puso los dos lados.

Lo que sí queda es el paso previo, y es donde está la detección real:

- Si la cookie se fijó desde un subdominio comprometido, hay una petición a **ese** subdominio en [[Log de acceso del servidor web]] inmediatamente antes de la acción. La correlación entre orígenes distintos del mismo dominio es la señal.
- El desbordamiento del frasco de cookies genera una ráfaga de peticiones con cabeceras `Cookie` anormalmente grandes, que a veces terminan en `431` o `400` en el registro.
- La acción en sí queda en [[Log de auditoría de la aplicación]] con el mismo perfil que cualquier CSRF: sin la navegación previa que debería precederla.
