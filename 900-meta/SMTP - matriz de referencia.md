---
tipo: meta
aliases:
  - SMTP - matriz
  - smtp cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# SMTP - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puertos: 25** (SMTP servidor-a-servidor y legacy), **587** (submission, con auth y STARTTLS) y **465** (SMTPS, TLS implícito). Recon y abuso del servicio de correo. La inyección de cabeceras en una app web es otra cosa: [[MOC - Email header injection]]. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST` es el objetivo; `dom` el dominio de correo. Muchos pasos se hacen hablando el protocolo crudo con `nc HOST 25`.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nc -nv HOST 25` · `telnet HOST 25` | Banner y conversación cruda |
| `nmap -sV --script "smtp-commands,smtp-open-relay,smtp-enum-users,smtp-ntlm-info" -p25,465,587 HOST` | Comandos soportados, relay abierto, usuarios y, en Exchange, info NTLM |

`smtp-commands` lista qué acepta el server (`VRFY`, `EXPN`, `AUTH`, `STARTTLS`) — decide el resto.

## Comandos del protocolo

Escritos a mano dentro de `nc HOST 25`:

| Comando | Qué hace |
|---|---|
| `EHLO host` | Saludo; lista extensiones (`AUTH`, `STARTTLS`, `SIZE`). `HELO` es la versión vieja |
| `MAIL FROM:<a@dom>` | Remitente del sobre |
| `RCPT TO:<b@dom>` | Destinatario; `250` acepta, `550` rechaza |
| `DATA` | Empieza el cuerpo; termina con un `.` solo en una línea |
| `VRFY user` | ¿Existe el usuario? |
| `EXPN lista` | Expande una lista o alias a sus miembros |
| `RSET` · `QUIT` | Reiniciar la transacción · cerrar |

## Enumeración de usuarios

El uso ofensivo clásico: sacar cuentas válidas para spray o phishing.

| Método | Comando |
|---|---|
| VRFY (en la sesión) | `VRFY root` → `250` existe, `550` no |
| EXPN (en la sesión) | `EXPN administrator` |
| RCPT TO (el más fiable) | `MAIL FROM:<a@a>` y luego `RCPT TO:<user>` — `250` = existe |
| smtp-user-enum | `smtp-user-enum -M VRFY -U users.txt -t HOST` |
| smtp-user-enum (RCPT) | `smtp-user-enum -M RCPT -U users.txt -D dom -t HOST` |
| nmap | `nmap --script smtp-enum-users -p25 HOST` |

`RCPT TO` funciona aunque `VRFY`/`EXPN` estén deshabilitados, porque el server igual acepta o rechaza destinatarios.

## Open relay — reenviar correo ajeno

Un server que acepta `MAIL FROM` y `RCPT TO` **ambos externos** es un relay abierto: spam y spoofing.

| Método | Comando |
|---|---|
| nmap | `nmap --script smtp-open-relay -p25 HOST` |
| Manual | `MAIL FROM:<a@externo.com>` + `RCPT TO:<b@otro-externo.com>` → si acepta, es relay |
| swaks | `swaks --server HOST --to b@externo.com --from a@externo.com` |

## Enviar correo (spoofing / phishing)

| Herramienta | Comando |
|---|---|
| swaks | `swaks --to victima@dom --from jefe@dom --server HOST --header "Subject: RRHH" --body "click"` |
| swaks + adjunto | `swaks ... --attach @payload.doc` |
| swaks + auth | `swaks ... --auth LOGIN --auth-user u --auth-password p` |
| Manual | conversación `EHLO`/`MAIL FROM`/`RCPT TO`/`DATA` por `nc` |

`swaks` es la navaja del correo: arma toda la conversación por vos y sirve para probar relay, auth y spoofing.

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `/etc/postfix/main.cf` | Postfix: `mynetworks`, `relayhost`, restricciones de relay |
| `/etc/postfix/master.cf` | Servicios y puertos de Postfix |
| `/etc/aliases` · `/etc/postfix/virtual` | Alias y redirecciones — nombres reales de cuentas |
| `/etc/exim4/` · `/etc/mail/sendmail.cf` | Config de Exim / sendmail |
| `/var/mail/<user>` · `/var/spool/mail/` | Los buzones — correo en claro |

### Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| `mynetworks = 0.0.0.0/0` (Postfix) | Confía en todo internet → relay abierto |
| Falta `reject_unauth_destination` en `smtpd_recipient_restrictions` | Habilita el relay |
| `disable_vrfy_command = no` | Deja `VRFY` activo → enumeración de usuarios |
| Exim viejo (`< 4.92`) | Familia de RCE en el parser (CVE-2019-10149 y otros) — fuera del alcance de esta matriz |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `502 VRFY disabled` | `VRFY` apagado | usar `RCPT TO`, que casi siempre responde |
| `550 relay not permitted` | no es open relay (lo normal) | probar con remitente/destino locales, o autenticar |
| `530 Authentication required` | 587 exige auth | `AUTH LOGIN`, o usar el 25 |
| conexión pero sin banner | STARTTLS/implícito | probar 465 con TLS (`openssl s_client -connect HOST:465`) |
