---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: canal-de-extraccion
implementacion: "Condición booleana convertida en retardo observable de respuesta"
opsec: ruidoso
telemetria: ["[[MySQL - slow query log]]"]
requisitos: [sin-salida-reflejada, sin-error-diferencial]
coste: alto
alternativas: ["[[SQLi - canal fuera de banda]]", "[[SQLi - canal booleano ciego]]"]
probado: 2026-06-02
contexto: [mysql8, mssql2019]
visibilidad: publica
creado: 2026-08-05
aliases:
  - SQLi temporal ciego
  - time-based blind
tags:
  - dominio/web
---

# SQLi - canal temporal ciego

## Cuándo lo elijo

Cuando no hay salida reflejada, los errores están suprimidos y el egress hacia fuera de banda está bloqueado. **Es el último recurso**: cualquier otro canal del árbol de [[MOC - SQL injection]] extrae más rápido y con menos ruido.

También es el canal de confirmación cuando ya se tiene la inyección por otro medio pero se necesita probar ejecución en un contexto que no devuelve nada (por ejemplo, un `INSERT`).

## Por qué funciona

El canal de datos es la **latencia de respuesta**: se convierte una condición booleana en tiempo observable. `IF(condición, SLEEP(5), 0)` no cambia el contenido de la respuesta, cambia cuándo llega. Ver [[La latencia como canal de datos]].

## Cómo falla

- **Jitter de red** — con retardos cortos el ruido de red se confunde con la señal. Obliga a subir el retardo, lo que multiplica el tiempo total.
- **Timeout de WAF o proxy** — corta la conexión antes de que se cumpla el retardo y todas las respuestas se ven iguales.
- **Rate limiting** — el ataque necesita cientos de peticiones; es exactamente el perfil que dispara los límites.
- **Balanceadores y pools de conexión** — un `SLEEP` puede agotar el pool y degradar el servicio: riesgo de DoS accidental, hay que fijar el retardo bajo y la concurrencia en uno.
- **Motores sin primitiva de retardo** — SQLite no tiene `sleep`; hay que simularlo con carga de CPU, que es mucho más ruidoso.

## Coste

Aproximadamente **un bit por petición**. Extraer un hash de 32 caracteres son cientos de peticiones, cada una esperando el retardo completo cuando la condición es verdadera. Con búsqueda binaria por carácter baja a ~7 peticiones por carácter, pero sigue siendo el canal más caro. Por eso siempre se intenta fuera de banda primero.

## Huella esperada

- Ráfaga de peticiones al mismo endpoint con el mismo parámetro variando.
- Distribución de latencias **bimodal** — el sello del canal, y lo que lo hace detectable sin inspeccionar el payload.
- [[MySQL - slow query log]] si `long_query_time` está por debajo del retardo usado.

La sintaxis por motor está en [[Dialectos SQL - matriz de referencia]].
