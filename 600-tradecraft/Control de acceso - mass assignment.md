---
tipo: tradecraft
clase: "[[CWE-915 - Improperly Controlled Modification of Dynamically-Determined Object Attributes]]"
eje: vector
implementacion: "Agregar campos no previstos a una petición que el marco de trabajo asigna automáticamente"
opsec: limpio
telemetria: ["[[Log de auditoría de la aplicación]]"]
requisitos: [endpoint-de-escritura, asignacion-automatica]
coste: bajo
alternativas: ["[[Control de acceso - escalada vertical]]"]
probado: nunca
contexto: [api-rest]
aliases:
  - escalada por campo de más
  - asignación masiva
tags:
  - dominio/web
---

# Control de acceso - mass assignment

## Cuándo lo elijo

Cuando hay un endpoint de escritura que acepta un objeto estructurado —típicamente JSON— y el marco de trabajo detrás asigna los campos automáticamente. Es la vía a escalada vertical que no requiere encontrar ninguna ruta administrativa: se usa una función legítima y se le agrega un campo de más.

El reconocimiento es asimétrico y en eso está la gracia: **la respuesta enseña qué pedir**. Si un `GET` del objeto devuelve campos que el formulario de edición no muestra, esos campos son la lista de candidatos, ya documentada por la propia aplicación. Después se reenvían en el `PUT` o el `PATCH` y se comprueba si tomaron.

Vale intentarlo siempre en el registro de usuarios: es el endpoint donde más veces existe el campo de rol y menos veces está protegido, porque lo escribe alguien pensando en el alta y no en el modelo de permisos.

## Por qué funciona

La asignación automática es una comodidad del marco de trabajo que no distingue entre un campo que el usuario debía poder editar y uno que no. Esa distinción vive **solo en la intención del programador** y no está escrita en ningún lado que el código pueda consultar.

El resultado es que el control de acceso, aunque exista, opera al nivel equivocado: verifica que este usuario pueda modificar **este objeto**, no que pueda modificar **este atributo del objeto**. Editar el propio perfil está permitido; que el propio perfil incluya el campo de rol es un detalle que nadie revisó.

## Cómo falla

- **Lista blanca de campos asignables** — la mitigación correcta. Los campos de más se descartan en silencio y no pasa nada.
- **Los campos extra provocan un error de validación** — la petición se rechaza entera. A veces se evita anidando el campo donde el validador no mira.
- **El campo se asigna y otra capa lo pisa** — el valor entra al objeto y el servidor lo sobrescribe al guardar. Parece que funcionó hasta que se relee el objeto.
- **El nombre del campo interno no es el que devuelve la API** — la respuesta muestra `admin` y el modelo espera `is_admin` o `role_id`. Hay que probar variantes, y ahí sí conviene la lista de convenciones de [[Control de acceso bypass - matriz de referencia]].
- **El cambio requiere reautenticación para tomar efecto** — el campo se escribió y el token viejo sigue teniendo el rol viejo.
- **Solo funciona en creación, no en actualización** — o al revés. Son rutas distintas con validaciones distintas: hay que probar ambas.

## Coste

Bajo. Una petición por campo candidato, y los candidatos los da la propia respuesta del servidor. Es de las técnicas con mejor relación esfuerzo/impacto de todo el vault: un campo de más en un JSON puede ser administrador.

## Huella esperada

Es la variante **más silenciosa del dominio**, y por márgenes amplios.

- La petición es una operación legítima sobre un objeto propio, con la sesión propia. No hay ruta rara, no hay identificador ajeno, no hay error. Desde [[Log de acceso del servidor web]] es indistinguible de un usuario editando su perfil.
- [[Log de auditoría de la aplicación]] la ve **solo si registra qué campos cambiaron**. Ese es el campo que casi nunca se instrumenta, y sin él no queda nada: el registro dirá "el usuario A actualizó su perfil", que es exactamente lo que pasó.
- La detección viable no está en el evento sino en la consecuencia: **un cambio de rol que no vino del flujo administrativo**. Se detecta comparando el estado, no observando la petición.

Esa asimetría —escritura crítica, evento trivial— la vuelve el caso donde más se nota que [[Log de auditoría de la aplicación]] tiene que registrar el detalle del cambio y no solo la operación.
