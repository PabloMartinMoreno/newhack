---
tipo: meta
aliases:
  - credential hunting Linux
  - búsqueda de credenciales Linux
  - loot Linux
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Búsqueda de credenciales en Linux - matriz de referencia

> [!info] Referencia pura, no un zettel
> Lo primero tras conseguir shell: barrer el host por secretos reusables que escalen o permitan pivotar. Es parte del privesc local — el resto (SUID, sudo, cron como vector, capabilities, kernel) en [[Enumeración de privesc Linux - matriz de referencia]]. Lo que salga **crackeable** (hashes, `key4.db`, KeePass) va a [[Cracking offline - matriz de referencia]].
> El criterio de fase, en [[MOC - Post-explotación]]. Cuatro fuentes: **archivos, historial/logs, memoria, keyrings**.

Comandos genéricos, sin datos de objetivo. `2>/dev/null` en todo lo que recorre `/`. Pipes escapadas `\|` en las tablas; al copiar son `|`. El principio: en Linux **todo es un archivo**, así que casi todo el loot se encuentra con `find` + `grep` bien dirigidos.

## 1. Archivos

| Fuente | Base | Qué trae |
|---|---|---|
| Configuración | `find / -name "*.conf" -o -name "*.cnf" -o -name "*.config" 2>/dev/null` | credenciales de servicios (mysql, apache, vpn), rutas |
| Bases de datos | `find / -name "*.sql" -o -name "*.db" -o -name "*.sqlite*" 2>/dev/null` | hashes, tokens, dumps de app |
| Notas | `find /home /root /opt -type f \( -name "*.txt" -o ! -name "*.*" \) 2>/dev/null` | listas de accesos, credenciales sueltas |
| Scripts | `find / -name "*.py" -o -name "*.sh" -o -name "*.pl" -o -name "*.php" 2>/dev/null` | credenciales hardcodeadas para correr sin interacción |
| Claves SSH | `find / \( -name "id_rsa" -o -name "id_ed25519" -o -name "*.pem" -o -name "authorized_keys" \) 2>/dev/null` | acceso directo a este u otros hosts |
| Cron (como fuente) | `cat /etc/crontab` · `ls -la /etc/cron.d/` · `crontab -l` | credenciales metidas en la línea del job |

Las config son el núcleo: a menudo traen la credencial **y** explican cómo funciona el servicio. Marcadas con `.conf`/`.config`/`.cnf`, pero el nombre puede estar cambiado — no asumir la extensión. Barrido completo de config, filtrando ruido del sistema:

```bash
for e in .conf .config .cnf; do
  echo -e "\n== $e =="
  find / -name "*$e" 2>/dev/null | grep -v "lib\|fonts\|share\|core"
done
```

Y en vez de abrir uno por uno, grepear credenciales dentro de cada `.cnf` (misma idea para las otras extensiones):

```bash
for f in $(find / -name "*.cnf" 2>/dev/null | grep -v "doc\|lib"); do
  echo -e "\n# $f"
  grep -iE "user|pass|password" "$f" 2>/dev/null | grep -v "#"
done
```

> Cron tiene **dos caras**: acá es fuente de credenciales (una clave en la línea del job); como vector de escalada —script escribible corrido por root— vive en [[Enumeración de privesc Linux - matriz de referencia]] § Cron.

## 2. Historial y logs

| Fuente | Comando | Qué trae |
|---|---|---|
| Historial de shell | `cat /home/*/.bash_history /root/.bash_history 2>/dev/null` | contraseñas tipeadas en claro, usuarios, hosts |
| Config de shell | `cat ~/.bashrc ~/.bash_profile ~/.zsh_history 2>/dev/null` | alias y exports con secretos |
| Logs clave | ver tabla abajo | autenticación, sudo, comandos con credenciales |

El `.bash_history` es oro: comandos como `mysql -u root -pPASS` o `su` seguido de la clave quedan literales. Logs que más rinden:

| Archivo | Qué guarda |
|---|---|
| `/var/log/auth.log` (Debian) · `/var/log/secure` (RHEL) | autenticación, `sudo`, sesiones SSH |
| `/var/log/syslog` · `/var/log/messages` | actividad general del sistema |
| `/var/log/cron` | ejecuciones de cron |
| `/var/log/apache2/*` · `/var/log/mysql/*` | credenciales en URLs/queries logueadas |

Barrido de líneas interesantes en todos los logs de una:

```bash
for f in $(ls /var/log/* 2>/dev/null); do
  grep -liE "accepted|session opened|failure|failed|sudo|COMMAND=|password changed|new user" "$f" 2>/dev/null
done
```

## 3. Memoria y caché

Credenciales que un proceso dejó en RAM (sesión gráfica activa, servicios). Requiere root:

`sudo python3 mimipenguin.py`

Es el equivalente Linux de volcar LSASS: lee la memoria de procesos conocidos (GNOME Keyring, LightDM, VSFTPd, Apache, SSH) y saca contraseñas en claro de los usuarios logueados.

## 4. Keyrings y navegador

El almacén cifrado del usuario. Firefox guarda los logins cifrados en `logins.json`, con las claves en `key4.db`:

| Paso | Comando |
|---|---|
| Ubicar perfiles | `ls -la ~/.mozilla/firefox/*.default*/` |
| Ver los blobs | `cat ~/.mozilla/firefox/*.default*/logins.json \| jq .` |
| Descifrar | `python3 firefox_decrypt.py` — pide el perfil, devuelve URL/usuario/clave en claro |

`firefox_decrypt` saca los `encryptedUsername`/`encryptedPassword` sin la master password si el usuario no puso una. Los keyrings del SO (GNOME Keyring, KWallet) cifran con una master key y se abren desde la sesión del usuario.

Para no ir fuente por fuente, **LaZagne** barre casi todo lo de esta matriz de un saque (navegadores, Wifi/wpa_supplicant, libsecret, KWallet, SSH, Git, AWS, FileZilla, KeePass, `/etc/shadow`, keyrings):

`sudo python2.7 laZagne.py all` · `python3 laZagne.py browsers`

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| `find` inunda de `Permission denied` | recorre dirs sin permiso | siempre con `2>/dev/null` |
| `firefox_decrypt` pide master password | el usuario puso una | crackearla (hashcat `-m 26100`/`26300` sobre `key4.db`) o abandonar ese perfil |
| `mimipenguin` no saca nada | sin sesión gráfica activa o sin root | caer a archivos/historial |
| El barrido no encuentra nada obvio | credenciales fuera de las rutas típicas | adaptar al rol del host: un DB server guarda secretos distintos que un workstation |
