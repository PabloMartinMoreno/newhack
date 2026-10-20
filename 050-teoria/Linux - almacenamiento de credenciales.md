---
tipo: teoria
habilita: ["[[Cracking offline - matriz de referencia]]", "[[Enumeración de privesc Linux - matriz de referencia]]", "[[MOC - Ataques de contraseña]]"]
relacionadas: ["[[Windows - almacenamiento de credenciales]]"]
aliases:
  - shadow
  - passwd
  - opasswd
  - PAM
  - yescrypt
tags: []
---

# Linux - almacenamiento de credenciales

## Qué dice la especificación

La autenticación pasa por **PAM** (Pluggable Authentication Modules). El módulo `pam_unix.so` es el que valida contra las contraseñas Unix locales: lee y escribe `/etc/passwd` y `/etc/shadow` cuando alguien se loguea o corre `passwd`. PAM tiene otros módulos apilables (LDAP, Kerberos, montaje) que no tocan estos archivos; acá importa la ruta Unix clásica.

**`/etc/passwd`** — una línea por usuario, **legible por todos**, siete campos separados por `:`:

```
htb-student:x:1000:1000:,,,:/home/htb-student:/bin/bash
```

`usuario : password : UID : GID : GECOS : home : shell`. El campo password hoy es casi siempre `x`: indica "el hash está en `/etc/shadow`". Un hash real ahí es legacy o error de configuración.

**`/etc/shadow`** — mismo formato, pero **solo lo lee root** (o el grupo `shadow`). Nueve campos:

```
htb-student:$y$j9T$3QSBB6...f8Ms:18955:0:99999:7:::
```

`usuario : hash : últimocambio : edadmín : edadmáx : aviso : inactividad : expiración : reservado`. Un usuario en `passwd` **sin** entrada en `shadow` es inválido. El campo hash dice más que el hash:

- `!` o `*` → la cuenta no puede loguear **con contraseña Unix** (pero sí por clave SSH o Kerberos).
- vacío → no pide contraseña para loguear.
- con hash → formato `$<id>$<salt>$<hash>`, donde el **id delata el algoritmo**:

| ID | Algoritmo | Cómo se rompe |
|---|---|---|
| `$1$` | md5crypt | hashcat `-m 500` — viejo, rápido |
| `$2a$`/`$2y$`/`$2b$` | bcrypt (Blowfish) | hashcat `-m 3200` — lento por diseño |
| `$5$` | sha256crypt | hashcat `-m 7400` |
| `$6$` | sha512crypt | hashcat `-m 1800` — el común en muchas distros |
| `$sha1$` | sha1crypt | john |
| `$7$` | scrypt | john |
| `$y$` / `$gy$` | yescrypt / gost-yescrypt | **john** — hashcat no tiene modo estable; es el **default moderno** en Debian/Ubuntu |

**`/etc/security/opasswd`** — `pam_unix.so` guarda acá las contraseñas **viejas** para impedir reúso. Lo lee root. Varias entradas por usuario separadas por `,`, cada una con su propio prefijo de algoritmo.

## Dónde el diseño abre superficie

Cada decisión de diseño es un vector:

- **`passwd` world-readable** — pensado para que cualquier proceso resuelva UID↔nombre, pero si un hash quedó ahí (legacy o misconfig), lo lee y crackea cualquiera sin privilegio.
- **`shadow` solo-root** — por eso leerlo ya implica root o pertenecer al grupo `shadow`; un backup olvidado o ese grupo mal asignado lo expone igual.
- **El prefijo del hash es público** — decide la factibilidad del crackeo antes de empezar: `$1$` cae en minutos, `$y$` es caro a propósito.
- **`/etc` o `passwd` escribibles** — una app que pidió permisos de más sobre `/etc` deja agregar un root propio o **blanquear** el campo de contraseña de root.
- **`opasswd`** — el historial de contraseñas viejas revela patrones de reúso (un `$1$` viejo rompe fácil y suele parecerse a la actual).

## Qué habilita

- Crackear lo que sale de `shadow` (o de `passwd` legacy): [[Cracking offline - matriz de referencia]] — el id del prefijo elige el `-m`.
- Los vectores de privesc que dependen de estos archivos (passwd/shadow escribible o legible, grupo `shadow`, `opasswd`): [[Enumeración de privesc Linux - matriz de referencia]].
- El dominio entero y de dónde sale cada hash: [[MOC - Ataques de contraseña]].

La contraparte en Windows (SAM/LSASS/DPAPI) es [[Windows - almacenamiento de credenciales]]: distinto almacén, misma idea de "lo que el sistema guarda para no re-pedir la clave es volcable con el privilegio justo".

## Cómo se ve en la práctica

Con root, `unshadow` (de John the Ripper) fusiona `passwd` + `shadow` en el formato `user:hash` listo para romper; el detalle está en [[Cracking offline - matriz de referencia]]. Si el default es **yescrypt** (`$y$`), el ataque va por john, no por GPU con hashcat.

Un `passwd` escribible permite el caso extremo: borrar el campo de contraseña de root deja `root::0:0:...` y `su` entra sin pedir nada.

Del lado defensivo (sin nota propia en el vault todavía): el cambio de contraseña y el reúso quedan en los logs de PAM (`/var/log/auth.log`), y la lectura de `shadow` por un proceso inesperado es auditable con `auditd`.

## Fuente

- `man 5 passwd` · `man 5 shadow` · `man 8 pam_unix` · libxcrypt (formatos de hash y prefijos).
