---
tipo: tradecraft
clase: "[[CWE-88 - Argument Injection]]"
eje: ruptura-del-contexto
implementacion: "Sin escapar del argumento: se inyectan flags que cambian el comportamiento del binario"
opsec: limpio
telemetria: ["[[Proceso hijo del servidor web]]"]
requisitos: [argumento-controlado, binario-con-flags-abusables]
coste: medio
alternativas: ["[[Command injection - canal directo]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - abuso de flags
  - inyección de flags
tags:
  - dominio/web
---

# Argument injection - abuso de flags

## Cuándo lo elijo

Cuando la inyección de comandos está cerrada pero el argumento sigue siendo mío. Concretamente: los metacaracteres de shell viajan como texto literal —porque la app usa `execve` con array o comilla cada parámetro— y sin embargo el contenido del argumento llega intacto al binario.

Es el nodo raíz del árbol de [[MOC - Command injection]] respondido por "no": **no hay shell, y aun así hay superficie**. La pregunta deja de ser "cómo escapo" y pasa a ser "qué sabe hacer este binario que yo pueda pedirle".

También es la respuesta cuando una app fue "arreglada" contra [[CWE-78 - OS Command Injection]] y se dio por segura. El parche correcto para esa CWE no toca esta.

## Por qué funciona

Un binario de línea de comandos no distingue quién escribió cada argumento: procesa toda la lista igual. Si el atacante controla un elemento y ese elemento empieza con `-`, el parser lo lee como opción, no como dato. El comando resultante es sintácticamente perfecto y hace algo distinto de lo que la aplicación quiso.

Lo que convierte esto en impacto real es que muchas herramientas comunes tienen flags que escriben archivos, ejecutan programas o leen rutas arbitrarias — capacidades legítimas y documentadas que en este contexto son primitivas de explotación.

Las tres formas concretas —flag inyectada, separación por espacios, valor con semántica especial— están en [[CWE-88 - Argument Injection]]; los binarios y sus flags, en [[Argument injection - matriz de referencia]].

## Cómo falla

- **El binario recibe `--` antes del argumento controlado** — cierra la lista de opciones y todo lo posterior se lee como dato. Es la mitigación correcta y la mata por completo.
- **El argumento no va en primera posición** — muchos binarios solo aceptan opciones antes de los operandos; si el input va al final, ya no se parsea como flag.
- **La app valida que el argumento no empiece con `-`** — barato de implementar y suficiente para la forma más común.
- **El binario no tiene nada abusable** — no toda herramienta tiene una flag que escriba archivos o ejecute algo. A veces hay inyección y el techo es leer un fichero.
- **El input se usa como parte de un argumento, no como argumento completo** — si va concatenado detrás de un prefijo (`--file=/ruta/<input>`), no puede empezar con `-`, y hay que buscar semántica especial en el valor en vez de una flag.

## Coste

Alto en reconocimiento, bajo en ejecución. Cuesta descubrir qué binario corre por detrás y en qué posición cae el argumento —muchas veces se deduce por mensajes de error o por el comportamiento de la app—, pero una vez identificado el binario, la flag correcta es una consulta a una tabla.

## Huella esperada

Es la variante **más limpia** del dominio, y esa es su ventaja principal. La cadena de procesos es la legítima: el servidor web invoca exactamente el binario que siempre invoca, sin shell de por medio. Nada en el árbol de procesos se ve raro.

- [[Proceso hijo del servidor web]] registra el evento, pero solo la **línea de comandos** delata algo: una flag que la aplicación nunca pasa. Detectarlo exige conocer la invocación normal y comparar contra ella, no buscar anomalías genéricas.
- Si la flag abusada escribe un archivo, ese archivo es la evidencia más fuerte que queda — y suele ser la única.

Por eso este es el punto ciego declarado de [[Proceso hijo del servidor web]]: la telemetría lo captura y la detección genérica no lo ve.
