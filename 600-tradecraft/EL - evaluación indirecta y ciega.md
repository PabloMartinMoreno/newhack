---
tipo: tradecraft
clase: "[[CWE-917 - Expression Language Injection]]"
eje: superficie
implementacion: "Inyectar en un campo que el framework evalúa como EL en un mensaje de validación, error o registro, sin ver el resultado"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Conexión saliente del servidor de aplicación]]", "[[Consulta DNS saliente]]", "[[Log de errores del servidor web]]"]
requisitos: [entrada-evaluada-fuera-de-la-respuesta]
coste: medio
alternativas: ["[[EL - reflejo directo en expresión]]", "[[EL - OGNL en el framework]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - bean validation injection
  - EL ciego
  - validation message EL
tags:
  - dominio/web
---

# EL - evaluación indirecta y ciega

## Cuándo lo elijo

Cuando la sospecha de EL existe pero `${7*7}` no vuelve como `49` en ninguna parte de la respuesta. Es el caso que separa a este dominio de SSTI: la expresión se evalúa en un lugar que no devuelve su resultado, y hay que confirmarla a ciegas.

El punto más frecuente es el **mensaje de una validación de bean**: una anotación de validación cuyo mensaje de error se construye con el valor rechazado y se evalúa como EL antes de mostrarse. El valor entra, la validación falla, y al armar el mensaje de error el framework evalúa la expresión que el atacante metió. También aparece en registros que interpolan EL y en plantillas de correo del lado del servidor.

Si la evaluación fuera reflejada, la rama sería [[EL - reflejo directo en expresión]]; si la entrada la evaluara el framework al procesar la petición, [[EL - OGNL en el framework]].

## Por qué funciona

El framework evalúa EL en lugares que el programador de la aplicación no piensa como puntos de inyección. El caso canónico de la validación de bean es instructivo: el mensaje de una restricción como `@Size` puede contener EL, y algunas versiones lo evaluaban sobre el **valor rechazado**. Un valor que falla la validación y contiene `${...}` termina evaluado al construir el mensaje de "valor inválido".

El programador nunca escribió una expresión con entrada del usuario. El framework la creó por él, al interpolar el valor en el mensaje. Ese es el patrón del dominio entero: la expresión aparece donde nadie la puso.

Como no se ve el resultado, la confirmación es por **canal fuera de banda**, igual que en [[Command injection - canal fuera de banda]] y [[SSTI - matriz de identificación]] cuando no hay reflejo:

- Una expresión que resuelve un nombre de dominio propio: si llega la consulta DNS, se evaluó.
- Una expresión que hace una petición HTTP a un servidor propio.
- Un retardo medible, cuando ni siquiera el egress está disponible.

Los payloads de confirmación ciega por motor están en [[EL injection payloads - matriz de referencia]].

## Cómo falla

Falla contra frameworks parcheados: la evaluación de EL en mensajes de validación fue un fallo concreto que se cerró, así que las versiones nuevas no evalúan el valor rechazado.

Falla cuando no hay ningún canal de salida: sin egress HTTP, sin DNS saliente y sin poder medir tiempo, una evaluación ciega no se puede confirmar y queda como sospecha. Es el peor caso del dominio y a veces no se supera.

Y falla, como la rama reflejada, contra un sandbox activo del motor.

## Coste

Medio. La técnica en sí es una petición por motor, pero montar el canal fuera de banda —un servidor propio que reciba la consulta DNS o el HTTP— es trabajo previo, y sin él la rama no avanza.

El coste de reconocimiento también sube: hay que encontrar el campo cuyo valor se evalúa, que no se delata solo porque nada vuelve en la respuesta. Se prueban los campos que pasan por validación con un payload de confirmación ciega y se observa el canal.

## Huella esperada

Es la rama con más huella propia del dominio, y a favor del defensor, porque la confirmación ciega **obliga al servidor a salir a la red**:

- La confirmación por DNS deja rastro en [[Consulta DNS saliente]] — un subdominio con un identificador, que es exactamente la firma de [[Exfiltración por subdominios de alta entropía]].
- La confirmación por HTTP, o una segunda etapa descargada, deja rastro en [[Conexión saliente del servidor de aplicación]], que cubren [[Barrido de puertos internos desde el servidor de aplicación]] y [[Petición al servicio de metadatos de instancia]] según el destino.
- Cuando escala a ejecución, nace el proceso hijo del servidor web y lo ve [[Intérprete de comandos como hijo del servidor web]].

Y el reconocimiento fallido llena [[Log de errores del servidor web]] de excepciones de EL, igual que la rama reflejada. La diferencia es que acá el atacante **no ve esas excepciones** —no vuelven en la respuesta—, así que el defensor tiene una ventaja de información: ve los errores que el atacante está causando a ciegas.
