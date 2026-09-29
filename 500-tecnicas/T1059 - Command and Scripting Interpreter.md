---
tipo: tecnica
taxonomia: attack
identificador: T1059
tacticas: [execution]
aliases:
  - T1059
  - Command and Scripting Interpreter
  - Intérprete de comandos y scripting
tags:
  - dominio/post-explotacion
---

# T1059 - Command and Scripting Interpreter

## Qué es

Ejecución por medio de un intérprete de comandos o de scripting presente en el objetivo: `sh`/`bash`, `cmd`, PowerShell, Python, Perl, un motor embebido. Es el paraguas de **la shell** — la sesión interactiva que se abre sobre un intérprete, sea que conecte hacia afuera (reverse), escuche (bind) o responda por HTTP (webshell).

## Por qué existe / qué la habilita

Un intérprete es el multiplicador de una primitiva de ejecución de un solo tiro. Ejecutar un comando por vez alcanza para enumerar; a partir de ahí hace falta **estado de sesión** —directorio, variables, un proceso vivo— y eso lo da entregarle a un socket la entrada y salida de un intérprete. La técnica la habilita cualquier RCE aguas arriba: [[MOC - Command injection]], [[MOC - File upload]], deserialización, SSTI, o una credencial válida a un servicio de administración remota.

## Ejes que la descomponen

El criterio no está en la técnica sino en la dirección de la conexión y en el origen del payload. Ejes en [[MOC - Shells]]; sintaxis en [[Reverse y bind shells - matriz de referencia]], [[Estabilización de shell - matriz de referencia]] y [[msfvenom - matriz de referencia]].

| Eje | Valores |
|---|---|
| Dirección de conexión | reverse · bind · sin socket (webshell) |
| Origen del payload | one-liner nativo (LOLBin) · binario generado (msfvenom) |
| Interactividad | dumb shell · TTY completo |
| Sistema | Windows · Linux |

## Referencias canónicas

- MITRE ATT&CK: [T1059](https://attack.mitre.org/techniques/T1059/) — subtécnicas relevantes: `.001` PowerShell, `.003` Windows Command Shell, `.004` Unix Shell, `.006` Python.
