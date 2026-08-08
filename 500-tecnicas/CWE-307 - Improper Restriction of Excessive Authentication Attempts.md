---
tipo: tecnica
taxonomia: cwe
identificador: CWE-307
wstg: WSTG-ATHN-04
tacticas: []
aliases:
  - CWE-307
  - Sin límite de intentos
  - brute force
tags:
  - dominio/web
---

# CWE-307 - Improper Restriction of Excessive Authentication Attempts

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Autenticación]]; las variantes, en [[Autenticación - password spraying]] y [[Autenticación - credential stuffing]].

## Qué es

La aplicación permite intentar credenciales sin un límite efectivo. "Efectivo" hace el trabajo pesado de la definición: casi todas las aplicaciones tienen **algún** límite, y casi todos están puestos en el eje equivocado.

## El error de diseño, no la ausencia

El control habitual cuenta intentos fallidos **por cuenta**: cinco errores y se bloquea. Detiene la fuerza bruta clásica —un usuario, muchas contraseñas— y no detiene nada más.

No detiene [[Autenticación - password spraying]], que prueba **una** contraseña contra miles de cuentas: cada cuenta recibe un solo intento fallido y ningún contador se acerca al umbral. Tampoco detiene [[Autenticación - credential stuffing]], donde la mayoría de los intentos aciertan a la primera porque la contraseña es la correcta, filtrada de otro sitio.

Por eso el hallazgo casi nunca es "no hay límite". Es **"el límite está en el eje equivocado"**, y conviene escribirlo así en el informe o se cierra agregando un contador que ya existía.

## Qué sí funciona

Limitar por **origen** además de por cuenta: intentos fallidos por dirección IP, por rango, por huella de cliente. Y sobre todo, alertar por la **tasa global de fallos** de la aplicación — un ataque de spraying es invisible cuenta por cuenta y evidentísimo en el agregado.

El complemento que cambia el resultado no es un límite: es un segundo factor. Con MFA bien implementado, la credencial correcta no alcanza, y todo este eje pasa de crítico a moderado.

## Por qué el bloqueo de cuenta es una mitigación con doble filo

Bloquear una cuenta tras N fallos convierte el ataque de credenciales en un ataque de **denegación de servicio**: un atacante bloquea a todos los usuarios de la organización a propósito, sin adivinar una sola contraseña.

Es una decisión de diseño real, no un detalle. El retraso progresivo y el CAPTCHA logran el mismo objetivo sin regalar ese poder.

## Referencias canónicas

- [CWE-307](https://cwe.mitre.org/data/definitions/307.html)
- [CWE-799](https://cwe.mitre.org/data/definitions/799.html) — control de frecuencia en general
- WSTG-ATHN-04
