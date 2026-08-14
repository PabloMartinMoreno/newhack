---
tipo: tradecraft
clase: "[[CWE-362 - Concurrent Execution using Shared Resource with Improper Synchronization]]"
eje: tipo-de-ventana
implementacion: "Enviar varias peticiones en la misma ventana para usar N veces algo pensado para una sola"
opsec: ruidoso
telemetria: ["[[Log de auditoría de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [operación-con-límite-verificado-antes-de-aplicarse]
coste: medio
alternativas: ["[[Race - colisión entre endpoints]]", "[[Race - subestado oculto]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - limit overrun
  - superación de límite
tags:
  - dominio/web
---

# Race - superación de límite

## Cuándo lo elijo

Es el caso base del dominio y el primero a probar. Se busca una operación con un **límite** —un saldo, un cupo, un uso único, un "una vez por cuenta"— que se verifica antes de aplicarse, y se disparan varias peticiones a la vez para pasar la verificación N veces antes de que se actualice el estado.

Se reconoce por el patrón de negocio, no por la respuesta: cualquier "solo podés hacer esto una vez / hasta N veces" es candidato. Si la colisión necesita dos operaciones distintas coordinadas, la rama es [[Race - colisión entre endpoints]]; si hay un estado multipaso oculto, [[Race - subestado oculto]].

## Por qué funciona

La lógica vulnerable es siempre la misma: **comprobar, después actuar**, con una ventana en el medio.

```
if (saldo >= monto) {      # comprobar
    # ← ventana: otra petición entra acá
    saldo -= monto          # actuar
}
```

Si veinte peticiones llegan dentro de la ventana, las veinte leen el saldo original, las veinte pasan la comprobación, y las veinte descuentan. El límite se supera tantas veces como peticiones entren juntas.

Los objetivos donde más rinde:

- **Tarjetas de regalo, cupones, créditos**: canjear el mismo saldo varias veces.
- **Retiros y transferencias**: sacar más de lo que hay.
- **"Un voto / una reseña / un like por cuenta"**: multiplicar.
- **Códigos de invitación o descuentos de un solo uso**: reutilizar.
- **Límites de tasa de la propia aplicación**: si el contador se comprueba antes de incrementarse, se supera.

La clave técnica es que las peticiones lleguen dentro de la ventana, y eso lo resuelve el **ataque de un solo paquete** sobre HTTP/2 o la sincronización por último byte sobre HTTP/1.1. La mecánica completa está en [[Race - matriz de disparo]] — es lo que separa un intento fallido por jitter de uno que funciona.

## Cómo falla

Falla contra atomicidad: si la comprobación y la acción son una transacción indivisible con bloqueo, no hay ventana. Es la mitigación correcta.

Falla contra una restricción a nivel de datos —un índice único que impide dos canjes del mismo código, un `CHECK` que prohíbe saldo negativo—: aunque la lógica tenga la ventana, la base rechaza la segunda escritura. Es la defensa que sobrevive incluso a la lógica mal escrita, y la que hay que recomendar.

Y falla, prácticamente, cuando la ventana es demasiado corta o el servidor procesa las peticiones estrictamente en serie: ahí ni el ataque de un solo paquete alcanza.

## Coste

Medio. Con herramienta —Turbo Intruder de Burp trae el ataque de un solo paquete listo— construir la ráfaga es una plantilla. El trabajo es de reconocimiento: encontrar la operación con límite que valga la pena, y calibrar cuántas peticiones y con qué técnica de sincronización.

A veces hace falta **calentar la conexión** —mandar peticiones previas para que el servidor tenga los recursos listos— y afinar el número de peticiones concurrentes: pocas no colisionan, demasiadas se serializan. Es prueba y ajuste, y está en la matriz.

## Huella esperada

Silenciosa en contenido, ruidosa en un patrón muy específico:

- La señal directa es **una ráfaga de peticiones idénticas casi simultáneas** al mismo endpoint —veinte canjes de la misma tarjeta en el mismo milisegundo—. En [[Log de acceso del servidor web]] eso es un pico de peticiones idénticas con timestamps pegados, una firma de agregado clarísima si alguien mira la cadencia.
- La señal que de verdad importa, y la única que confirma el daño, es de **invariante**: el saldo quedó negativo, la tarjeta figura canjeada dos veces, hay más votos que votantes. Eso vive en [[Log de auditoría de la aplicación]] y es `forma: invariante` —una condición que nunca debería violarse—, el mismo tipo de detección que [[Actividad de sesión posterior a su cierre]].

Es el dominio que más claramente pide detección por invariante: como cada petición es individualmente legítima, no hay firma que valga, y lo único que distingue el ataque es que **el resultado es imposible**. La ráfaga simultánea es candidato de agregado, la violación del invariante es la confirmación. Los dos quedan anotados en [[MOC - Race conditions]] — ninguna detección del vault los implementa aún, pero los dos son escribibles con la telemetría de aplicación que ya se modela.
