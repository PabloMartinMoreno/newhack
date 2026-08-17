---
tipo: tradecraft
clase: "[[CWE-93 - Improper Neutralization of CRLF Sequences]]"
eje: alcance
implementacion: "Inyectar un From/Reply-To falso, o un doble \\r\\n que reescribe el cuerpo y las partes MIME del correo"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]"]
requisitos: [entrada-en-una-cabecera-de-correo-sin-filtrar]
coste: medio
alternativas: ["[[Email header - inyección de destinatarios]]", "[[XSS - almacenado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - From spoofing
  - MIME injection
  - inyección de cuerpo de correo
tags:
  - dominio/web
---

# Email header - falsificación y cuerpo

## Cuándo lo elijo

Cuando la inyección de CRLF en el correo está confirmada y el objetivo es **falsificar el remitente** o **reescribir el contenido** del mensaje, no agregar destinatarios. Se elige cuando el `To` es fijo —así que [[Email header - inyección de destinatarios]] no aplica— pero se controla otra cabecera, o cuando el impacto buscado es phishing en vez de exfiltración.

Es el escalón de mayor control del dominio: con un doble `\r\n` se pasa de las cabeceras al cuerpo, y se escribe el correo entero.

## Por qué funciona

Dos niveles, paralelos a la inyección de cabecera y la división de respuesta de [[MOC - CRLF injection]]:

**Falsificar cabeceras de identidad.** Inyectar un `From:` o `Reply-To:` propio hace que el correo parezca venir del dominio del objetivo o responder a una dirección del atacante:

```
email = x%0d%0aFrom: soporte@objetivo.com%0d%0aReply-To: atacante@evil.com
```

El correo llega con el remitente del objetivo —que pasa los filtros de reputación del dominio— y las respuestas van al atacante. Es phishing con la identidad prestada del objetivo, mucho más creíble que uno desde un dominio ajeno.

**Reescribir el cuerpo.** Un doble `\r\n` cierra las cabeceras y empieza el cuerpo del correo, igual que en la división de respuesta HTTP:

```
email = x%0d%0aContent-Type: text/html%0d%0a%0d%0a<h1>Contenido del atacante</h1>
```

Con esto el atacante controla el HTML que ve el destinatario —una página de phishing dentro de un correo legítimo del objetivo—. Y con `Content-Type: multipart` puede inyectar **partes MIME**: un adjunto malicioso, o un cuerpo alternativo que los filtros no inspeccionan.

Las construcciones —falsificación, cuerpo, MIME— están en [[Email header impacto - matriz de referencia]].

## Cómo falla

Falla contra el mismo filtro que la otra rama —rechazar `\r\n`—, y además contra los que permiten un salto pero bloquean el doble, específicamente contra la inyección de cuerpo.

Falla cuando el `From` lo fija el servidor con una dirección autenticada —lo correcto—, de modo que el remitente no sale de la entrada.

Y el phishing por `From` falso falla contra SPF/DKIM/DMARC bien configurados: aunque se inyecte el `From`, el correo puede terminar en spam o rechazado si el dominio del objetivo firma sus correos y el servidor de envío no está autorizado. Es una capa de defensa fuera de la aplicación que conviene verificar antes de vender el hallazgo como phishing efectivo.

## Coste

Medio. La falsificación de `From` es una petición. La inyección de cuerpo y MIME es más delicada —hay que cerrar bien las cabeceras y armar las partes para que el cliente de correo las renderice—, con varios intentos ajustando el `Content-Type` y los límites de las partes.

El costo de reconocimiento es entender qué campo controla qué cabecera, y si el `From` es inyectable o fijo.

## Huella esperada

Firma sobre la petición, la más gruesa del dominio:

- El campo lleva **`%0d%0a` seguido de `From:`, `Content-Type:`, o `%0d%0a` repetido** —nombres de cabecera de correo o estructura MIME en un campo de entrada—, una firma inconfundible que ve [[Registro del WAF]] y [[Log de acceso del servidor web]] si viaja en la query. Es la misma familia que [[CRLF - división de respuesta]], con el sink de correo.
- El impacto —el correo falsificado— no lo ve el vault, mismo hueco de fuente que la otra rama: no hay artefacto de telemetría del servidor de correo. La detección aprovechable es la firma de la petición.

Refuerza, con la rama de destinatarios y con las dos de CRLF, el candidato transversal de una detección de firma de metacaracteres de estructura en la entrada: el `\r\n` codificado seguido de un nombre de cabecera —HTTP o de correo— es el patrón común. Anotado en [[MOC - Email header injection]].
