---
tipo: tradecraft
clase: "[[CWE-78 - OS Command Injection]]"
eje: canal-de-extraccion
implementacion: "El comando ejecuta pero su salida no vuelve; se infiere por efecto lateral observable"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]"]
requisitos: [shell-invocada, sin-salida-reflejada]
coste: medio
alternativas: ["[[Command injection - canal fuera de banda]]", "[[Command injection - canal temporal]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - command injection ciego
  - blind command injection
tags:
  - dominio/web
---

# Command injection - canal ciego

## Cuándo lo elijo

Cuando hay ejecución confirmada pero la salida no aparece en la respuesta. Antes de bajar a este canal hay que agotar dos cosas: redirigir `stderr` a `stdout` —ver [[Command injection - canal directo]]— y probar si hay egress, porque [[Command injection - canal fuera de banda]] extrae mucho más rápido.

Este canal cubre el caso intermedio: **el atacante puede escribir en algún lado que después puede leer**. El patrón que lo hace viable casi siempre es el mismo: la aplicación sirve archivos estáticos desde un directorio conocido, y el comando inyectado escribe ahí.

## Por qué funciona

Se separa la **ejecución** de la **lectura** en dos peticiones distintas. La primera inyecta un comando cuya salida se redirige a un archivo dentro de la raíz web; la segunda pide ese archivo por HTTP como si fuera contenido normal. El canal de datos no es la respuesta a la inyección, es un recurso estático que apareció en el servidor.

La variante sin escritura convierte la respuesta en un oráculo booleano de un bit por petición: una condición que, al cumplirse, produce una diferencia observable —un retardo, un error, un código de estado distinto—. Es más lento y en general solo se usa para confirmar la vulnerabilidad, no para extraer.

## Cómo falla

- **No hay directorio escribible dentro de la raíz web** — lo más común en despliegues correctos. Sin lugar donde dejar el archivo, el canal se cae y hay que volver al temporal o al fuera de banda.
- **La raíz web no es escribible por el usuario del servidor** — separación de privilegios entre quien despliega y quien sirve. Correcta, y suficiente para romper esta técnica.
- **El archivo queda ahí.** Es el problema serio de opsec: un `.txt` con salida de comandos en la raíz web es evidencia persistente que sobrevive al engagement. Hay que borrarlo, y hay que acordarse.
- **Antivirus o monitoreo de integridad** — un archivo nuevo en la raíz web es exactamente lo que vigilan los sistemas de integridad de ficheros.
- **Escritura en directorio no servido** — se escribe bien y no se puede leer. Cuesta una ronda entera descubrirlo.

## Coste

Dos peticiones por comando y un archivo que hay que limpiar. Barato en tiempo, caro en huella: es el canal que más rastro deja en disco.

## Huella esperada

- [[Proceso hijo del servidor web]] ve el comando completo, incluida la redirección al archivo — que es en sí misma un indicador de alta fidelidad.
- Un archivo nuevo en la raíz web con dueño `www-data`, seguido a los segundos de una petición GET a ese mismo archivo. La correlación temporal entre la creación y la primera lectura es la firma, más que cualquiera de los dos eventos por separado.

Los oráculos, la lógica de extracción y las rutas escribibles habituales están en [[Command injection ciego - matriz de referencia]].
