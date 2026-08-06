---
tipo: moc
dominio: web
visibilidad: publica
creado: 2026-08-05
aliases:
  - MOC SQLi
  - SQL injection
tags:
  - dominio/web
---

# MOC - SQL injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-89 - SQL Injection]]. La sintaxis por motor vive en [[Dialectos SQL - matriz de referencia]]. Acá vive **la decisión**.

SQLi no es una técnica: es la intersección de cinco ejes ortogonales. Una nota por **valor de eje**, nunca por combinación — el producto cartesiano son cientos de casos y ~25 notas los cubren.

| Eje | Valores |
|---|---|
| Canal de extracción | UNION · error · booleano ciego · temporal ciego · fuera de banda |
| Contexto de inyección | string · numérico · `ORDER BY` · `LIMIT` · `INSERT` · segundo orden |
| Motor | MySQL · MSSQL · PostgreSQL · Oracle · SQLite |
| Obstáculo | WAF · comillas filtradas · espacios filtrados · palabras clave bloqueadas |
| Impacto | lectura de archivos · escritura · RCE · movimiento a otra base |

## Árbol de decisión — elegir canal

```
¿Los datos vuelven en la respuesta?
├─ Sí, directamente        → [[SQLi - canal UNION]]
├─ Sí, dentro de un error  → [[SQLi - canal basado en errores]]
└─ No
   ├─ ¿Hay egress de red?  → [[SQLi - canal fuera de banda]]
   └─ No
      ├─ ¿Respuesta diferencial? → [[SQLi - canal booleano ciego]]
      └─ No                      → [[SQLi - canal temporal ciego]]
```

El orden no es arbitrario: es el orden de **coste creciente**. El temporal ciego extrae aproximadamente un bit por petición; por eso siempre se intenta fuera de banda primero.

## Árbol de decisión — obstáculos

```
¿Qué te está bloqueando?
├─ Comillas filtradas/escapadas → [[SQLi - evasión sin comillas]]
├─ Espacios filtrados           → [[SQLi - evasión sin espacios]]
├─ Palabras clave bloqueadas    → [[SQLi - evasión de palabras clave]]
└─ WAF con firma                → [[SQLi - evasión de WAF]]
```

## Orden de aprendizaje

Secuencia por dependencia conceptual. Este es el temario del módulo.

1. [[CWE-89 - SQL Injection]] — qué es y por qué existe
2. [[SQLi - contexto numérico]] y contexto string — dónde cae la inyección
3. [[SQLi - canal UNION]] — el caso feliz, fija el modelo mental
4. [[SQLi - canal basado en errores]]
5. [[La latencia como canal de datos]] — el concepto antes de la técnica
6. [[SQLi - canal booleano ciego]] → [[SQLi - canal temporal ciego]]
7. [[SQLi - canal fuera de banda]]
8. [[SQLi - inyección de segundo orden]] — rompe la intuición de "entrada = salida"
9. Evasiones
10. Impacto: [[SQLi - lectura de archivos en MySQL]], [[SQLi - stacked queries en MSSQL]]

## Cara azul

Qué emite cada canal y qué lo ve: [[MySQL - slow query log]], logs de aplicación, anomalía de latencia en WAF, resolución DNS saliente desde el servidor de base de datos.

## Huecos conocidos

- [ ] Contexto `ORDER BY` y `LIMIT`
- [ ] Segundo orden
- [ ] Evasión de WAF (¿nota por producto o nota por primitiva? — por primitiva)
- [ ] Mapear cada canal a su nota de telemetría en `550-telemetria/`
