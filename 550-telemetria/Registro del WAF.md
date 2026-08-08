---
tipo: telemetria
plataforma: [linux, windows]
producto: ModSecurity / AWS WAF / Cloudflare / Azure Front Door
identificador: "evento de regla"
por-defecto: false
coste: alto
aliases:
  - WAF log
  - eventos de WAF
tags:
  - dominio/web
---

# Registro del WAF

## Qué lo genera

Cada petición que coincide con una regla del cortafuegos de aplicación, bloqueada o solo registrada.

Su valor propio no es detectar ataques —para eso están las detecciones de efecto— sino **ver lo que ninguna otra fuente web ve: el cuerpo de la petición**. [[Log de acceso del servidor web]] no registra el cuerpo, así que todo payload enviado por POST es invisible ahí. El WAF sí lo inspecciona, y eso lo vuelve la única fuente que cubre ese punto ciego sin instrumentar la aplicación.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Regla disparada | Qué firma coincidió | Clasifica el intento por familia |
| Acción | `block` o `detect` | **Si es `detect`, el payload llegó a la aplicación** |
| Cuerpo o fragmento | El payload | Lo único que ve el cuerpo del POST |
| Puntaje de anomalía | Suma de coincidencias | Un puntaje alto sin bloqueo es lo que hay que mirar |
| Origen y sesión | Quién | Correlación con el resto |
| Ruta | Dónde | Identifica el endpoint atacado |

La fila de la acción es la que más se pasa por alto en el triaje: un WAF en modo de solo detección produce el mismo registro que uno que bloquea, y significan cosas opuestas.

## Coste de recolección

Alto. Todo servidor público recibe escaneo de fondo permanente, así que el volumen es enorme y casi todo es irrelevante. Se domina agrupando por origen y por sesión en vez de alertar por evento, que es la razón por la que las reglas que lo consumen son de forma `agregado`.

## Cómo se activa

Ya está donde hay WAF; lo que falta casi siempre es **enviarlo al SIEM** y conservar el cuerpo, que muchos despliegues truncan o desactivan por volumen y por privacidad.

## Limitaciones

- **Es una fuente de firmas**, y hereda todos los límites de las firmas: cualquier evasión de [[SQLi evasión - matriz de referencia]], [[XSS evasión - matriz de referencia]] o [[Command injection evasión - matriz de referencia]] la esquiva.
- **No ve tráfico que no pasa por él** — peticiones directas al origen saltándose el WAF, o tráfico interno.
- **No ve lo que no es un ataque conocido.** [[Control de acceso - IDOR]], [[Autenticación - credential stuffing]] y [[Sesión - robo de token]] son peticiones perfectamente normales: ninguna regla las toca.
- **Ausencia de eventos no es ausencia de ataque**, y esa confusión es el riesgo principal de esta fuente: un WAF silencioso tranquiliza y no prueba nada.
- **Falsos positivos permanentes** en aplicaciones que manejan texto libre.

Por eso vale como fuente de contexto y de cuerpo de petición, y no como fuente primaria de detección.

## Quién lo emite / quién lo consume

Rojo: [[SQLi - canal UNION]] · [[SQLi - canal basado en errores]] · [[XSS - reflejado]] · [[XSS - almacenado]] · [[Command injection - canal directo]] · [[Path traversal]] · [[LFI - inclusión local]] · [[XXE - canal directo]] · [[File upload - bypass de validación]]
Azul: [[Puntaje de anomalía alto sin bloqueo]]
