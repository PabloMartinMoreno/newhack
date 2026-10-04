---
tipo: meta
aliases:
  - privesc Linux
  - enumeración de privilegios Linux
  - Linux privesc enum
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Enumeración de privesc Linux - matriz de referencia

> [!info] Referencia pura, no un zettel
> Las búsquedas que revelan un vector de escalada local en Linux, una vez con shell. El criterio de fase, en [[MOC - Post-explotación]]. Cómo **abusar** cada binario/capability encontrado: GTFOBins (link abajo). Windows es una nota hermana, todavía hueco. Ver también [[Enumeración de privesc Linux - matriz de referencia#Automatizado]] para correrlo todo de una.

Comandos genéricos, sin datos de objetivo. `2>/dev/null` en todo lo que recorre `/` para no ahogarse en errores de permiso. Las tuberías van escapadas `\|` en las tablas; al copiar son `|`.

## Por dónde empezar
Los que más rinden, en orden: **`sudo -l` → SUID → capabilities → cron → escribibles → versión de kernel**. Si algo de eso cae, no hace falta seguir.

## Contexto básico

| Busco | Comando | Qué indica |
|---|---|---|
| Quién soy y mis grupos | `id` · `groups` | grupo peligroso (docker, lxd, disk, adm, sudo) → salto directo |
| Qué puedo con sudo | `sudo -l` | binarios sudo sin contraseña → GTFOBins; `env_keep`, `NOPASSWD` |
| SO y arquitectura | `uname -a` · `cat /etc/os-release` · `arch` | versión de kernel → exploit conocido |
| Usuarios con shell | `grep -vE 'nologin\|false' /etc/passwd` | otras cuentas a las que pivotar |
| Hash en passwd (legacy) | `grep -v '^[^:]*:[x*!]' /etc/passwd` | contraseña en el propio passwd |


## SUID / SGID

| Busco | Comando |
|---|---|
| Binarios SUID | `find / -perm -4000 -type f 2>/dev/null` |
| Binarios SGID | `find / -perm -2000 -type f 2>/dev/null` |
| SUID **y** SGID | `find / -perm -6000 -type f 2>/dev/null` |
| Con detalle (dueño/tamaño) | `find / -perm -4000 -type f -exec ls -la {} \; 2>/dev/null` |

Cada binario no estándar → buscarlo en GTFOBins § SUID. Los de siempre (`passwd`, `mount`, `su`) son normales; el raro (`find`, `nmap`, `vim`, `python`, un binario custom) es el vector. Un intérprete (`python`/`perl`/`ruby`) SUID es escalada directa: [[Python SUID y setuid capability - matriz de referencia]].

## Capabilities

| Busco | Comando | Qué indica |
|---|---|---|
| Capabilities en binarios | `getcap -r / 2>/dev/null` | `cap_setuid`, `cap_dac_read_search` → GTFOBins § Capabilities |

`python3` o `perl` con `cap_setuid+ep` = root en una línea: [[Python SUID y setuid capability - matriz de referencia]]. Es SUID "invisible": no aparece en `find -perm -4000`.

## Cron y tareas programadas

| Busco | Comando | Qué indica |
|---|---|---|
| Crontab del sistema | `cat /etc/crontab` | script corrido como root a intervalo |
| Directorios cron | `ls -la /etc/cron.d /etc/cron.daily /etc/cron.hourly 2>/dev/null` | script escribible ejecutado por root |
| Timers de systemd | `systemctl list-timers --all` | equivalente moderno de cron |
| Tareas de otros procesos (sin ser root) | `pspy` (subir binario) | ve cron/procesos que no salen en `ps` |

Si un script de cron corriendo como root es **escribible** por vos, o usa un comando sin ruta absoluta con tu PATH manipulable → escalada.

## Archivos escribibles e interesantes

| Busco | Comando |
|---|---|
| Archivos world-writable | `find / -perm -2 -type f 2>/dev/null` |
| Directorios world-writable | `find / -writable -type d 2>/dev/null` |
| Escribibles por mí que no son míos | `find / -writable ! -user $(whoami) -type f 2>/dev/null` |
| `/etc/passwd` / `/etc/shadow` escribibles | `ls -la /etc/passwd /etc/shadow` |
| `/etc/sudoers` o `sudoers.d` escribibles | `ls -la /etc/sudoers /etc/sudoers.d/ 2>/dev/null` |

`/etc/passwd` escribible → agregar un usuario root con hash propio (`openssl passwd`). `/etc/shadow` legible → crackear offline ([[Cracking offline - matriz de referencia]], `-m 1800` para `$6$`).

## PATH y variables

| Busco | Comando | Qué indica |
|---|---|---|
| PATH actual | `echo $PATH` | un `.` o un dir escribible al principio → PATH hijacking |
| Variables de entorno | `env` · `cat /proc/self/environ` | credenciales, `LD_PRELOAD` reutilizable |


## Kernel y software (para exploit)

| Busco | Comando | Qué indica |
|---|---|---|
| Versión de kernel | `uname -r` | mapear a CVE (DirtyPipe, DirtyCow, PwnKit…) |
| Versión de sudo | `sudo -V \| head -1` | sudo < 1.9.5p2 → Baron Samedit (CVE-2021-3156) |
| Paquetes instalados | `dpkg -l 2>/dev/null` · `rpm -qa 2>/dev/null` | versión vulnerable conocida |


## Procesos, servicios y red

| Busco | Comando | Qué indica |
|---|---|---|
| Procesos (¿qué corre como root?) | `ps aux` · `ps -ef` | servicio root explotable, credenciales en la línea de comando |
| Puertos en escucha (solo local) | `ss -tulpn` · `netstat -tulpn` | servicio interno no expuesto afuera → pivote local |
| Servicios | `systemctl list-units --type=service` | servicio escribible/mal configurado |


## Credenciales en disco

| Busco | Comando |
|---|---|
| Historial de shell | `cat ~/.bash_history ~/.zsh_history 2>/dev/null` |
| Claves SSH y config | `find / -name id_rsa -o -name id_dsa -o -name authorized_keys 2>/dev/null` |
| Config con secretos | `grep -rniE 'password\|passwd\|secret\|api_key' /var/www /opt /home /etc 2>/dev/null` |
| Archivos `.env` / config | `find / -name ".env" -o -name "*.conf" 2>/dev/null` |
| Montajes y fstab | `mount` · `cat /etc/fstab` | credenciales de montaje, NFS (ver [[NFS - matriz de referencia]]) |

## Grupos peligrosos
`id` que muestre uno de estos suele ser escalada directa:

| Grupo | Por qué |
|---|---|
| `sudo` / `wheel` | `sudo -l` |
| `docker` / `lxd` | montar `/` en un contenedor → root del host |
| `disk` | leer/escribir el dispositivo crudo (`debugfs /dev/sda`) |
| `adm` | leer logs (credenciales, rutas) |
| `shadow` | leer `/etc/shadow` → crackear |


## Automatizado
Corren todo lo de arriba de un saque. Entran como entidades en `400-entidades/` (pendientes). El manual sirve cuando no podés subir binarios o querés no hacer ruido.

| Herramienta | Qué hace |
|---|---|
| LinPEAS | el enumerador de referencia; colorea lo interesante |
| LinEnum / linux-smart-enumeration | alternativas más livianas |
| pspy | procesos y cron **sin ser root** — clave para cron oculto |
| linux-exploit-suggester | mapea `uname -r` a exploits de kernel |

## GTFOBins — de la búsqueda al abuso

Esta matriz **encuentra** el vector; [gtfobins.github.io](https://gtfobins.github.io) dice **cómo abusarlo**: buscá el binario y filtrá por `SUID`, `Sudo` o `Capabilities` según cómo lo hallaste. Es el compañero obligado de las secciones SUID, sudo y capabilities.

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| `find` inunda de `Permission denied` | recorre dirs sin permiso | siempre con `2>/dev/null` |
| `getcap -r /` no existe | falta `libcap` | instalar, o subir un `getcap` estático |
| SUID encontrado pero no escala | no está en GTFOBins | revisar si es custom → leer/decompilar, o buscar CVE |
| `sudo -l` pide contraseña y no la tengo | sin TTY o sin pass | estabilizar la shell ([[Estabilización de shell - matriz de referencia]]); sin pass, saltar sudo |

