---
tipo: meta
aliases:
  - xfreerdp - matriz
  - xfreerdp cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# xfreerdp - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los flags de `xfreerdp`, el cliente RDP de cabecera. El criterio de ataque de RDP (recon, brute, BlueKeep, robo de sesión) vive en [[RDP - matriz de referencia]]; acá va la sintaxis del comando.

`HOST`, `u`, `p`, `DOM` son marcadores. Sintaxis de FreeRDP 2/3: `/flag` o `/flag:valor`, `+flag`/`-flag` para activar/desactivar.

## Conexión y autenticación

| Flag | Qué hace |
|---|---|
| `/v:HOST` | Objetivo (agregar `:puerto` si no es 3389) |
| `/u:u` `/p:'p'` `/d:DOM` | Usuario, contraseña y dominio |
| `/pth:NTHASH` | Pass-the-hash (necesita Restricted Admin en el destino) |
| `/cert:ignore` | Acepta el certificado autofirmado |
| `/sec:nla` \| `tls` \| `rdp` | Forzar el modo de seguridad |
| `/gateway:g:GW,u:u,p:p` | Conectar a través de un RD Gateway |

## Pantalla

| Flag | Qué hace |
|---|---|
| `/f` | Pantalla completa (Ctrl+Alt+Enter alterna) |
| `/w:1600 /h:900` | Resolución fija |
| `/dynamic-resolution` | Ajusta al redimensionar la ventana |
| `/multimon` | Usa todos los monitores |
| `/bpp:16` | Profundidad de color (baja = más rápido) |

## Redirección (transferencia y periféricos)

| Flag | Qué hace |
|---|---|
| `+clipboard` | Portapapeles compartido |
| `/drive:loot,/tmp` | Monta `/tmp` local como unidad en la sesión — **vía de transferencia** |
| `+home-drive` | Monta tu home directamente |
| `/sound` `/microphone` | Audio |
| `/printer` `/smartcard` | Impresora / lectora |

## Rendimiento

| Flag | Qué hace |
|---|---|
| `/network:lan` | Perfil de red rápido (activa cachés) |
| `/compression` | Comprime el flujo |
| `/gfx` | Pipeline gráfico moderno (RemoteFX/H264) |

## Ejemplos armados

```sh
# Básico, ignorando el cert
xfreerdp /u:u /p:'p' /v:HOST /cert:ignore

# Con dominio, portapapeles y disco para exfiltrar
xfreerdp /u:u /d:DOM /p:'p' /v:HOST /cert:ignore +clipboard /drive:loot,/tmp

# Pass-the-hash a pantalla completa
xfreerdp /u:u /pth:NTHASH /v:HOST /cert:ignore /f
```

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `certificate ... not trusted` | cert autofirmado | `/cert:ignore` |
| `ERRCONNECT_LOGON_FAILURE` | credencial o dominio mal | agregar `/d:DOM`, revisar credencial |
| `ERRCONNECT_SECURITY_NEGO...` | desajuste de modo de seguridad | forzar `/sec:nla` o `/sec:tls` |
| PtH rechazado | Restricted Admin apagado en el destino | usar la contraseña |
| en FreeRDP viejo, `-` en vez de `/` | sintaxis vieja (`-u user`) | actualizar, o usar la sintaxis vieja consistente |
