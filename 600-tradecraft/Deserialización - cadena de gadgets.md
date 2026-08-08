---
tipo: tradecraft
clase: "[[CWE-502 - Deserialization of Untrusted Data]]"
eje: impacto
implementacion: "Encadenar métodos de bibliotecas cargadas hasta una primitiva de ejecución"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Conexión saliente del servidor de aplicación]]", "[[Log de errores del servidor web]]"]
requisitos: [blob-controlado, biblioteca-con-cadena-conocida]
coste: medio
alternativas: ["[[Deserialización - manipulación de objeto]]"]
probado: 2026-08-08
contexto: [web-generica]
aliases:
  - gadget chain
  - deserialización a RCE
tags:
  - dominio/web
---

# Deserialización - cadena de gadgets

## Cuándo lo elijo

Cuando manipular el objeto no alcanza y el objetivo es ejecución. Es la rama cara del árbol de [[MOC - Deserialización]] y la que le dio fama al dominio, aunque en la práctica [[Deserialización - manipulación de objeto]] resuelve más casos.

El dato que decide si es viable no está en la aplicación: está en **sus dependencias**. Hay cadena si alguna biblioteca cargada tiene una publicada; si no, hay que construirla, que es trabajo de días y a veces imposible.

Python es la excepción que conviene tener presente: `pickle` ejecuta código arbitrario por diseño del formato, sin necesidad de gadget alguno. Ahí la pregunta no es si hay cadena sino si el blob llega al deserializador.

## Por qué funciona

Porque deserializar no es leer: **reconstruir un objeto ejecuta código de la propia aplicación** — constructores, destructores, ganchos del ciclo de vida, métodos de comparación. El atacante no aporta código; aporta un **estado** que hace que ese código, invocado en el orden correcto, termine en una primitiva peligrosa.

De ahí la fragilidad característica del dominio: la explotabilidad depende de qué bibliotecas están cargadas y en qué versión. Una aplicación puede ser explotable hoy y no mañana **sin que su código cambie**, porque una dependencia agregó o quitó una clase. Es la razón por la que este tradecraft caduca más rápido que casi cualquier otro del vault.

## Cómo falla

- **Lista blanca de clases permitidas** al deserializar. La mitigación real dentro del formato, y cierra la rama entera.
- **No hay cadena para las bibliotecas presentes.** El caso más común, y no siempre es evidente: hay que enumerar dependencias y versiones primero.
- **La cadena existe pero la versión está parcheada.** Las bibliotecas grandes rompen sus propias cadenas de forma rutinaria, a veces sin anunciarlo como arreglo de seguridad.
- **El blob va firmado** — ver [[Deserialización - firma débil]].
- **El gadget necesita salida de red y no hay** — muchas cadenas de Java terminan en una búsqueda remota de clase, que sin egress no completa.
- **Rompe la aplicación.** Una cadena a medio ejecutar puede dejar el proceso en estado inconsistente o tirar el trabajador. No es teórico: pasa seguido.

## Coste

Medio si hay cadena publicada y herramienta que la genere: minutos. Alto si hay que adaptarla, y prohibitivo si hay que construirla desde cero.

El grueso del trabajo es **enumerar dependencias**, que es reconocimiento: mensajes de error, archivos de bloqueo expuestos, rutas de recursos estáticos, cabeceras del marco de trabajo.

## Un límite operativo

> [!danger] Las cadenas rompen procesos
> Una cadena de gadgets manipula el estado interno del proceso para conseguir la ejecución, y muchas dejan el trabajador inutilizable o disparan excepciones que la aplicación no maneja. En un servidor con pocos trabajadores eso es degradación visible del servicio.
>
> Se prueba primero la variante más inocua de la cadena —una que solo genere una petición saliente o un retardo— para confirmar la ejecución antes de lanzar la que ejecuta comandos. Confirmar y ejecutar son dos pasos, y conviene no juntarlos.

## Huella esperada

Es la variante más ruidosa del dominio, al revés que su hermana.

- [[Proceso hijo del servidor web]] cuando el gadget final ejecuta un comando, que es lo habitual. Ahí [[Intérprete de comandos como hijo del servidor web]] la detecta sin saber que hubo deserialización de por medio — otra vez la detección de efecto cubriendo una técnica que no conoce.
- [[Conexión saliente del servidor de aplicación]] si la cadena hace una búsqueda remota de clase o resuelve un nombre. En Java es frecuentísimo y suele ser lo primero que sale.
- [[Log de errores del servidor web]] con excepciones de deserialización de las cadenas que fallaron. **Los intentos fallidos son más visibles que el exitoso**, y suelen preceder al que funciona: una ráfaga de excepciones de deserialización es reconocimiento en curso.

Las cadenas por lenguaje y biblioteca están en [[Deserialización gadgets - matriz de referencia]].
