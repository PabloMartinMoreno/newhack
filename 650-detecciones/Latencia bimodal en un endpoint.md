---
tipo: deteccion
tecnicas: ["[[CWE-89 - SQL Injection]]", "[[CWE-78 - OS Command Injection]]"]
telemetria: ["[[Log de acceso del servidor web]]", "[[MySQL - slow query log]]"]
forma: agregado
ventana: "15m"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - distribución bimodal de respuesta
tags:
  - dominio/web
---

# Latencia bimodal en un endpoint

## Qué detecta

Un endpoint cuyas respuestas se agrupan en **dos picos de latencia claramente separados** dentro de una ventana, con el pico lento en un valor redondo de segundos.

Es la firma de todos los canales temporales del vault —[[SQLi - canal temporal ciego]] y [[Command injection - canal temporal]]— y tiene una propiedad que la vuelve valiosa: **no mira el payload**. Detecta la forma del ataque, no su contenido, así que ninguna evasión de las matrices de evasión la afecta.

Un endpoint sano tiene una distribución de latencia continua alrededor de una media. Uno bajo extracción temporal tiene dos: las peticiones donde la condición fue falsa, que responden normal, y aquellas donde fue verdadera, que responden exactamente N segundos más tarde. Ese "exactamente" es la señal: **el retardo lo eligió una persona**, así que es un número redondo y se repite idéntico.

## Lógica

```
accesos
| where timestamp > ago(15m)
| summarize
    n = count(),
    p50 = percentile(tiempo_respuesta, 50),
    p95 = percentile(tiempo_respuesta, 95),
    lentas = countif(tiempo_respuesta > 2s),
    valores = dcount(round(tiempo_respuesta, 1))
  by uri_path, client_ip
| where n > 30 and lentas > 5 and p95 > p50 * 10 and valores < 5
```

Las dos últimas condiciones son las que discriminan. `p95 > p50 * 10` captura la separación entre los dos picos; `valores < 5` captura que las lentas se agrupan en **muy pocos valores distintos** — que es lo que distingue un retardo inyectado de una cola de latencias naturales, siempre dispersa.

Refuerzo si existe [[MySQL - slow query log]]: consultas lentas cuyo texto contiene una primitiva de retardo, con `long_query_time` por debajo del retardo usado.

## Falsos positivos conocidos

- **Endpoints con caché**: aciertos rápidos y fallos lentos producen una distribución genuinamente bimodal. Es el falso positivo dominante y el más difícil de separar; ayuda que la latencia de un fallo de caché **no** se agrupa en un valor único.
- **Consultas que degradan con el tamaño del resultado** — una búsqueda que a veces devuelve diez filas y a veces cien mil.
- **Tiempos de espera de servicios externos**, que producen un pico secundario en el valor exacto del tiempo de espera. Este sí se parece mucho, y se separa porque el valor coincide con un tiempo de espera configurado.
- **Escáneres automáticos** que hacen exactamente esto de forma autorizada.

## Evasiones conocidas

- **Retardos aleatorios** en vez de un valor fijo. Rompe la condición de pocos valores distintos y es barato de hacer, aunque casi ninguna herramienta lo hace por defecto.
- **Retardos cortos**, cerca del ruido de red. Deja el ataque debajo del umbral, a costa de multiplicar los errores de medición del atacante.
- **Distribuir el origen**, que rompe el agrupamiento por IP.
- **Ejecución asíncrona** — si la app encola el trabajo, no hay retardo que medir ni por el atacante ni por el defensor. Ver [[Command injection - canal temporal]].

## Cómo se prueba

Disparadores: [[SQLi - canal temporal ciego]] y [[Command injection - canal temporal]].

Es forma `agregado`: necesita volumen y línea base. Y necesita algo que casi nunca está — **el tiempo de respuesta en el formato del log de acceso**, que no viene por defecto. Sin ese campo esta regla no se puede escribir, y habilitarlo es la recomendación previa a desplegarla.
