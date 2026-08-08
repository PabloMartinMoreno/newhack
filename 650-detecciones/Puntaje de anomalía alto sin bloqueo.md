---
tipo: deteccion
tecnicas: ["[[CWE-89 - SQL Injection]]", "[[CWE-78 - OS Command Injection]]", "[[CWE-79 - Cross-site Scripting]]"]
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]"]
forma: agregado
ventana: "30m"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - WAF en modo detección
  - payload que pasó el WAF
tags:
  - dominio/web
---

# Puntaje de anomalía alto sin bloqueo

## Qué detecta

Peticiones que acumulan coincidencias de reglas del WAF **sin llegar a ser bloqueadas**, agrupadas por origen y por sesión.

El interés no está en lo que el WAF bloqueó — eso ya se detuvo y es ruido de fondo de internet. Está en lo que **coincidió parcialmente y pasó**: un puntaje alto sin bloqueo significa que algo se parecía mucho a un ataque y llegó igual a la aplicación.

Cubre además el punto ciego estructural del lado web: [[Log de acceso del servidor web]] **no registra el cuerpo**, así que todo payload por POST es invisible ahí. El WAF sí lo inspecciona, y es la única fuente que cubre eso sin instrumentar la aplicación.

## Lógica

```
waf
| where timestamp > ago(30m)
| summarize
    puntaje = sum(anomaly_score),
    reglas = dcount(rule_id),
    bloqueadas = countif(action == 'block'),
    pasaron = countif(action == 'detect'),
    rutas = dcount(uri_path)
  by client_ip, session_id
| where pasaron > 0 and puntaje > umbral and reglas > 3
| where rutas <= 3
```

La última condición es la que separa un atacante de un escáner: **el escaneo de fondo de internet toca muchas rutas una vez cada una**; alguien probando una inyección toca **una ruta muchas veces** con el payload variando. Agrupar por ruta invierte la señal y saca casi todo el ruido.

Refuerzo de mayor valor todavía, y es una consulta de caza más que una alerta: correlacionar un puntaje alto que pasó con **cualquier detección de efecto disparada después** desde la misma IP — [[Intérprete de comandos como hijo del servidor web]], [[Archivo ejecutable nuevo en la raíz web]], [[Petición al servicio de metadatos de instancia]]. Eso reconstruye la cadena desde el intento hasta el impacto.

> [!warning] `detect` y `block` significan cosas opuestas
> Un WAF en modo de solo detección produce exactamente los mismos registros que uno que bloquea. Si el triaje no distingue el campo de acción, se leen como ataques frustrados cosas que llegaron enteras a la aplicación. Es el error de lectura más común sobre esta fuente.

## Falsos positivos conocidos

- **Aplicaciones con texto libre** — foros, gestores de incidencias, documentación técnica, buscadores. Hablar de `UNION SELECT` es su contenido legítimo y disparan reglas todo el día.
- **Escáneres autorizados** y monitoreo, que generan puntajes altísimos por diseño.
- **Escaneo de fondo de internet**: permanente en cualquier servidor público. El filtro de cardinalidad de rutas lo saca casi entero.
- **Clientes que envían contenido rico** — HTML, marcado, JSON anidado.

El umbral de puntaje no es transferible entre aplicaciones. Hay que derivarlo de la línea base propia.

## Evasiones conocidas

Todas. Esta es una fuente de firmas y hereda todos sus límites: [[SQLi evasión - matriz de referencia]], [[XSS evasión - matriz de referencia]] y [[Command injection evasión - matriz de referencia]] existen precisamente para no coincidir con ninguna regla y no generar puntaje.

Además:

- **Saltarse el WAF** yendo directo al origen, si es alcanzable.
- **Técnicas que no son ataques reconocibles** — [[Control de acceso - IDOR]], [[Autenticación - credential stuffing]] y [[Sesión - robo de token]] son peticiones perfectamente normales. Ninguna regla las toca.
- **Repartir el payload** entre varias peticiones para que ninguna acumule puntaje.

> [!important] Silencio no es seguridad
> Un WAF sin eventos tranquiliza y no prueba nada. Es el riesgo principal de esta fuente, y la razón por la que en este vault es **contexto y cuerpo de petición**, no detección primaria.

## Cómo se prueba

Disparadores: [[SQLi - canal UNION]] y [[Command injection - canal directo]] sin evasión contra un laboratorio con WAF en modo detección.

Forma `agregado`: necesita volumen y línea base. Probar además con las evasiones de las matrices, para medir cuánto de lo que hay que detectar pasa sin puntaje — ese número es más informativo que la regla misma.
