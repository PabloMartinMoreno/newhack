---
tipo: teoria
habilita: ["[[Kerberoasting]]", "[[AS-REP roasting]]", "[[Golden ticket]]", "[[Pass-the-ticket]]", "[[MOC - AD delegaciones]]"]
relacionadas: ["[[Windows - proceso de autenticación]]", "[[NTLM - desafío y respuesta]]"]
aliases:
  - Kerberos
  - TGT
  - TGS
  - KDC
tags: []
---

# Kerberos - el flujo de tickets

## Cómo funciona

Tres actores: el **cliente**, el **KDC** (Key Distribution Center, que corre en el DC y tiene dos mitades, AS y TGS) y el **servicio**. La gracia: el cliente prueba quién es **una vez** y después usa tickets, sin reenviar la contraseña.

1. **AS-REQ / AS-REP** — el cliente pide un TGT al AS. La **preautenticación** es un timestamp cifrado con la clave del usuario (derivada de su contraseña): si el AS lo descifra, sos vos. Devuelve un **TGT** cifrado con la clave de la cuenta **krbtgt**, más una session key.
2. **TGS-REQ / TGS-REP** — el cliente presenta el TGT y pide un ticket para un servicio puntual (por su **SPN**). El TGS devuelve un **service ticket** cifrado con la clave de **la cuenta del servicio**.
3. **AP-REQ** — el cliente presenta el service ticket al servicio, que lo descifra con **su propia clave**. El servicio **no consulta al KDC**: confía en que solo el KDC pudo haberlo cifrado.

Dentro de cada ticket viaja el **PAC**: los SIDs y grupos del usuario, o sea la autorización.

## Dónde el diseño abre superficie

Cada "cifrado con la clave de X" es una palanca:

- **Preauth es opcional por cuenta.** Si una cuenta la tiene deshabilitada, cualquiera pide un AS-REP y obtiene material cifrado con la clave de esa cuenta → crackeable offline.
- **El service ticket se cifra con el hash de la cuenta de servicio.** Pedir un TGS de un SPN y crackearlo offline recupera esa contraseña **sin tocar la cuenta ni autenticarse al servicio**.
- **El TGT se cifra con el hash de krbtgt.** Quien tenga el hash de krbtgt forja TGTs arbitrarios, con el PAC que quiera.
- **El servicio valida sin el KDC.** Quien tenga la clave de un servicio forja service tickets para ese servicio (sin pasar por el TGS).
- **RC4 sigue soportado.** Un etype RC4 es mucho más rápido de crackear que AES.

## Qué habilita

- Preauth opcional → [[AS-REP roasting]].
- Service ticket cifrado con el hash del servicio → [[Kerberoasting]].
- Hash de krbtgt → [[Golden ticket]] (TGT forjado; persistencia de todo el dominio).
- Hash de un servicio → silver ticket (service ticket forjado) — sin nota propia aún.
- Tickets en memoria reutilizables → [[Pass-the-ticket]].
- Reenvío / S4U del TGT → [[MOC - AD delegaciones]].

## Cómo se ve en la práctica

El pedido es la ventana observable (el crackeo es offline y mudo): la AS-REQ queda en [[Windows 4768 - Kerberos TGT requested]] —preauth en cero delata AS-REP roasting—; la TGS-REQ en [[Windows 4769 - Kerberos service ticket requested]] —etype RC4 en volumen delata Kerberoasting—. Un golden ticket se nota porque pide servicios sin un `4768` previo. Dónde viven los tickets y por qué LSASS los tiene, en [[Windows - proceso de autenticación]].

## Fuente

- RFC 4120 (Kerberos V5) · MS-KILE (implementación de Microsoft, PAC incluido).
