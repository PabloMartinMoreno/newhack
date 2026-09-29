---
tipo: tradecraft
clase: "[[T1059 - Command and Scripting Interpreter]]"
eje: origen-del-payload
implementacion: "Binario o shellcode fabricado con msfvenom, entregado y ejecutado en el objetivo"
opsec: quemado
telemetria: ["[[Sysmon EID 1 - ProcessCreate]]", "[[Sysmon EID 3 - NetworkConnect]]"]
requisitos: [ejecucion-confirmada, formato-o-capacidad-que-el-one-liner-no-da]
coste: medio
alternativas: ["[[Shell - conexión reversa]]"]
probado: nunca
contexto: [win2019-defender, ubuntu22-auditd]
aliases:
  - payload generado
  - staged vs stageless
tags:
  - dominio/post-explotacion
---

# Payload generado con msfvenom

## Cuándo lo elijo

Cuando el one-liner nativo no alcanza, y solo entonces. Tres motivos legítimos: (1) hace falta un **formato concreto** —`.exe`, `.dll`, `.elf`, `.war`, `.apk`, un macro— porque la primitiva de entrega ejecuta un archivo, no una línea; (2) el objetivo **no tiene intérprete** conveniente (ni `bash`, ni `python`, ni PowerShell usable); (3) se quiere la **sesión Meterpreter** por sus capacidades (pivot, port-forward, `hashdump`, migración de proceso) integradas con Metasploit.

Para simplemente abrir una sesión, el default correcto es el one-liner nativo de [[Shell - conexión reversa]]: no toca disco, no arrastra la firma de [[metasploit]] y se confunde mejor con el sistema. El binario generado es la excepción, no la regla. El comando y los formatos, en [[msfvenom - matriz de referencia]].

## Por qué funciona

msfvenom empaqueta un payload (el código que da la sesión) en un contenedor que el objetivo ejecuta. La decisión de fondo es **staged vs stageless**, y se lee en el nombre del payload:

- **Staged** (`windows/meterpreter/reverse_tcp`, con `/`): manda un *stager* mínimo que, al ejecutarse, descarga el resto por la misma conexión. Payload inicial chico; la etapa grande viaja en runtime. Necesita un handler que sepa servir la etapa.
- **Stageless** (`windows/meterpreter_reverse_tcp`, con `_`): todo el código va en el artefacto. Más grande, pero **autocontenido y más confiable** sobre enlaces malos o cuando la segunda conexión no puede volver.

El handler que atrapa la sesión es `exploit/multi/handler` de Metasploit, con el mismo `PAYLOAD`/`LHOST`/`LPORT` — ver la matriz.

## Cómo falla

- **AV/EDR lo levanta de entrada** — es el modo de fallo dominante y la razón del `opsec: quemado`. Los payloads default y los encoders clásicos (`shikata_ga_nai`) están firmados por todos los motores desde hace años. Codificar con `-e` **no evade EDR moderno**: ofusca bytes, no comportamiento. Sirve para *bad chars*, no para sigilo.
- **Staged contra egress de un solo tiro** — si la segunda conexión (la de la etapa) no puede volver, la sesión staged no se completa; ahí gana el stageless.
- **Arquitectura equivocada** — un payload x64 en un proceso x86 (o al revés) no corre. `-p` y el proceso destino tienen que coincidir.
- **Bad chars sin filtrar** — en explotación de memoria, un `\x00`/`\x0a` no excluido con `-b` corta el shellcode.
- **Meterpreter en memoria migra a inyección** — al migrar o inyectarse en otro proceso, deja de ser este dominio y pasa a process injection y su telemetría (`CreateRemoteThread` = [[Sysmon EID 8 - CreateRemoteThread]], `ImageLoad` = [[Sysmon EID 7 - ImageLoad]]), que el vault todavía no consume con ninguna detección. Hueco anotado en [[MOC - Shells]].

## Coste

Medio en esfuerzo —generar, entregar y atrapar—, alto en OPSEC. Un binario de msfvenom en disco es evidencia forense directa y candidato número uno de cualquier AV. Para un engagement serio: entrega en memoria, artefacto borrado apenas ejecuta, y registrar en el informe qué se dejó.

## Huella esperada

- El proceso del payload al ejecutar — [[Sysmon EID 1 - ProcessCreate]], con un padre anómalo si vino de un RCE.
- La conexión saliente del stager/payload hacia el handler — [[Sysmon EID 3 - NetworkConnect]]; en staged, **dos** conexiones (stager y etapa) sobre el mismo destino.
- El artefacto en disco, si se entregó como archivo — lo ve el AV y queda para forense.
