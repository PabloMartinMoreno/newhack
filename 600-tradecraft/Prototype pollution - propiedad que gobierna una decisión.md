---
tipo: tradecraft
clase: "[[CWE-1321 - Prototype Pollution]]"
eje: gadget
implementacion: "Contaminar una propiedad que el código consulta para decidir, sin necesitar ninguna cadena"
opsec: limpio
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]", "[[Registro del WAF]]"]
requisitos: [contaminacion-confirmada, propiedad-consultada-con-valor-por-defecto]
coste: bajo
alternativas: ["[[Prototype pollution - gadget del lado del servidor]]", "[[Control de acceso - mass assignment]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - property injection
  - pollution a bypass de autorización
tags:
  - dominio/web
---

# Prototype pollution - propiedad que gobierna una decisión

## Cuándo lo elijo

Siempre primero, apenas [[Prototype pollution - matriz de identificación]] confirma que se puede contaminar. No necesita gadget, no necesita conocer las bibliotecas cargadas, y cuesta una petición.

La condición es que exista alguna propiedad que el código consulte para decidir algo y que **normalmente no esté definida**. Eso es más frecuente de lo que parece: cualquier bandera opcional, cualquier campo de rol que solo aparece en algunos usuarios, cualquier opción de configuración con valor por defecto.

Si no hay ninguna propiedad así, o si el objetivo es ejecución, se pasa a [[Prototype pollution - gadget del lado del servidor]].

## Por qué funciona

La contaminación no crea la propiedad en el objeto: la hace aparecer en **todos** los objetos que no la definan. Y ahí está la parte que hay que entender, porque decide qué se puede atacar:

```js
if (usuario.esAdmin) { ... }        // vulnerable si esAdmin no está definido
if (usuario.rol === 'admin') { ... } // vulnerable solo si rol falta
```

La comprobación `if (opciones.saltearValidacion)` sobre un objeto de opciones que casi nunca trae ese campo es explotable; la misma comprobación sobre un campo que siempre viene del cliente, no. **Lo que se ataca es la ausencia, no el valor** — el prototipo solo se consulta cuando la propiedad propia no existe.

De ahí el método de trabajo: en vez de buscar el campo que gobierna, se contamina un lote de nombres plausibles y se mira qué cambia en la respuesta.

Es exactamente [[Control de acceso - mass assignment]] por otro camino, y conviene tenerlo presente porque la lista de nombres a probar es la misma. La diferencia es que mass assignment escribe en **un** objeto y esto escribe en todos, incluidos los que el atacante no puede alcanzar por parámetro — objetos internos, de configuración, de sesión de otros usuarios.

Ese último punto es el que sube la severidad: el efecto es global al proceso, así que una bandera contaminada puede afectar peticiones de otras personas.

## Cómo falla

Falla cuando el objeto que decide se construye con `Object.create(null)` o es un `Map`, que es la mitigación correcta y cada vez más común en código nuevo.

Falla cuando las propiedades que gobiernan siempre están definidas —vienen de la base de datos con valor explícito—, porque entonces el propio valor gana sobre el prototipo. Es el caso más frecuente y el que hace que esta rama no siempre rinda.

Y falla, en el sentido de que se vuelve difícil de demostrar, cuando el efecto es global: si la aplicación corre varios procesos detrás de un balanceador, la contaminación queda en uno solo y las peticiones siguientes pueden caer en otro. Se ve como un comportamiento intermitente que parece un error de la prueba y no lo es.

> [!warning] Esto ensucia el proceso
> El prototipo contaminado sobrevive a la petición y afecta a todos los usuarios hasta que el proceso se reinicie. Contaminar `esAdmin` en producción es cambiar el comportamiento de la aplicación para terceros. Elegir un nombre de propiedad inventado para las pruebas de confirmación —y solo tocar los reales cuando haga falta demostrar— es parte del trabajo, no una cortesía.

## Coste

Bajo. Una petición para contaminar y otra para observar. Probar un lote de veinte nombres plausibles son veinte pares de peticiones y se automatiza en un rato.

Lo que puede encarecer es demostrar el impacto: si la propiedad afecta una ruta administrativa que el atacante no ve, hay que encadenar la contaminación con una petición desde otro contexto, y con varios procesos de por medio eso se vuelve poco fiable.

## Huella esperada

La contaminación en sí viaja en la petición y **es visible como texto**: `__proto__` o `constructor[prototype]` en la query string o en el cuerpo JSON. Es de los pocos casos del vault donde una detección de **firma** funciona razonablemente bien, porque esas cadenas no aparecen en tráfico legítimo casi nunca — ver la nota sobre esto en [[MOC - Prototype pollution]].

Queda en [[Log de acceso del servidor web]] si viaja por la URL, y en [[Registro del WAF]] si viaja por el cuerpo. La detección existente que la cubre es [[Payload de inyección en parámetros de la URL]], que es de firma y lo declara.

El efecto queda en [[Log de auditoría de la aplicación]] con el mismo perfil que cualquier escalada: **un privilegio ejercido sin el cambio de estado que debería haberlo concedido**. Lo cubre [[Cambio de privilegio fuera del flujo administrativo]] sin saber que hubo contaminación de por medio.

Hay una huella indirecta que conviene mencionar en el informe porque es la que más veces delata el problema en producción: **comportamiento anómalo para usuarios que no atacaron nada**. Un prototipo contaminado produce errores raros y dispersos que nadie asocia con un ataque.
