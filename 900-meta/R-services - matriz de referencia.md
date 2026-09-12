---
tipo: meta
aliases:
  - r-services - matriz
  - rservices cheatsheet
  - rlogin - matriz
  - rsh - matriz
tags:
  - meta/referencia
  - dominio/red
---

# R-services - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los comandos "r" de Berkeley — acceso remoto **legacy, en texto plano**, con autenticación por **confianza de host** (`.rhosts`/`hosts.equiv`) en vez de contraseña. Casi extintos, pero aparecen en Unix viejo. Cliente: paquete `rsh-client`. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST` es el objetivo; `u` el usuario.

## Los servicios y sus puertos

| Servicio | Puerto | Qué hace |
|---|---|---|
| `rexec` | 512/tcp | Ejecución remota; pide usuario y contraseña **en claro** |
| `rlogin` | 513/tcp | Login remoto; confía en `.rhosts`/`hosts.equiv` |
| `rsh` / `rcp` | 514/tcp | Shell y copia remota; misma confianza |
| `rwho` | 513/udp | Quién está logueado en la red local (`rwhod`) |
| `rstat` · `ruptime` | RPC (111) | Estadísticas y uptime vía `rstatd` |

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nmap -sV -p512,513,514 HOST` | Detecta exec/login/shell y sus versiones |
| `rusers -l HOST` | Usuarios logueados en el objetivo (RPC) |

## Ejecutar y entrar

| Comando | Qué hace |
|---|---|
| `rlogin -l u HOST` | Login remoto como `u` |
| `rsh -l u HOST "id"` | Ejecuta un comando |
| `rsh HOST bash -i` | Shell interactiva si hay confianza |
| `rexec -l u -p p HOST "id"` | Ejecuta con credencial (viaja en claro) |
| `rcp archivo u@HOST:/ruta` | Copia (como `cp` pero remoto) |

## El ataque: confianza por `.rhosts` / `hosts.equiv`

El corazón de los r-services. Si el objetivo confía en tu host+usuario, entrás **sin contraseña**.

- `hosts.equiv` (global) o `~/.rhosts` (por usuario) listan `host usuario` de confianza.
- La línea `+ +` significa **confiar en todos** — cualquiera entra como ese usuario.
- Con un `~/.rhosts` de root con `+ +` → `rlogin -l root HOST` es shell de root sin credencial.

Si tenés escritura sobre el home de un usuario (por otra vía), **crear su `~/.rhosts` con tu `host usuario`** es acceso passwordless — a la vez explotación y persistencia.

## Fuga de información

| Comando | Qué da |
|---|---|
| `rwho` | Usuarios logueados en los hosts de la red local |
| `ruptime` | Uptime y carga de esos hosts |
| `rusers -al HOST` | Usuarios en un host puntual |

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `/etc/hosts.equiv` | Hosts de confianza a nivel sistema |
| `~/.rhosts` | Confianza por usuario — **`+ +` = acceso passwordless** |
| `/etc/inetd.conf` · `xinetd.d/` | Dónde se habilitan `shell`/`login`/`exec` |

### Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| `+ +` en `.rhosts`/`hosts.equiv` | Confía en cualquier host y usuario → acceso libre |
| Un `.rhosts` de root | Login de root sin contraseña |
| Los servicios habilitados | Todo el tráfico (incluida la credencial de `rexec`) viaja en claro |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `command not found: rlogin` | falta el cliente | instalar `rsh-client` |
| `Permission denied` | no hay confianza para tu host+usuario | apuntar a un usuario con `.rhosts` laxo, o escribir uno |
| conecta pero pide contraseña | no está confiando; cae a auth normal | probar otro usuario, o `rexec` con credencial |
| nada en 512-514 | servicios deshabilitados (lo normal hoy) | confirmar con `nmap`; buscar Unix viejo |
