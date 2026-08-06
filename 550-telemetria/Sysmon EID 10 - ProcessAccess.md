---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 10"
por-defecto: false
coste: alto
aliases:
  - Sysmon EID 10
  - ProcessAccess
tags:
  - plataforma/windows
---

# Sysmon EID 10 - ProcessAccess

## Qué lo genera

Un proceso abre un handle a otro proceso. Se registra en el momento de `OpenProcess`, con la máscara de acceso solicitada — antes de que se lea un solo byte de memoria.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `SourceImage` | Ejecutable que pide el handle | Distinguir lo esperado (`MsMpEng.exe`, `csrss.exe`) del resto |
| `TargetImage` | Proceso accedido | Filtrar por `lsass.exe` |
| `GrantedAccess` | Máscara de acceso concedida | `0x1010`/`0x1410` implican lectura de memoria |
| `CallTrace` | Pila de llamadas hasta el `OpenProcess` | Delata `dbghelp.dll`/`dbgcore.dll` y llamadas desde memoria sin respaldo en disco |

`CallTrace` es el campo caro y el que más valor tiene: es lo que separa una detección por nombre de proceso de una por comportamiento.

## Coste de recolección

Alto sin filtrado. La configuración debe excluir por `TargetImage` y quedarse con los objetivos sensibles, o el volumen hace inviable la retención.

## Cómo se activa

Sysmon no viene instalado en Windows. Requiere despliegue y una configuración con la regla `ProcessAccess` — la configuración por defecto de Sysmon no la incluye de forma útil.

## Limitaciones

- No ve lecturas hechas desde kernel ni desde un proceso ya protegido.
- Si la lectura se hace vía un handle **heredado** o duplicado en vez de un `OpenProcess` propio, el evento no aparece con el proceso real como `SourceImage`.
- Es un artefacto de host: si el host no está desplegado, no existe. Ver [[Consultas del vault]] § Puntos únicos de fallo.

## Quién lo emite / quién lo consume

Rojo: [[LSASS - volcado vía comsvcs.dll MiniDump]]
Azul: [[Acceso a LSASS desde proceso no firmado]]
