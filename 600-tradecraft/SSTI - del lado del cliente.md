---
tipo: tradecraft
clase: "[[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]]"
eje: capacidad-del-motor
implementacion: "Inyectar en un motor de plantillas que evalúa en el navegador y escapar su entorno restringido"
opsec: ruidoso
telemetria: ["[[Informe de violación de CSP]]", "[[Log de acceso del servidor web]]"]
requisitos: [motor-de-plantillas-en-el-navegador]
coste: medio
alternativas: ["[[XSS - reflejado]]", "[[XSS - DOM-based]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - CSTI
  - client-side template injection
  - AngularJS sandbox
tags:
  - dominio/web
---

# SSTI - del lado del cliente

## Cuándo lo elijo

Cuando `{{7*7}}` devuelve `49` **en el navegador y no en la respuesta del servidor**. La distinción se hace mirando el cuerpo crudo: si viene literal por HTTP y aparece como `49` en el DOM renderizado, el motor corre del lado del cliente y el dominio no es el mismo.

Se llega acá desde una aplicación que usa AngularJS, Vue o cualquier motor que evalúe expresiones en el navegador sobre contenido que vino del servidor sin escapar.

El resultado no es ejecución en el servidor: es **ejecución de JavaScript en el origen**, o sea XSS por otro camino. Por eso las alternativas de esta nota son las notas de XSS y no las otras ramas de SSTI.

## Por qué funciona

Es la razón por la que esta variante merece nota propia en vez de ser una fila en una matriz de XSS: **sobrevive a las defensas que detienen un XSS clásico**.

- **El filtro de etiquetas no la ve.** El payload no lleva `<script>` ni `onerror`: son llaves y nombres de propiedad. Todo sanitizador orientado a HTML lo deja pasar.
- **La política de seguridad de contenido no la detiene**, o no siempre. El código que ejecuta lo invoca el propio motor, que ya está autorizado; si la política permite `unsafe-eval` —que muchas aplicaciones con estos motores necesitan— la ejecución es directa.

Del lado del entorno restringido, el mecanismo es idéntico al de [[SSTI - escape del entorno restringido]]: el motor bloquea nombres y deja acceder a atributos, y desde cualquier objeto se llega al constructor de funciones del lenguaje, que evalúa cadenas arbitrarias. Cambia el lenguaje anfitrión, no el método.

En las versiones de AngularJS posteriores a la 1.6 el entorno restringido se **quitó** —los desarrolladores concluyeron que no era una frontera de seguridad—, así que en esas versiones ni siquiera hay que escapar nada: la expresión ejecuta.

## Cómo falla

Falla cuando la aplicación no tiene un motor de plantillas en el navegador, que es el caso mayoritario en marcos de trabajo modernos: React y Vue con plantillas compiladas no evalúan cadenas en tiempo de ejecución.

Falla contra una política de seguridad de contenido estricta sin `unsafe-eval`, que impide la evaluación dinámica de cadenas. Es la mitigación efectiva y la que va en el informe — junto con la de fondo, que es no insertar contenido no confiable dentro del alcance del motor.

Y falla si el contenido inyectado cae fuera del ámbito que el motor procesa. Es un detalle de ubicación que se comprueba con la prueba aritmética antes de invertir en el escape.

## Coste

Medio. Confirmar el motor y su versión son dos peticiones; el escape depende de la versión y hay cadenas publicadas para cada una, así que es cuestión de elegir la correcta más que de construirla.

Lo que encarece es el diagnóstico inicial: distinguir esta variante de un XSS común y de un SSTI del servidor lleva tres peticiones bien elegidas, y equivocarse manda a probar payloads del dominio incorrecto durante un rato largo.

## Huella esperada

**El servidor no ve nada.** La evaluación ocurre en el navegador de la víctima, así que ninguna fuente del lado del servidor la registra: no hay proceso hijo, no hay excepción de plantilla, no hay conexión saliente desde la aplicación.

La única fuente que la ve es [[Informe de violación de CSP]], y solo si hay política configurada en modo de reporte y el payload la viola. Es la misma limitación que tienen [[XSS - DOM-based]] y [[XSS - mutation XSS]], y por la misma razón: el ataque no cruza el servidor.

Del lado del servidor queda el reflejo de la carga en [[Log de acceso del servidor web]], si viaja por la URL. Si viaja por el cuerpo de un `POST`, tampoco eso — el log de acceso no registra el cuerpo, que es el punto ciego estructural que cubre [[Registro del WAF]].
