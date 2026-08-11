---
tipo: tradecraft
clase: "[[CWE-287 - Improper Authentication]]"
eje: fase-del-flujo
implementacion: "Cambiar la identidad en los datos que el cliente acepta sin poder verificarlos"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [flujo-implicito-o-identidad-por-parametro]
coste: bajo
alternativas: ["[[OAuth - validación del id_token]]", "[[OAuth - redirect_uri mal validado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - implicit flow
  - OAuth authentication bypass
tags:
  - dominio/web
---

# OAuth - flujo implícito y token no verificable

## Cuándo lo elijo

Cuando el flujo devuelve el token en el **fragmento** de la URL —`response_type=token` o `id_token`— y el cliente lo recibe por JavaScript, o cuando la petición final que autentica al usuario incluye su identidad como parámetro que el atacante puede tocar.

La señal en el tráfico es directa: después de volver del proveedor hay una petición al propio cliente que lleva el correo, el identificador de usuario o el token en un campo modificable. Si esa petición existe, esta rama es la primera a probar porque cuesta una petición y no deja ruido.

Cuando el cliente sí verifica una firma y el problema está en cómo la verifica, la rama es [[OAuth - validación del id_token]].

## Por qué funciona

El flujo implícito nació para aplicaciones de página única que no podían guardar un secreto de cliente. La consecuencia es que los datos vuelven por el navegador de la víctima, o sea **por un canal que el atacante controla**, y no por el canal directo entre el cliente y el proveedor.

El error que sigue es de razonamiento: el que integra ve que los datos vienen del proveedor y los trata como confiables, cuando lo único que sabe es que pasaron por el navegador. De ahí salen las tres variantes:

- **La identidad viaja como parámetro.** La aplicación manda `POST /login {email: "victima@x.com", token: "..."}` y solo comprueba que el token sea válido, sin comprobar que pertenezca a ese correo. Cambiar el correo entra a la cuenta ajena.
- **El token de acceso no está atado al cliente.** Un token emitido para la aplicación del atacante se acepta en la aplicación objetivo. Es el problema que OpenID Connect resuelve con `aud` en el `id_token`, y que no existe si el cliente solo usa un token de acceso para preguntar "¿quién sos?".
- **El identificador de usuario se toma de una respuesta que no se verifica.** Igual que arriba, pero con un campo distinto.

La segunda es la más elegante y la que se pasa por alto: el atacante registra su propia aplicación en el mismo proveedor, consigue que una víctima la use, y reutiliza ese token contra el objetivo. No hace falta ninguna redirección desviada.

## Cómo falla

Falla contra el flujo de código de autorización con canje del lado del servidor, donde el token nunca pasa por el navegador. Es la recomendación de fondo y es lo que dice la especificación desde 2020: el flujo implícito está desaconsejado, punto.

Falla cuando el cliente valida `aud` en el `id_token`, que es lo que ata el token a esa aplicación y anula la segunda variante.

Y falla cuando la identidad no viaja como parámetro sino que se deriva del token del lado del servidor, que es la implementación correcta y la más común en bibliotecas mantenidas.

## Coste

Bajo, el más bajo del dominio. Una petición modificada y se sabe.

Es también el de mejor retorno por su relación coste/impacto: no necesita interacción de la víctima —a diferencia de [[OAuth - redirect_uri mal validado]] y [[OAuth - falta de state]]—, así que cuando funciona no hay techo de severidad por requisitos.

## Huella esperada

Es la variante limpia del dominio y por eso el `opsec: limpio`: no hay redirecciones raras, no hay errores del proveedor, no hay ráfaga de peticiones fallidas. Una petición modificada que devuelve `200`.

La única señal está en [[Log de autenticación de la aplicación]] y es un desajuste, no una firma: **la identidad que se autenticó no coincide con la que el proveedor emitió el token**. Detectarlo exige registrar las dos cosas, que es justo lo que las implementaciones vulnerables no hacen — si la aplicación distinguiera ambos valores, no sería vulnerable.

Es el mismo tipo de límite que documenta [[Un log sin identidad es un historial, no una detección]]: la regla no es difícil de escribir, es imposible sin el campo. La recomendación defensiva de mayor retorno acá no es una detección sino instrumentar el registro para que guarde el sujeto del token junto al usuario autenticado.

Del lado del proveedor, la segunda variante deja algo visible que el cliente no puede ver: **un token emitido para una aplicación y presentado a otra**. Solo el proveedor lo detecta, y solo si compara `aud` con quien consulta.
