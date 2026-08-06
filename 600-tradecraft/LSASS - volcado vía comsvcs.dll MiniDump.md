---
tipo: tradecraft
clase: "[[T1003.001 - LSASS Memory]]"
implementacion: "rundll32 comsvcs.dll,MiniDump — LOLBin, sin binario propio en disco"
opsec: quemado
telemetria: ["[[Sysmon EID 10 - ProcessAccess]]"]
requisitos: [admin-local, seDebugPrivilege]
coste: bajo
alternativas: []
probado: 2025-11-20
contexto: [win2019-defender, win11-defender]
aliases:
  - comsvcs MiniDump
tags:
  - dominio/ad
  - plataforma/windows
---

# LSASS - volcado vía comsvcs.dll MiniDump

> [!danger] `opsec: quemado`
> Firmada por todos los EDR relevantes y por reglas ASR de Defender desde hace años. Está en el vault como **línea base de comparación** y como caso de prueba para detecciones, no como opción operativa. Ver [[Consultas del vault]] § Backlog de revalidación.

## Cuándo lo elijo

Prácticamente nunca en un entorno con EDR. Sirve en dos casos:

1. **Validar una detección propia** — es el disparador más limpio y reproducible de [[Acceso a LSASS desde proceso no firmado]].
2. Entornos sin EDR y sin PPL donde el objetivo es velocidad y no sigilo.

Cuando el objetivo es sigilo, la decisión se toma en otro eje: evitar el `OpenProcess` desde un proceso propio, o no tocar LSASS en absoluto.

## Por qué funciona

`comsvcs.dll` exporta `MiniDump`, que envuelve `MiniDumpWriteDump`. Al invocarse vía `rundll32`, el binario que abre el handle a LSASS es un ejecutable firmado por Microsoft y presente en todo Windows: no hay artefacto propio en disco.

## Cómo falla

- **PPL (RunAsPPL)** — el handle con permisos de lectura no se concede; la técnica muere antes de empezar.
- **Credential Guard** — el volcado se obtiene igual, pero los secretos reutilizables no están ahí.
- **Reglas ASR de Defender** — bloqueo directo del acceso a LSASS.
- **Detección por `CallTrace`** — la pila delata `dbghelp.dll`/`dbgcore.dll` incluso si el `SourceImage` es un binario firmado. Ese es exactamente el campo que usa la detección propia.

## Coste

Bajo en esfuerzo, altísimo en riesgo de detección. Requiere admin local y `SeDebugPrivilege`. Deja un archivo de volcado grande en disco que además hay que exfiltrar.

## Huella esperada

- [[Sysmon EID 10 - ProcessAccess]] con `TargetImage: lsass.exe` y `GrantedAccess: 0x1410`.
- `SourceImage: rundll32.exe`, `CallTrace` con `dbgcore.dll`.
- Escritura de un archivo de varios cientos de MB.
- Windows `4688` con la línea de comandos, si está habilitado el registro de argumentos.
