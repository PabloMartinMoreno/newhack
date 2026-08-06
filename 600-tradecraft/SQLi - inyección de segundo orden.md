---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: contexto-de-inyeccion
implementacion: "Input guardado que se ejecuta en una consulta posterior distinta"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [input-persistido, reuso-inseguro-del-dato]
coste: medio
alternativas: []
probado: 2026-08-06
contexto: [mysql8]
visibilidad: publica
creado: 2026-08-06
aliases:
  - SQLi segundo orden
  - second-order SQLi
tags:
  - dominio/web
---

# SQLi - inyección de segundo orden

## Cuándo lo elijo

Cuando la inyección directa no aparece por ningún canal, pero la app **guarda** mi input y después lo **reutiliza** en otra consulta. No es un canal ni un obstáculo: es una condición del flujo de datos que hace que el punto de inyección y el punto de ejecución sean **peticiones distintas**.

La señal para sospecharlo: un campo que se guarda (nombre de usuario, alias, dirección) y que reaparece en otra parte de la app (un perfil, un panel de admin, un log). El payload viaja limpio en la escritura y detona en la lectura.

## Por qué funciona

La primera consulta —la que recibe mi input— suele estar parametrizada, así que **guarda el string tal cual, sin ejecutarlo**. Una segunda funcionalidad lee ese valor de la base y lo concatena en una consulta nueva sin escapar. El desarrollador "confía" en el dato porque ya está en la base, y esa confianza es el bug.

```
1. Registro: usuario = admin'-- 
   INSERT INTO users(name) VALUES (?)      ← parametrizado, guarda "admin'-- " intacto

2. Cambiar contraseña (otra request, otra query):
   UPDATE users SET pass='nueva' WHERE name='admin'-- '   ← concatenado, EXPLOTA acá
```

## Cómo falla

- **El dato nunca se reutiliza en SQL** — si solo se muestra en HTML, será XSS almacenado, no SQLi.
- **La segunda consulta también está parametrizada** — no hay reuso inseguro, no hay bug.
- **Difícil de confirmar a ciegas** — como detona en otra función, hay que mapear qué feature lee el dato. Es trabajo de correlación, no de un solo request.
- **El input se sanitiza al guardar** (no solo al usar) — el payload llega ya roto a la base.

## Coste

Medio, pero el costo real es de **descubrimiento**, no de explotación. Encontrarlo requiere entender el flujo: qué campos se persisten y dónde se releen. Una vez identificado el par escritura→lectura, la explotación es SQLi común en el punto de ejecución.

## Huella esperada

- El payload aparece en el [[Log de acceso del servidor web]] en una petición **benigna** (el registro), y el error o el efecto ocurre en **otra** petición posterior. La correlación entre ambas es lo que delata el ataque — y lo que lo hace difícil de detectar del lado azul, porque ningún request individual se ve malicioso.

Sintaxis de breakout según dónde detone: [[SQLi UNION - matriz de referencia]] y [[Dialectos SQL - matriz de referencia]].
