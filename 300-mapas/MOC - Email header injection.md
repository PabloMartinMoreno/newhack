---
tipo: moc
dominio: web
aliases:
  - MOC email header
tags:
  - dominio/web
---

# MOC - Email header injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-93 - Improper Neutralization of CRLF Sequences]]. Las codificaciones y sinks, en [[Email header inyección - matriz de referencia]]. Acá vive **la decisión**.

Es la hermana de [[MOC - CRLF injection]] con el sink cambiado: el mismo átomo `\r\n`, que allá estructura una respuesta HTTP, acá estructura un mensaje de correo. La clase padre `CWE-93` es la misma inyección de CRLF; lo que cambia es que el destino son cabeceras de correo y el impacto es de correo —exfiltración, spam, phishing—.

| Eje | Valores |
|---|---|
| Alcance | una cabecera de correo (`\r\n`) · el cuerpo/MIME (`\r\n\r\n`) |
| Objetivo | destinatario (`Bcc`/`Cc`) · identidad (`From`) · cuerpo |
| Sink | `mail()` de PHP · biblioteca sin escape · SMTP a mano → matriz |
| Impacto | exfil de reset · spam · phishing · malware MIME |

**El alcance es el eje raíz**, igual que en CRLF: un `\r\n` agrega una cabecera —un destinatario, un remitente falso—, un `\r\n\r\n` llega al cuerpo. La codificación y el sink van a matriz.

## Árbol de decisión — qué alcance y qué objetivo

```
¿Un campo del formulario va a una cabecera de correo?  → [[Email header inyección - matriz de referencia]] § 1
├─ Cae en el cuerpo, no en cabecera → inyección de cuerpo directa, sin CRLF
└─ Cae en una cabecera — inyectá %0d%0aBcc: propio y esperá la copia
   │
   ├─ ¿El objetivo es exfiltrar o hacer spam?
   │     → [[Email header - inyección de destinatarios]]   ← PRIMERO
   │       Bcc en el reset = token de otra cuenta; Bcc masivo = spam
   │
   ├─ ¿Falsificar el remitente o reescribir el cuerpo?
   │     → [[Email header - falsificación y cuerpo]]
   │       From prestado + doble \r\n para el cuerpo
   │
   └─ ¿El To es fijo pero controlo Subject/From?
         → misma nota: no hay destinatarios de más, sí falsificación
```

Tres cosas que este orden codifica:

**La inyección de destinatarios va primero porque tiene el mayor impacto barato.** Un `Bcc` en el flujo de reset exfiltra el token de otra cuenta —toma de cuenta— con una petición. La falsificación de identidad es más laboriosa y depende de SPF/DKIM.

**El `Bcc` en el reset es la joya del dominio.** Conecta con la autenticación por un vector distinto del de [[Host header - envenenamiento del restablecimiento]]: aquel cambia el dominio del enlace y espera que la víctima haga clic; este se manda una copia del correo entero y no depende de nada que haga la víctima. Los dos atacan el mismo flujo de reset desde ángulos opuestos.

**SPF/DKIM/DMARC limitan el phishing por `From` falso.** Es una defensa fuera de la aplicación que hay que verificar antes de vender el hallazgo: aunque se inyecte el `From`, el correo puede terminar en spam si el dominio firma sus correos.

## Árbol de decisión — qué consigo

```
¿Qué inyecté?
├─ Bcc en el reset → token de la víctima → toma de cuenta → [[MOC - Autenticación]]
├─ Bcc masivo → relay de spam desde el dominio del objetivo
├─ From falso + cuerpo → phishing con identidad prestada (ojo SPF/DKIM)
└─ MIME con adjunto → malware que evade filtros de la parte de texto
```

## Cheatsheets — entrada directa

- [[Email header inyección - matriz de referencia]] — Confirmar, sinks (`mail()`, SMTP), dónde cae, codificaciones, cabeceras a inyectar
- [[Email header impacto - matriz de referencia]] — Exfil de reset, spam, `From` falso, cuerpo, MIME, por impacto

## Orden de aprendizaje

1. [[CWE-93 - Improper Neutralization of CRLF Sequences]] — el mismo átomo que CRLF, otro sink
2. [[Email header - inyección de destinatarios]] — el caso base, el `Bcc` y la exfil de reset
3. [[Email header - falsificación y cuerpo]] — el escalón: identidad y cuerpo

## Relación con otros dominios

- [[MOC - CRLF injection]] — la hermana directa, el mismo `\r\n`. Allá el sink es una respuesta HTTP, acá un correo. La clase padre `CWE-93` es común; `CWE-113` es la variante HTTP. Las codificaciones y el árbol de alcance son idénticos.
- [[MOC - Host header]] — [[Host header - envenenamiento del restablecimiento]] y [[Email header - inyección de destinatarios]] atacan el mismo flujo de reset desde ángulos opuestos: uno el dominio del enlace, otro una copia del correo.
- [[MOC - Autenticación]] — el `Bcc` en el reset comparte objetivo con [[Autenticación - abuso de recuperación de contraseña]], `CWE-640`: recuperar la cuenta ajena, acá por exfiltración del correo.
- [[MOC - Cross-site scripting]] — el cuerpo HTML inyectado es phishing, no XSS, pero comparte la idea de contenido controlado en un canal confiable.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Inyección de destinatarios | [[Registro del WAF]] · [[Log de acceso del servidor web]] | `%0d%0a` + `Bcc:`/`Cc:`/`To:` en un campo de correo |
| Falsificación y cuerpo | [[Registro del WAF]] | `%0d%0a` + `From:`/`Content-Type:` en un campo |
| El correo enviado | — | **Ningún artefacto de correo modelado** |

Dos observaciones:

**La firma de la petición es escribible; el correo es un hueco de fuente.** El campo de correo con un `\r\n` seguido de un nombre de cabecera —`Bcc:`, `From:`— es una firma inconfundible sobre la petición, que ve el WAF y el log de acceso. Pero el **impacto** —el correo con el destinatario o el remitente de más— no lo ve ninguna fuente del vault: no hay artefacto de telemetría del servidor de correo modelado. Si el servidor de correo registrara los destinatarios y las cabeceras, un `Bcc` inyectado sería visible; queda como un hueco de fuente propio, distinto de los demás porque la fuente no es web sino el MTA.

**Consolida el candidato de firma transversal, ahora sobre dos sinks.** El `\r\n` codificado seguido de un nombre de cabecera —HTTP en [[MOC - CRLF injection]], de correo acá— es el mismo patrón. Con las cuatro hermanas de inyección, el Host, el CRLF y ahora el correo, el candidato de una regla de firma de metacaracteres de estructura en la entrada cubre siete dominios. El `\r\n` + nombre de cabecera es un sub-patrón limpio de ese candidato.

Vigésimo dominio cerrado sin detección nueva.

## Huecos conocidos

- [x] Los dos alcances — cabecera de correo y cuerpo/MIME
- [x] Sinks, codificaciones y payloads de impacto — dos matrices
- [x] Cara azul de firma sobre la petición — escribible
- [ ] **El servidor de correo no está modelado como fuente.** El impacto —destinatarios, remitente, cuerpo inyectados— solo se vería en el MTA, que el vault no modela. Hueco de fuente distinto: no es web, es correo
- [ ] IMAP injection —inyección en los comandos de un webmail que habla IMAP— como superficie propia, más rara
- [ ] La firma `\r\n` + nombre de cabecera es el sub-patrón de correo del candidato transversal de inyección
