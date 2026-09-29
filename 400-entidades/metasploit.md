---
tipo: entidad
clase-entidad: herramienta
tecnicas: ["[[T1059 - Command and Scripting Interpreter]]", "[[T1105 - Ingress Tool Transfer]]"]
aliases:
  - Metasploit
  - msfconsole
  - msfvenom
  - Meterpreter
tags:
  - dominio/post-explotacion
---

# metasploit

## Qué es

Framework de explotación. Tres piezas importan para el dominio de shells y payloads:

- **msfvenom** — el generador de payloads: fabrica el binario/shellcode que da la sesión, en el formato y para la plataforma que se pidan.
- **`exploit/multi/handler`** (en `msfconsole`) — el listener que atrapa la sesión que el payload devuelve.
- **Meterpreter** — el payload avanzado: sesión en memoria con pivot, port-forward, `hashdump`, migración de proceso y transferencia de archivos integradas.

## Qué técnicas implementa

- Payload y sesión: [[Payload generado con msfvenom]]
- Sintaxis de generación y handler: [[msfvenom - matriz de referencia]]
- Transferencia integrada (Meterpreter): [[Traer herramientas al objetivo]]

## Cuándo NO usarla

Cuando alcanza un one-liner nativo. Un `bash -i >& /dev/tcp/...` o un `python -c` de [[Reverse y bind shells - matriz de referencia]] abre la sesión sin tocar disco, sin arrastrar la firma de Metasploit y sin la superficie que todo EDR conoce de memoria. msfvenom entra cuando hace falta un **formato** concreto (`.exe`/`.dll`/`.war`), no hay intérprete usable, o se quieren las capacidades de Meterpreter — criterio en [[Payload generado con msfvenom]].

## Estado

Mantenida y activa, y por eso mismo **fuertemente firmada**: los payloads y encoders default (`shikata_ga_nai`) los detecta cualquier AV moderno. Es herramienta de laboratorio, CTF y demostración; en un engagement con EDR real, o se evade en serio (fuera del alcance de `-e`) o se usa otra cosa.

## Notas relacionadas

[[MOC - Shells]] · [[Payload generado con msfvenom]] · [[msfvenom - matriz de referencia]]
