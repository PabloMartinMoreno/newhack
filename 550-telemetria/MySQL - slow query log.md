---
tipo: telemetria
plataforma: [linux, windows]
producto: MySQL
identificador: "slow_query_log"
por-defecto: false
coste: bajo
aliases:
  - slow_query_log
  - Registro de consultas lentas de MySQL
tags:
  - dominio/web
---

# MySQL - slow query log

## Qué lo genera

Toda consulta cuyo tiempo de ejecución supera `long_query_time` (10 segundos por defecto). Registra la consulta completa, el tiempo, las filas examinadas y el usuario.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Query_time` | Duración | El propio canal del ataque temporal ciego |
| `SQL text` | Consulta literal | Se ve el `SLEEP()` / `BENCHMARK()` inyectado |
| `User@Host` | Cuenta de aplicación y origen | Correlacionar con el frontend |
| `Rows_examined` | Filas leídas | Distingue lentitud por carga de lentitud por retardo artificial |

## Coste de recolección

Bajo si `long_query_time` está bien calibrado. Si se baja a un valor pequeño para atrapar retardos cortos, el volumen se dispara y la latencia de escritura afecta al motor.

## Cómo se activa

`slow_query_log = 1` + `slow_query_log_file`. Está desactivado por defecto y casi nunca se envía al SIEM: es la fuente que existe pero nadie recolecta.

## Limitaciones

- Un atacante que use retardos de 2 segundos queda por debajo del umbral por defecto y no aparece nunca.
- No ve el canal booleano ciego ni el fuera de banda: esos no generan lentitud.
- Es log de motor, no de aplicación: no trae el parámetro HTTP de origen.

## Quién lo emite / quién lo consume

Rojo: [[SQLi - canal temporal ciego]]
Azul: pendiente — ver [[Consultas del vault]] § Huecos defensivos propios
