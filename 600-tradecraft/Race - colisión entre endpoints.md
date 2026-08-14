---
tipo: tradecraft
clase: "[[CWE-362 - Concurrent Execution using Shared Resource with Improper Synchronization]]"
eje: tipo-de-ventana
implementacion: "Disparar dos operaciones distintas a la vez para que se crucen en un estado intermedio inconsistente"
opsec: ruidoso
telemetria: ["[[Log de auditoría de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [dos-operaciones-que-comparten-estado-y-no-deben-cruzarse]
coste: alto
alternativas: ["[[Race - superación de límite]]", "[[Race - subestado oculto]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - multi-endpoint race
  - colisión multi-endpoint
tags:
  - dominio/web
---

# Race - colisión entre endpoints

## Cuándo lo elijo

Cuando la ventana no está en una sola operación repetida sino **entre dos operaciones distintas** que comparten estado y no deberían ejecutarse cruzadas. No es "hacer lo mismo N veces" —eso es [[Race - superación de límite]]— sino "hacer A y B a la vez para que B pase mientras A todavía está a medias".

Se reconoce cuando hay un flujo de dos pasos donde el estado intermedio es aprovechable: aplicar un descuento mientras se confirma el pago, cambiar el correo mientras se envía la verificación, agregar a un carrito mientras se cobra.

## Por qué funciona

Muchas operaciones dejan el sistema, por un instante, en un estado que ninguna interfaz muestra pero que es válido si se lo alcanza. Dos peticiones a **endpoints distintos** que llegan juntas se cruzan en ese estado:

- **Aplicar un cupón mientras se confirma el pedido.** El precio se calcula en un paso y se cobra en otro; si el cupón se aplica en la ventana entre ambos, se cobra el precio viejo con el descuento nuevo, o se aplica dos veces.
- **Cambiar de correo mientras se dispara la verificación.** El token de verificación se genera para el correo A y se envía; si el correo se cambia a B en la ventana, el token válido para A llega a B o valida B.
- **Confirmar una amistad/permiso mientras cambia el rol**, dejando un permiso que no correspondía.

La diferencia técnica con la superación de límite es que las peticiones van a **URLs distintas** y a veces necesitan un orden aproximado —A tiene que estar a medias cuando llega B—. Eso complica la sincronización: no alcanza con que lleguen juntas, tienen que llegar juntas **en el punto correcto del procesamiento**. El ataque de un solo paquete y el calentamiento de conexión de [[Race - matriz de disparo]] siguen siendo la base, pero el ajuste es más fino.

## Cómo falla

Falla contra transacciones que abarcan el flujo completo, de modo que el estado intermedio nunca es visible para otra petición. Es la mitigación correcta y la más difícil de implementar bien, por lo que este tipo es de los que más sobrevive en producción.

Falla cuando las dos operaciones no comparten estado de verdad —parecían cruzarse y no—, que se descubre probando y viendo que nada inconsistente queda.

Y falla cuando el orden requerido es demasiado estrecho para acertarlo con la dispersión que queda aun con el ataque de un solo paquete.

## Coste

Alto, el más alto del dominio. Requiere entender el flujo de negocio lo bastante como para saber qué estado intermedio existe y qué dos operaciones lo cruzan, y después acertar la sincronización fina entre endpoints distintos. Es el que más reconocimiento de lógica de negocio pide de todo el vault web.

Conviene mapear el flujo primero —qué pasos tiene, qué estado queda entre ellos— y solo entonces construir la colisión. Tirar ráfagas a ciegas contra dos endpoints rara vez da.

## Huella esperada

Como toda la familia, cada petición es válida y la señal está en el cruce, no en el contenido:

- En [[Log de acceso del servidor web]] quedan **dos ráfagas a endpoints distintos con timestamps entrelazados** —no una ráfaga idéntica como en la superación de límite, sino dos flujos que normalmente son secuenciales llegando solapados—. Es más difícil de ver que la ráfaga simple, porque no son peticiones iguales.
- La confirmación vuelve a ser de **invariante** en [[Log de auditoría de la aplicación]]: un estado final imposible —un pedido con descuento y sin el cupón consumido, un correo verificado que no coincide con el que recibió el token—. Es `forma: invariante` y la única señal que confirma el ataque.

La detección natural es la misma que en [[Race - superación de límite]] —el invariante roto— pero el agregado es más débil acá, porque no hay una ráfaga idéntica que salte a la vista. Refuerza que en este dominio la cara azul aprovechable es la del invariante sobre el resultado, no la de la firma sobre la petición. Anotado en [[MOC - Race conditions]].
