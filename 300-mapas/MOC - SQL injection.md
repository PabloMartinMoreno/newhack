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

Las primitivas se combinan; todas viven en [[SQLi evasión - matriz de referencia]], una sección por obstáculo.

```
¿Qué te está bloqueando?
├─ Comillas filtradas/escapadas → hex / char()          → § Sin comillas
├─ Espacios filtrados           → comentarios / %09 %0a → § Sin espacios
├─ Palabras clave bloqueadas    → case / anidado / /*! */→ § Palabras clave
└─ WAF con firma                → doble encode / versión → § Evasión de WAF
```

## Cheatsheets — entrada directa a los payloads

Cuando ya sabés qué hacer y solo querés la sintaxis, sin pasar por las notas de criterio:

| Matriz | Cubre |
|---|---|
| [[SQLi UNION - matriz de referencia]] | Confirmar inyección, cierre, columnas, enumerar, extraer, archivos — paso a paso |
| [[SQLi error-based - matriz de referencia]] | Primitivas de error por motor, enumerar, truncamiento |
| [[SQLi ciego - matriz de referencia]] | Booleano y temporal: oráculo, extracción por carácter, binaria |
| [[SQLi fuera de banda - matriz de referencia]] | Primitiva de red por motor, exfil por DNS, herramientas |
| [[SQLi evasión - matriz de referencia]] | Sin comillas / sin espacios / palabras clave / WAF |
| [[SQLi impacto - matriz de referencia]] | Lectura y escritura de archivos, stacked queries → RCE |
| [[SQLi contextos - matriz de referencia]] | Cómo romper según dónde cae el input: numérico, string, `ORDER BY`, `LIMIT`, `INSERT` |
| [[Dialectos SQL - matriz de referencia]] | Diferencias de sintaxis entre los 5 motores |

## Orden de aprendizaje

Secuencia por dependencia conceptual. Este es el temario del módulo.

1. [[CWE-89 - SQL Injection]] — qué es y por qué existe
2. [[SQLi contextos - matriz de referencia]] — dónde cae la inyección y cómo romper
3. [[SQLi - canal UNION]] — el caso feliz, fija el modelo mental
4. [[SQLi - canal basado en errores]]
5. [[La latencia como canal de datos]] — el concepto antes de la técnica
6. [[SQLi - canal booleano ciego]] → [[SQLi - canal temporal ciego]]
7. [[SQLi - canal fuera de banda]]
8. [[SQLi - inyección de segundo orden]] — rompe la intuición de "entrada = salida"
9. Evasiones
10. Impacto: [[SQLi - lectura de archivos en MySQL]], [[SQLi - stacked queries en MSSQL]]

## Cara azul

Qué emite cada canal y qué lo ve:

| Canal | Telemetría | Firma |
|---|---|---|
| UNION / error-based | [[Log de acceso del servidor web]] | `UNION SELECT` / `extractvalue` en la URL; ráfaga de `500` en error-based |
| Booleano ciego | [[Log de acceso del servidor web]] | Payloads casi idénticos que solo cambian un carácter; dos tamaños de respuesta |
| Temporal ciego | [[MySQL - slow query log]] | Distribución de latencias bimodal |
| Fuera de banda | [[Consulta DNS saliente]] | Resolución externa desde la IP del servidor de BD |

## Huecos conocidos

- [x] Los cinco canales de extracción — completos
- [x] Evasiones — en [[SQLi evasión - matriz de referencia]]
- [x] Impacto — [[SQLi - lectura de archivos en MySQL]] y [[SQLi - stacked queries en MSSQL]]
- [x] Contexto de inyección — [[SQLi contextos - matriz de referencia]]
- [x] Segundo orden — [[SQLi - inyección de segundo orden]]
