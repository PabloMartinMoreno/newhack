---
tipo: tradecraft
clase: "[[T1048 - Exfiltration Over Alternative Protocol]]"
eje: exfiltracion
implementacion: "Sacar datos por un protocolo de propósito general que el perímetro deja salir (HTTP/FTP/SMB)"
opsec: ruidoso
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]"]
requisitos: [salida-de-red-a-un-destino-controlado]
coste: bajo
alternativas: ["[[Exfiltración por canal encubierto]]"]
probado: nunca
contexto: [win11-defender, ubuntu22-auditd]
aliases:
  - exfiltración abierta
tags:
  - dominio/post-explotacion
---

# Exfiltración por canal abierto

## Cuándo lo elijo

Cuando el perímetro deja salir un protocolo de propósito general hacia un destino que controlo: HTTPS a mi servidor, un `POST` a un servicio, FTP o SMB. Es la **primera opción** siempre que exista salida: más rápida, más simple y sin las limitaciones de tamaño y velocidad del canal encubierto.

Se descarta cuando el egress está restringido a destinos o puertos concretos, o hay inspección de contenido — ahí pasa a [[Exfiltración por canal encubierto]].

## Por qué funciona

El firewall permite tráfico saliente de propósito general porque el negocio lo necesita. El dato robado viaja **como tráfico normal**: un `POST` HTTPS es indistinguible de cualquier otro sin romper TLS. El volumen y el destino son las únicas señales, y ambas necesitan línea base.

## Cómo falla

- **DLP** que inspecciona el contenido saliente y marca patrones (números de tarjeta, clasificaciones).
- **Proxy con inspección TLS** que rompe el cifrado y ve el payload.
- **Egress allowlist por destino**: solo salen dominios aprobados, y el mío no está.

## Coste

Bajo. Un `curl` o un `Invoke-WebRequest`. La sintaxis por sistema y canal, en [[Exfiltración - matriz de referencia]].

## Huella esperada

- La conexión saliente a un destino no habitual, en [[Sysmon EID 3 - NetworkConnect]] — pero es tráfico legítimo en la forma; la detección depende de línea base de destino y volumen, no de firma. Ver [[Detectar el efecto sobrevive a la evasión]].
- Del lado de red (que el vault todavía no modela): un pico de subida hacia un destino nuevo.
