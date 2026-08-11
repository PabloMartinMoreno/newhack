---
tipo: tradecraft
clase: "[[CWE-78 - OS Command Injection]]"
eje: canal-de-extraccion
implementacion: "La salida del comando inyectado vuelve dentro de la respuesta HTTP"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Log de acceso del servidor web]]", "[[Registro del WAF]]"]
requisitos: [shell-invocada, salida-reflejada]
coste: bajo
alternativas: ["[[Command injection - canal ciego]]", "[[Command injection - canal fuera de banda]]"]
probado: nunca
contexto: [php8-linux]
aliases:
  - command injection directo
  - in-band command injection
tags:
  - dominio/web
---

# Command injection - canal directo

## Cuándo lo elijo

Siempre primero, si existe. Es el caso feliz del árbol de [[MOC - Command injection]]: la app muestra la salida del comando que ejecuta —un `ping`, un `nslookup`, un `whois`, una conversión de imagen que reporta errores— y esa salida se convierte en el canal de lectura.

La señal de que existe es que la respuesta contiene texto que la aplicación evidentemente no escribió: la salida cruda de una herramienta de sistema.

Si la salida no vuelve, el árbol baja a [[Command injection - canal ciego]]; si además no hay respuesta diferencial, a [[Command injection - canal temporal]].

## Por qué funciona

El shell ya está devolviendo `stdout` a la aplicación, que lo imprime. Al encadenar un segundo comando con un separador, su salida se suma a la misma corriente y sale por el mismo lugar. No hay que construir ningún canal: se reusa el que la app abrió sola.

Vale un matiz que cambia la técnica más de lo que parece: **muchas apps imprimen `stdout` y descartan `stderr`**. Un comando que falla parece no haber corrido. Redirigir el error a la salida estándar convierte medio dominio de "ciego" en "directo", y es lo primero que se prueba antes de aceptar que el canal no existe.

## Cómo falla

- **La app captura la salida pero no la imprime** — la ejecuta para conocer el código de retorno. Hay ejecución y no hay canal: es ciego, no inmune.
- **Solo se imprime `stderr`, o solo `stdout`** — la mitad de los comandos parecen no ejecutarse. Se resuelve redirigiendo, no cambiando de canal.
- **La salida se parsea antes de mostrarse** — si la app extrae con una expresión regular solo la latencia del `ping`, todo lo demás se descarta en el camino.
- **Longitud truncada** — el campo de salida tiene un límite y los volcados largos se cortan sin aviso. Obliga a paginar.
- **Sin shell** — si la app usa `execve` con array, los separadores son texto literal. El dominio colapsa a [[Argument injection - abuso de flags]].

## Coste

El más bajo de los cuatro canales: una petición por comando, salida completa. Es el único que permite trabajar de forma interactiva sin montar infraestructura.

## Huella esperada

- [[Proceso hijo del servidor web]] es lo que lo delata: `www-data` como padre de `/bin/sh`, y de ahí a lo que se haya inyectado. Es una relación padre-hijo que en operación normal casi no ocurre.
- [[Log de acceso del servidor web]] tiene el payload entero **solo si viajó por GET**. Por POST no queda nada en el log de acceso, y ese es exactamente el punto ciego que hace obligatoria la telemetría de proceso.

Los separadores y la sintaxis de redirección por shell están en [[Command injection shells - matriz de referencia]]; cómo romper según dónde cae el input, en [[Command injection contextos - matriz de referencia]].
