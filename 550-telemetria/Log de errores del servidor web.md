---
tipo: telemetria
plataforma: [linux, windows]
producto: nginx / Apache / PHP / el framework de la aplicación
identificador: "error.log"
por-defecto: true
coste: bajo
aliases:
  - error.log
  - log de errores de la aplicación
  - stack traces
tags:
  - dominio/web
---

# Log de errores del servidor web

## Qué lo genera

Toda excepción no controlada, error del intérprete y fallo del servidor. Está activado por defecto casi siempre, y casi siempre nadie lo mira.

Es el par complementario de [[Log de acceso del servidor web]]: aquel registra qué se pidió, este registra **qué se rompió al procesarlo**. Para todo el tramo de descubrimiento de una vulnerabilidad —donde el atacante todavía está probando y la mayoría de los intentos fallan— este archivo tiene mucha más señal que el de acceso.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Mensaje de excepción | Qué falló y por qué | En XXE por error, **contiene el archivo leído** |
| Traza de pila | Dónde falló | Identifica el parser y la biblioteca vulnerable |
| Ruta y parámetro | Qué petición lo causó | Correlación con [[Log de acceso del servidor web]] |
| Frecuencia | Ráfagas | Muchos errores del mismo tipo en poco tiempo es reconocimiento |
| Nombre de archivo citado | Rutas que se intentaron abrir | `/etc/passwd` en un mensaje de error no necesita más análisis |

## Coste de recolección

Bajo. Un servidor sano genera pocos errores, así que el volumen es una fracción del log de acceso y se conserva mucho tiempo barato. Su problema no es el coste: es que **el aumento de volumen es la señal**, y sin línea base no se nota.

## Cómo se activa

Ya está. Lo que casi nunca está es enviado al SIEM, y lo que suele estar mal es el nivel: en producción se baja para no llenar el disco y con eso se pierde exactamente lo que sirve.

Cuidado con la contracara: los errores detallados son útiles para el defensor **y** son un canal de extracción para el atacante — ver [[SQLi - canal basado en errores]] y [[XXE - canal por error]]. Lo correcto es registrarlos completos en el servidor y no devolverlos nunca al cliente.

## Limitaciones

- **No ve lo que funciona.** Un ataque exitoso y limpio no genera errores. Esta fuente detecta el camino, no la llegada.
- **Ruido de fondo por errores crónicos.** Aplicaciones con excepciones permanentes por bugs conocidos entierran la señal.
- **Formato heterogéneo.** Cada framework escribe distinto y el parseo es específico de cada aplicación: es la fuente que peor se normaliza.
- **Rotación agresiva.** Configuraciones que rotan por tamaño pueden perder horas de registro justo durante un ataque, que es cuando más se escribe.

## Quién lo emite / quién lo consume

Rojo: [[XXE - canal por error]] · [[SQLi - canal basado en errores]] · [[SSRF - canal ciego]] · [[Path traversal]] · [[File upload - bypass de validación]]
Azul: [[Ráfaga de errores del servidor desde un mismo origen]]
