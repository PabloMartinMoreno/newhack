---
tipo: tecnica
taxonomia: cwe
identificador: CWE-93
wstg: WSTG-INPV-16
tacticas: []
aliases:
  - CWE-93
  - email header injection
  - inyección en cabeceras de correo
  - SMTP injection
tags:
  - dominio/web
---

# CWE-93 - Improper Neutralization of CRLF Sequences

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Email header injection]]; las codificaciones y sinks en [[Email header inyección - matriz de referencia]]; los payloads en [[Email header impacto - matriz de referencia]].

## Qué es

La aplicación arma un correo —un formulario de contacto, un enlace de restablecimiento, una notificación— poniendo entrada del usuario en una **cabecera del mensaje** (`To`, `From`, `Subject`, `Reply-To`) sin filtrar el salto de línea. Como las cabeceras de un correo se separan con `\r\n`, igual que las de HTTP, inyectar esa secuencia agrega cabeceras propias: un destinatario oculto, un remitente falso, o un cuerpo entero.

Es la hermana de [[CWE-113 - Improper Neutralization of CRLF Sequences in HTTP Headers]] —la clase padre `CWE-93` es la misma inyección de CRLF—, con el sink cambiado: allá el `\r\n` estructura una respuesta HTTP, acá estructura un mensaje de correo. El átomo es idéntico, el impacto es de correo.

## Por qué el sink clásico es `mail()`

El caso emblemático es la función `mail()` de PHP y equivalentes, cuyo quinto parámetro son las **cabeceras adicionales**, construidas a menudo concatenando entrada del usuario:

```php
mail($to, $subject, $body, "From: " . $_POST['email']);
```

Si `email` lleva un `\r\n`, cierra la cabecera `From` y agrega las que el atacante quiera. Lo mismo pasa cuando `To` o `Subject` se arman con entrada, y en cualquier biblioteca que no escape los saltos de línea al serializar las cabeceras.

## Qué se consigue, en orden de impacto

| Inyección | Resultado |
|---|---|
| Un `Bcc:` a la víctima de un reset | Exfiltrar el correo de restablecimiento — toma de cuenta |
| Un `Bcc:`/`Cc:` a destinatarios arbitrarios | Relay de spam desde el dominio legítimo |
| Un `From:`/`Reply-To:` falso | Phishing con el remitente del objetivo |
| Un cuerpo o parte MIME | Reescribir el contenido del correo, adjuntar |

El primero conecta el dominio con la autenticación: si el formulario que inyecta es el de restablecimiento, un `Bcc` propio recibe una copia del correo de reset de **otra** cuenta, con su token. Es la contracara de [[Host header - envenenamiento del restablecimiento]] —aquel cambia el dominio del enlace, este se manda una copia del correo entero.

## Por qué la mitigación es filtrar el salto de línea

- **Rechazar** `\r` y `\n` en cualquier campo que vaya a una cabecera de correo —una dirección de correo válida no los contiene—.
- **Usar una biblioteca de correo** que serialice las cabeceras y las escape, en vez de concatenar en `mail()`.
- **Validar el formato** de las direcciones contra una expresión estricta antes de usarlas.
- Separar las cabeceras del cuerpo con una API, no con concatenación.

## Referencias canónicas

- [CWE-93](https://cwe.mitre.org/data/definitions/93.html)
- [CWE-113](https://cwe.mitre.org/data/definitions/113.html) — la hermana en HTTP
- WSTG-INPV-16
- OWASP — Testing for IMAP/SMTP Injection
