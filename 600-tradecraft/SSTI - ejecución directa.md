---
tipo: tradecraft
clase: "[[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]]"
eje: capacidad-del-motor
implementacion: "Usar la construcción documentada del motor que invoca al sistema operativo"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Log de errores del servidor web]]"]
requisitos: [motor-sin-entorno-restringido]
coste: bajo
alternativas: ["[[SSTI - escape del entorno restringido]]", "[[SSTI - lectura sin ejecución]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - SSTI a RCE
tags:
  - dominio/web
---

# SSTI - ejecución directa

## Cuándo lo elijo

Cuando [[SSTI - matriz de identificación]] dio un motor que expone ejecución sin entorno restringido: Freemarker, Velocity, Smarty, ERB, Pug, Jinja2 con acceso a `os`, o Twig con las extensiones peligrosas cargadas.

Es la rama más corta del dominio: hay una construcción documentada, se pega y devuelve la salida del comando. No hay cadena que armar ni grafo que trepar.

Si el motor está restringido —Jinja2 estándar, Twig sin extensiones— la rama es [[SSTI - escape del entorno restringido]]. Si el motor es sin lógica, no hay ejecución posible y va [[SSTI - lectura sin ejecución]].

## Por qué funciona

Estos motores exponen el lenguaje anfitrión a propósito, porque su público objetivo es el desarrollador de la aplicación, no el usuario final. Freemarker documenta una clase para ejecutar comandos; Velocity permite instanciar clases arbitrarias; ERB es Ruby completo entre delimitadores.

Nada de esto es un fallo del motor. **El fallo es que la plantilla la escriba el atacante**, y una vez que eso pasa, el motor hace exactamente lo que promete.

De ahí una consecuencia útil: no hay evasión que valga la pena inventar. El payload es el que está en la documentación del motor, y si no funciona, casi siempre es porque el motor no es el que se pensaba — se vuelve a identificar en vez de insistir.

## Cómo falla

Falla cuando el motor sí tiene entorno restringido y la identificación fue optimista. Es el error más frecuente: los delimitadores `{{ }}` los usan varios motores, y confundir Jinja2 con Twig lleva a probar payloads que no van a funcionar nunca.

Falla cuando el proceso corre con privilegios mínimos y sin shell disponible en el contenedor. Ahí la ejecución existe pero no rinde: conviene pasar a lectura de archivos y de variables de entorno, que en un contenedor suele traer credenciales.

Y falla parcialmente cuando el resultado no se refleja: si la plantilla se renderiza en un proceso asíncrono —un correo, un informe, una notificación— la ejecución ocurre y no se ve. Ese caso se resuelve por canal fuera de banda, igual que en [[Command injection - canal fuera de banda]], y está en la matriz.

## Coste

Bajo. Confirmada la inyección y el motor, son dos peticiones: una para probar la ejecución y otra para el objetivo real.

El coste está antes, en identificar. Ahí conviene ser sistemático en vez de tirar payloads: el árbol de [[SSTI - matriz de identificación]] resuelve el motor en cuatro peticiones y evita las veinte que se gastan probando payloads de motores equivocados.

## Huella esperada

Es la rama más visible del vault, y por una razón que conviene entender: **la ejecución nace un proceso hijo del servidor web**, que es la relación en la que ancla [[Intérprete de comandos como hijo del servidor web]]. Esa detección no sabe que hubo SSTI de por medio y no le hace falta — ve el efecto compartido con command injection, deserialización y webshells.

Antes de eso queda el reconocimiento, y es abundante: los payloads de motores equivocados lanzan excepciones del motor, que caen en [[Log de errores del servidor web]] con el nombre de la plantilla y a veces la traza entera. Una ráfaga de excepciones de plantilla desde un mismo origen es reconocimiento de SSTI en curso, y precede al intento que funciona.

Es la misma asimetría que en [[MOC - Deserialización]]: lo fallido es más visible que lo exitoso.
