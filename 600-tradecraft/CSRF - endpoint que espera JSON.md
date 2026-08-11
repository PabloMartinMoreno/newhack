---
tipo: tradecraft
clase: "[[CWE-352 - Cross-Site Request Forgery]]"
eje: defensa
implementacion: "Mandar el cuerpo JSON con un tipo de contenido que no dispare el control previo de CORS"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]", "[[Registro del WAF]]", "[[Log de errores del servidor web]]"]
requisitos: [api-con-sesion-por-cookie, sin-token-en-cabecera]
coste: medio
alternativas: ["[[CSRF - token ausente o no ligado]]", "[[CSRF - bypass de validación de origen]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - CSRF en API JSON
  - simple request
tags:
  - dominio/web
---

# CSRF - endpoint que espera JSON

## Cuándo lo elijo

Cuando la acción vive en una API que recibe JSON y la sesión sigue viajando por cookie. Es la forma que toma el dominio en aplicaciones de página única, y la que más veces se descarta por error con el argumento de que "las API no tienen CSRF".

La condición que hay que confirmar antes de invertir tiempo: que la autenticación sea **por cookie**. Si el cliente manda un token en `Authorization`, el navegador no lo adjunta solo y no hay ataque por esta vía.

## Por qué funciona

El navegador solo pide permiso al servidor —el control previo de CORS— cuando la petición sale de un conjunto acotado. Una petición se considera simple y **se envía sin preguntar** si usa `GET`, `HEAD` o `POST` y su tipo de contenido es uno de tres: `application/x-www-form-urlencoded`, `multipart/form-data` o `text/plain`.

`application/json` no está en la lista, y ahí está la defensa accidental: la mayoría de las API JSON están protegidas por casualidad, no por diseño. Se rompe cuando el servidor es tolerante con el tipo de contenido:

- **Acepta `text/plain` con cuerpo JSON.** Muchos analizadores ignoran la cabecera y parsean igual. Un formulario con `enctype="text/plain"` manda el cuerpo tal cual.
- **Acepta el cuerpo con codificación de formulario** y lo mapea a los mismos campos, que es el comportamiento por defecto de varios marcos de trabajo.
- **Acepta `multipart/form-data`**, que también es simple.

El truco del formulario con `text/plain` es el que hay que conocer: el navegador serializa como `nombre=valor`, así que se pone el JSON entero en el **nombre** del campo y se cierra la llave con el valor. Está en [[CSRF entrega - matriz de referencia]].

## Cómo falla

Falla cuando el servidor exige `application/json` de verdad y rechaza cualquier otro tipo. Es una línea de configuración y cierra la rama entera.

Falla contra cualquier cabecera personalizada obligatoria —`X-Requested-With`, `X-CSRF-Token`—: pedir una cabecera que no está en la lista de simples **fuerza el control previo**, y el control previo es una defensa que este ataque no evade. No importa qué valor tenga la cabecera; importa que exista, porque su sola presencia saca a la petición del conjunto simple.

Ese es el punto que más rinde en el informe: la mitigación no es validar el contenido de una cabecera, es exigirla.

Y falla, por supuesto, si hay token ligado a la sesión.

## Coste

Medio. Confirmar la tolerancia al tipo de contenido son tres peticiones. Construir el formulario que produce un JSON válido con `text/plain` es fiddly —hay que hacer que la serialización `nombre=valor` del navegador quede sintácticamente correcta— y suele llevar varios intentos hasta que el servidor lo parsea.

Vale la pena solo si la acción es de impacto alto: en una API el ataque queda a ciegas igual que en el CSRF clásico, así que sirve para escribir, no para leer.

## Huella esperada

La señal es un desajuste que no ocurre en tráfico legítimo: **el mismo endpoint recibiendo un tipo de contenido que su cliente propio nunca manda**. La aplicación de página única siempre manda `application/json`; una petición a ese mismo endpoint con `text/plain` no vino de la aplicación.

Queda en [[Log de acceso del servidor web]] si se registra el tipo de contenido, que no es lo habitual — es una limitación de la fuente, no del método. Donde sí queda completo es en [[Registro del WAF]], que ve el cuerpo, y en [[Log de auditoría de la aplicación]] como acción sin la navegación previa.

Durante la prueba se acumulan `400` y `415` del servidor rechazando tipos de contenido, que es la parte ruidosa y la que aparece en [[Log de errores del servidor web]].
