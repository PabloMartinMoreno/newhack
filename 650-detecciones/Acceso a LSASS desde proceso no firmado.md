---
tipo: deteccion
tecnicas: ["[[T1003.001 - LSASS Memory]]"]
telemetria: ["[[Sysmon EID 10 - ProcessAccess]]"]
forma: evento
ventana: 
estado: borrador
fidelidad: media
logica: sigma
validada: 2026-06-02
aliases: []
tags:
  - plataforma/windows
---

# Acceso a LSASS desde proceso no firmado

## Qué detecta

Apertura de un handle a `lsass.exe` con máscara de acceso que permite leer memoria, desde un proceso que no está en la lista de accesos legítimos conocidos.

Detecta **el acceso**, no la herramienta. Esa es la razón de anclar en `GrantedAccess` y `CallTrace` y no en `SourceImage`.

## Lógica

```yaml
detection:
  selection:
    EventID: 10
    TargetImage|endswith: '\lsass.exe'
    GrantedAccess:
      - '0x1010'
      - '0x1410'
      - '0x143a'
  filter_legitimos:
    SourceImage|endswith:
      - '\MsMpEng.exe'
      - '\csrss.exe'
      - '\wininit.exe'
  condition: selection and not filter_legitimos
```

Refuerzo de alta fidelidad: `CallTrace` que contenga `dbgcore.dll` o `dbghelp.dll`, o marcos `UNKNOWN` (código ejecutando desde memoria sin respaldo en disco).

## Falsos positivos conocidos

- Antivirus y EDR de terceros que escanean memoria de LSASS.
- Herramientas de monitoreo de rendimiento e inventario.
- Depuradores en estaciones de desarrollo.

La lista de exclusión es específica de cada entorno. La regla no es portable tal cual: se calibra por cliente.

## Evasiones conocidas

- Handles heredados o duplicados en vez de un `OpenProcess` propio.
- Acceso desde kernel o desde un proceso ya protegido.
- Volcado de LSASS sin abrirlo (snapshot de proceso, silo, forzado de un volcado por el propio sistema).

Toda evasión listada acá debería tener su nota en `600-tradecraft/`. Si no la tiene, es un hueco del lado rojo.

## Cómo se prueba

Disparador de referencia: [[LSASS - volcado vía comsvcs.dll MiniDump]]. Laboratorio: ver [[Validación de tradecraft en laboratorio]].

> [!warning] Estado
> `estado: borrador` — validada en laboratorio, sin calibrar contra el ruido de un entorno real. No pasa a `produccion` hasta tener una semana de línea base de falsos positivos.
