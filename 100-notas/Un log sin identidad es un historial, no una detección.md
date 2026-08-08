---
tipo: zettel
relacionadas: ["[[Log de auditoría de la aplicación]]", "[[Acceso a un objeto de otro usuario]]"]
aliases:
  - instrumentación antes que reglas
tags: []
---

# Un log sin identidad es un historial, no una detección

## Idea

Un registro puede ser completo, estar bien formado, conservarse años y **no servir para detectar nada**. Lo que decide no es que el evento esté: es que estén los campos con los que se puede hacer la pregunta.

"El usuario A leyó el documento 4021" es cierto, es preciso y es inútil. "El usuario A leyó el documento 4021, **que pertenece a B**" es una detección. La diferencia es un campo.

## Por qué importa

Porque cambia qué hay que recomendar. Frente a una clase de ataque que no se detecta, la respuesta instintiva es escribir una regla mejor. A veces la regla es imposible y lo que falta es **un campo**.

En este vault hay tres casos, y en los tres la nota lo dice en una sección propia:

| Falta | Bloquea |
|---|---|
| dueño del objeto | detectar acceso a datos ajenos |
| campos modificados | detectar escalada por escritura |
| motivo del fallo de acceso | distinguir enumeración de adivinanza de contraseñas |

Ninguna de esas reglas es difícil. **Son imposibles** sin el campo, y confundir las dos cosas hace descartar como "no detectable" algo que solo necesitaba una línea de instrumentación.

## El caso que lo muestra entero

Los ataques de control de acceso no producen ninguna anomalía técnica: la petición es válida, la sesión legítima, la respuesta correcta. La anomalía es **la relación entre dos campos**, y si uno de los dos no se registra, no hay nada que comparar.

Por eso la recomendación defensiva de mayor retorno de todo el dominio web no es una regla de detección: es **registrar el dueño del objeto**. Y por eso conviene reportarlo como requisito de instrumentación y no como detalle de implementación — si va en la sección equivocada del informe, nadie lo prioriza.

## Consecuencias

- **Antes de escribir una regla, verificar que los campos existen.** Si no, la prueba falla por falta de datos y no por la regla, y se descarta una regla buena.
- **Auditar solo lo denegado no alcanza.** El caso grave de control de acceso es el que se **permite**: no hay denegación que registrar. Es el error de diseño más común en registros de auditoría.
- **Los registros que emite la aplicación son los únicos que conocen la semántica.** Ninguna fuente del sistema operativo o de red sabe de quién es un objeto. Esa capa hay que programarla.
- **Retención.** Un abuso de acceso se descubre semanas después por un reclamo. Con siete días de retención, la evidencia no existe cuando se la busca.

## Fuente

Destilado de escribir la cara azul de los dominios de control de acceso y autenticación de este vault.
