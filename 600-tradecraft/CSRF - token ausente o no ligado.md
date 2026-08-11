---
tipo: tradecraft
clase: "[[CWE-352 - Cross-Site Request Forgery]]"
eje: defensa
implementacion: "Quitar el token, reusarlo entre cuentas, o cambiar el método hasta que deje de validarse"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [sesion-por-cookie, accion-que-cambia-estado]
coste: bajo
alternativas: ["[[CSRF - double submit y cookie inyectada]]", "[[CSRF - bypass de SameSite]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - token CSRF débil
  - CSRF sin token
tags:
  - dominio/web
---

# CSRF - token ausente o no ligado

## Cuándo lo elijo

Siempre primero. Es la rama más barata del dominio y la que más veces resuelve el caso: son cinco peticiones y ninguna necesita entender el resto de la aplicación.

La condición es que haya una acción que cambie estado y que la sesión viaje por cookie. Si la aplicación autentica con una cabecera —`Authorization: Bearer`— no hay CSRF por esta vía, porque el navegador no adjunta esa cabecera sola; ahí el dominio se vuelve el de [[Control de acceso - IDOR]] o el de CORS mal configurado.

Cuando el token existe y sí está ligado a la sesión, se pasa a [[CSRF - double submit y cookie inyectada]] o, si la defensa real es la cookie, a [[CSRF - bypass de SameSite]].

## Por qué funciona

El token sincronizador prueba una sola cosa: que quien manda la petición **pudo leer una página de la aplicación**. Esa prueba se cae de cinco maneras, y las cinco son fallos de implementación, no de diseño:

- **El token no se valida si no está.** El código comprueba `if (isset($token))` y sin el parámetro no entra a comparar nada.
- **El token no está ligado a la sesión.** Es válido, pero cualquiera sirve: el atacante saca uno de su propia cuenta y lo usa contra la víctima.
- **La validación depende del método.** El `POST` valida y el `GET` no, o el marco de trabajo solo protege los métodos que considera inseguros.
- **El token viaja en una cookie propia** en vez de en la sesión — ese caso es [[CSRF - double submit y cookie inyectada]].
- **El token es predecible**: correlativo, derivado del identificador de usuario, o el mismo para toda la aplicación.

Ninguna de las cinco requiere ingenio. Requiere probarlas en orden, que es lo que hace la matriz.

## Cómo falla

Falla cuando el token está ligado a la sesión del lado del servidor y se compara en tiempo constante contra el valor guardado. Es el caso normal en cualquier marco de trabajo moderno con la protección encendida, y es el punto en el que hay que dejar esta rama.

Falla también cuando la acción exige la contraseña actual o un segundo factor: el token deja de ser la única prueba y CSRF solo no alcanza. Contra eso, la salida no es este dominio sino [[XSS - reflejado]], que se salta todo porque ejecuta **dentro** del origen.

Y falla silenciosamente cuando la aplicación es de página única y la acción se hace por `fetch` con una cabecera personalizada: esa cabecera dispara el control previo de CORS, que es una defensa que este ataque no evade. Ahí se pasa a [[CSRF - endpoint que espera JSON]].

## Coste

Bajo. Cinco peticiones para las cinco pruebas, y la mitad se descartan por el código de respuesta sin mirar el cuerpo.

El coste real es de reconocimiento: encontrar la acción que vale la pena. Un cambio de correo o de contraseña sin reautenticación es toma de cuenta completa; un cambio de preferencia de idioma es un hallazgo informativo. La misma vulnerabilidad, dos severidades incomparables.

## Huella esperada

La petición llega con la sesión de la víctima y aspecto normal. Lo único anómalo está en dos campos:

- **`Referer` de otro origen** —o ausente— sobre una acción que cambia estado, en [[Log de acceso del servidor web]].
- **La acción sin la navegación previa que la precede siempre**: nadie cambia su correo sin abrir antes la página de perfil. Es un invariante sobre la secuencia, no una firma, y por eso cae en [[Log de auditoría de la aplicación]] y no en una regla de evento.

Durante la prueba, además, quedan varias peticiones con token inválido o ausente que devuelven `403`. Esa ráfaga es la parte ruidosa y es lo que separa la prueba del ataque real, que es una sola petición.
