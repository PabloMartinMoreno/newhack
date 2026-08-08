---
tipo: tradecraft
clase: "[[CWE-78 - OS Command Injection]]"
eje: canal-de-extraccion
implementacion: "Condición convertida en retardo de respuesta mediante un comando que duerme"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]"]
requisitos: [shell-invocada, sin-salida-reflejada, sin-egress]
coste: alto
alternativas: ["[[Command injection - canal ciego]]", "[[Command injection - canal fuera de banda]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - command injection temporal
  - time-based command injection
tags:
  - dominio/web
---

# Command injection - canal temporal

## Cuándo lo elijo

Último recurso, igual que su gemelo [[SQLi - canal temporal ciego]]: sin salida reflejada, sin lugar donde escribir un archivo legible y sin egress hacia fuera de banda. Cualquier otra rama del árbol de [[MOC - Command injection]] extrae más rápido.

Su uso principal no es extraer sino **confirmar**. Es la prueba universal de ejecución de comandos: funciona en todo contexto, no depende de que la salida vuelva, y un retardo de N segundos que se reproduce a demanda es evidencia difícil de discutir en un informe.

## Por qué funciona

El canal de datos es la latencia de la respuesta: la petición HTTP no vuelve hasta que el comando inyectado termina, así que dormir N segundos dentro del comando desplaza la respuesta N segundos. Ver [[La latencia como canal de datos]] — el mecanismo es idéntico al de SQLi, solo cambia quién duerme.

Para extraer y no solo confirmar, se encadena el retardo detrás de una condición evaluada en el propio shell. Cada petición devuelve un bit.

## Cómo falla

- **Timeout del servidor, proxy o WAF** — corta antes de que se cumpla el retardo y todas las respuestas se ven iguales. Obliga a bajar el retardo hasta acercarlo al ruido de red.
- **Jitter de red** — con retardos cortos la señal se confunde con el ruido. Retardos largos multiplican el tiempo total del ataque.
- **La petición se procesa de forma asíncrona** — si el comando corre en una cola o en segundo plano, la respuesta vuelve al instante y el canal no existe, aunque la ejecución sí. Es el falso negativo clásico: se descarta una vulnerabilidad real por probar solo esto.
- **Riesgo de DoS accidental** — cada petición retiene un worker del servidor durante todo el retardo. Con concurrencia o retardos altos se agota el pool y se cae el sitio. Retardo bajo y concurrencia en uno, siempre.
- **`sleep` ausente o bloqueado** — en Windows no existe como tal y hay que suplirlo; en contenedores mínimos puede faltar el binario.

## Coste

El más caro: un bit por petición, cada una esperando el retardo completo cuando la condición se cumple. Extraer algo de largo real por este canal es inviable en la práctica — se usa para confirmar y después se cambia de canal, o se acepta la extracción parcial.

## Huella esperada

- Distribución de latencias **bimodal** en [[Log de acceso del servidor web]], si el formato incluye el tiempo de respuesta. Es el mismo sello que deja el canal temporal de SQLi, y se detecta sin mirar el payload.
- [[Proceso hijo del servidor web]] muestra procesos hijos de vida anormalmente larga: un `sleep` colgando de `php-fpm` no tiene explicación legítima.
- Ráfaga de peticiones al mismo endpoint con el mismo parámetro variando poco entre una y otra.

Los payloads de retardo por shell y la lógica de extracción están en [[Command injection ciego - matriz de referencia]].
