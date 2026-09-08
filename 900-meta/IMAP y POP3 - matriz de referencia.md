---
tipo: meta
aliases:
  - IMAP - matriz
  - POP3 - matriz
  - imap pop3 cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# IMAP y POP3 - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puertos: IMAP 143** (STARTTLS) / **993** (IMAPS); **POP3 110** / **995** (POP3S). Los dos **leen** buzones — la contracara de [[SMTP - matriz de referencia]], que los envía. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `u`, `p` son marcadores. En IMAP cada comando lleva un **tag** al principio (`a`, `b`, …); en POP3 no.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nc -nv HOST 110` · `nc -nv HOST 143` | Banner y conversación cruda (sin cifrar) |
| `openssl s_client -connect HOST:993` · `HOST:995` | Igual pero sobre TLS (IMAPS / POP3S) |
| `nmap -sV --script 'pop3*,imap*' -p110,143,993,995 HOST` | Capacidades, mecanismos de auth y, en Exchange, info NTLM |

`CAPABILITY` (IMAP) / `CAPA` (POP3) listan qué auth soporta y si exige TLS.

## Comandos por protocolo

| Tarea | POP3 | IMAP |
|---|---|---|
| Login | `USER u` + `PASS p` | `a LOGIN u p` |
| Listar buzones | — (solo INBOX) | `a LIST "" "*"` |
| Seleccionar buzón | — | `a SELECT INBOX` |
| Estado / contar | `STAT` | `a STATUS INBOX (MESSAGES)` |
| Listar mensajes | `LIST` | `a FETCH 1:* (FLAGS)` |
| Leer un mensaje | `RETR n` | `a FETCH n BODY[]` |
| Buscar (¡oro!) | — | `a SEARCH SUBJECT "password"` |
| Borrar | `DELE n` | `a STORE n +FLAGS \Deleted` |
| Cerrar | `QUIT` | `a LOGOUT` |

La diferencia que importa en un pentest: **POP3 baja y (por defecto) borra, solo ve INBOX; IMAP deja todo en el server, con carpetas y `SEARCH`**. Con credenciales, `a SEARCH BODY "password"` sobre IMAP es la vía directa al loot.

## Autenticar sobre TLS
Cuando el plano está deshabilitado, se habla el protocolo dentro de la sesión TLS:

| Protocolo | Comando |
|---|---|
| IMAPS | `openssl s_client -connect HOST:993` (o `HOST:imaps`) → luego `a LOGIN u p` |
| POP3S | `openssl s_client -connect HOST:995` (o `HOST:pop3s`) → luego `USER u` / `PASS p` |

El nombre de servicio (`imaps`/`pop3s`) lo resuelve `openssl` por `/etc/services` — equivale al número de puerto.

## Con curl (una línea)

`curl` habla los cuatro protocolos por URL — más rápido que la sesión cruda para listar y bajar. `-k` salta la verificación del certificado (útil con el self-signed del lab).

| Tarea | Comando |
|---|---|
| Listar carpetas (IMAP) | `curl -k 'imaps://HOST' --user u:p` |
| Ver una carpeta | `curl -k 'imaps://HOST/INBOX?NEW' --user u:p` |
| Bajar un mensaje (IMAP) | `curl -k 'imaps://HOST/INBOX;UID=1' --user u:p` |
| Buscar (IMAP) | `curl -k 'imaps://HOST/INBOX' -X 'SEARCH SUBJECT "password"' --user u:p` |
| Listar mensajes (POP3) | `curl -k 'pop3s://HOST' --user u:p` |
| Bajar un mensaje (POP3) | `curl -k 'pop3s://HOST/1' --user u:p` |

Para el plano (sin TLS), cambiar `imaps`/`pop3s` por `imap`/`pop3`.


## Fuerza bruta

| Herramienta | Comando |
|---|---|
| hydra (POP3) | `hydra -L users.txt -P pass.txt pop3://HOST` |
| hydra (IMAP) | `hydra -L users.txt -P pass.txt imap://HOST` |
| nmap | `nmap --script pop3-brute -p110 HOST` |


## Configuración (con acceso al host)
Casi siempre Dovecot.

| Archivo | Qué tiene |
|---|---|
| `/etc/dovecot/dovecot.conf` | Config principal: protocolos, `mail_location` |
| `/etc/dovecot/conf.d/10-auth.conf` | `disable_plaintext_auth`, mecanismos |
| `/etc/dovecot/conf.d/10-ssl.conf` | `ssl` (required/no) y certificados |
| `/var/mail/<user>` · `/home/<user>/Maildir/` | Los buzones — correo en claro |


### Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| `disable_plaintext_auth = no` | Acepta `USER`/`PASS`/`LOGIN` en claro sin TLS → credenciales capturables en red |
| `ssl = no` | Todo el correo y la auth viajan sin cifrar |
| `auth_mechanisms = plain login` sin TLS | Igual que arriba: login en texto plano |


## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| IMAP: `a BAD command` | falta el tag al principio | anteponer un tag: `a LOGIN ...` |
| `NO [PRIVACYREQUIRED]` / login rechazado en claro | exige TLS | usar `openssl s_client` a 993/995 |
| POP3 `-ERR` al `PASS` | credencial mala, o buzón bloqueado por otra sesión | reintentar, verificar credencial |
| conexión pero sin banner | puerto TLS implícito | usar `openssl s_client`, no `nc` |

