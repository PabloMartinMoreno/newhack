---
tipo: tradecraft
clase: "[[CWE-601 - URL Redirection to Untrusted Site]]"
eje: fase-del-flujo
implementacion: "Desviar la redirección de vuelta para que el código de autorización llegue al servidor del atacante"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de autenticación de la aplicación]]"]
requisitos: [cliente-con-validacion-laxa, interaccion-de-la-victima]
coste: medio
alternativas: ["[[OAuth - falta de state]]", "[[OAuth - PKCE ausente o degradado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - robo de código de autorización
  - redirect_uri bypass
tags:
  - dominio/web
---

# OAuth - redirect_uri mal validado

## Cuándo lo elijo

Cuando el objetivo tiene inicio de sesión con un proveedor externo y la primera prueba —cambiar `redirect_uri` por un dominio propio— devuelve algo distinto de un error rotundo. Si el servidor de autorización responde con un error de dirección no registrada, esta rama se cierra rápido y se pasa a [[OAuth - falta de state]].

Es la rama de mayor impacto del dominio: termina en la cuenta de la víctima sin necesitar su contraseña ni su segundo factor. Por eso va primero aunque cueste más que las otras.

## Por qué funciona

El servidor de autorización manda el código a la dirección que el cliente le pidió. La única cosa que impide que esa dirección sea del atacante es una comparación de cadenas, y esa comparación se rompe de tres maneras que están todas en [[OAuth redirect_uri - matriz de referencia]]:

- **La validación es laxa.** Prefijo sin anclar, comodín de subdominio, coincidencia por subcadena, o solo se compara el dominio y no la ruta.
- **La dirección registrada es válida y redirige.** Acá no hay fallo en la validación de OAuth: hay un [[CWE-601 - URL Redirection to Untrusted Site]] en el propio cliente. El código llega a donde corresponde y el cliente lo reenvía. Es el caso más frecuente en aplicaciones grandes, porque cualquier redirección abierta en cualquier rincón del dominio sirve.
- **Hay un XSS o un `iframe` permitido en el dominio registrado.** El código llega a la página legítima y se lee desde ahí.

La segunda vía es la que conviene tener presente: **la vulnerabilidad no está en la implementación de OAuth sino en otra parte del sitio**, y por eso la busca poca gente. Un redirector de márketing olvidado alcanza.

Cuando la dirección de redirección no se puede desviar pero sí se puede quedar el código en el fragmento, la variante es la del flujo implícito — ver [[OAuth - flujo implícito y token no verificable]].

## Cómo falla

Falla contra una lista blanca de direcciones completas comparadas exactas, que es lo que la especificación pide desde el principio. Es la mitigación que va en el informe y cierra la rama entera.

Falla contra PKCE bien implementado **para robos de código en tránsito**, pero no acá: si el atacante desvía la redirección, obtiene el código y no el verificador, así que no puede canjearlo. Es una distinción que se confunde seguido — PKCE protege la interceptación, no la desviación hacia un cliente que el atacante no controla. Cuando el atacante **sí** controla un cliente registrado, el desvío vuelve a rendir.

Y falla en la práctica cuando el código está atado al cliente y a la dirección: canjearlo desde otro contexto devuelve error aunque se lo haya conseguido.

Lo que nunca falla es el requisito de interacción: la víctima tiene que abrir el enlace. Sin eso no hay ataque, y eso pone un techo a la severidad que conviene reflejar honestamente en el informe.

## Coste

Medio. Probar las variantes de la matriz son diez o quince peticiones y se descartan por el código de respuesta.

Lo caro es la segunda vía: encontrar una redirección abierta dentro del dominio registrado es un trabajo de reconocimiento propio que puede llevar más que todo el resto del dominio. Conviene buscarla solo después de confirmar que la validación estricta está puesta, porque si la validación es laxa no hace falta.

## Huella esperada

Del lado del servidor de autorización queda lo más visible: **peticiones de autorización con direcciones de redirección que no están registradas**, cada una devolviendo error. Durante la prueba son quince seguidas desde el mismo origen. Es la señal más limpia del dominio y vive en [[Log de autenticación de la aplicación]] del proveedor, que rara vez es el sistema auditado.

Del lado del cliente queda menos: el canje del código llega desde una dirección distinta de la habitual, lo que se ve en [[Log de acceso del servidor web]] si se registra el origen.

Y el ataque exitoso deja algo que sí discrimina: **un inicio de sesión de la víctima desde una dirección de red que nunca usó, en el mismo minuto en que abrió un enlace externo**. Es correlación, no firma, y la cubre [[Misma sesión desde dos orígenes]] sin saber que hubo OAuth de por medio.
