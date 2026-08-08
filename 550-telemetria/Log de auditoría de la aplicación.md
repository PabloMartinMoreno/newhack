---
tipo: telemetria
plataforma: [linux, windows]
producto: la propia aplicación
identificador: "evento de auditoría"
por-defecto: false
coste: bajo
aliases:
  - audit log
  - log de auditoría
  - eventos de negocio
tags:
  - dominio/web
---

# Log de auditoría de la aplicación

## Qué lo genera

La aplicación misma, cuando registra **qué usuario hizo qué sobre qué objeto**. No lo emite el servidor web ni el sistema operativo: hay que escribirlo en el código.

Es el único artefacto que ve el dominio de [[MOC - Broken access control]], y la razón es estructural: un ataque de control de acceso **no produce ninguna anomalía técnica**. La sesión es válida, la petición está bien formada, la respuesta es `200`. Lo único anómalo es la relación entre la identidad y el objeto, y esa relación solo la conoce la aplicación.

Sin esta fuente, todo el dominio es invisible. Con ella, es de los más fáciles de detectar.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Identidad del actor | Usuario autenticado, no la IP | El campo central: sin esto la fuente no sirve para nada |
| Objeto afectado | Tipo e identificador del recurso | Permite preguntar de quién era |
| Dueño del objeto | A quién pertenecía | **La comparación con el actor es toda la detección** |
| Acción | Leer, crear, modificar, borrar | Separa curiosidad de daño |
| Resultado | Permitido o denegado | Los denegados en ráfaga son reconocimiento |
| Rol efectivo | Con qué privilegio se resolvió | Detecta escalada vertical |
| Campos modificados | Qué atributos cambiaron | Lo único que ve [[Control de acceso - mass assignment]] |

Las filas tres y siete son las que casi nunca están, y son justo las que convierten esta fuente en detección en vez de en archivo.

## Coste de recolección

Bajo en volumen —un evento por operación de negocio, órdenes de magnitud menos que el log de acceso— y **alto en implementación**, que es su verdadero problema. Ninguna configuración lo enciende: hay que instrumentar la aplicación, decidir qué es auditable y mantenerlo cuando el código cambia.

Por eso es el artefacto más valioso y el que menos existe.

## Cómo se activa

No se activa: se construye. Algunos marcos de trabajo y ORM ofrecen registro automático de cambios, que cubre las escrituras y deja las lecturas afuera — y las lecturas son la mitad del dominio, porque un IDOR de lectura no modifica nada.

En productos comerciales suele existir con nombre propio y hay que pedirlo explícitamente. Casi siempre viene apagado por volumen.

## Limitaciones

- **Solo ve lo que la aplicación decidió registrar.** Si un endpoint no está instrumentado, el ataque a través de él no existe para esta fuente. La cobertura es tan desigual como el código.
- **Registrar solo lo denegado no alcanza.** El caso grave de control de acceso es el que se **permite**: no hay denegación que registrar. Auditar únicamente los rechazos es el error de diseño más común en esta fuente.
- **Sin el dueño del objeto no hay detección posible**, solo un historial. Es la diferencia entre "el usuario A leyó el documento 4021" y "el usuario A leyó el documento 4021, que pertenece a B".
- **Retención.** Un abuso de control de acceso se descubre semanas después, por reclamo de un cliente. Si la retención es de siete días, la evidencia no existe cuando se la busca.

## Quién lo emite / quién lo consume

Rojo: [[Control de acceso - IDOR]] · [[Control de acceso - escalada vertical]] · [[Control de acceso - mass assignment]] · [[Control de acceso - salto de contexto]]
Azul: pendiente — ver [[Consultas del vault]] § Huecos defensivos propios
