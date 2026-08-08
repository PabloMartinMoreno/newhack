---
tipo: tecnica
taxonomia: cwe
identificador: CWE-640
wstg: WSTG-ATHN-09
tacticas: []
aliases:
  - CWE-640
  - Recuperación de contraseña débil
  - password reset
tags:
  - dominio/web
---

# CWE-640 - Weak Password Recovery Mechanism for Forgotten Password

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Autenticación]]; la variante, en [[Autenticación - abuso de recuperación de contraseña]].

## Qué es

El mecanismo de recuperación permite tomar control de una cuenta sin conocer la credencial. Es, por definición, **un camino que evita la autenticación**: existe para eso.

## Por qué es el eslabón débil estructural

No por descuido, sino por su función. La recuperación tiene que funcionar para alguien que perdió lo único que probaba quién era, así que se apoya en algo más débil que la contraseña — el acceso a un correo, un número de teléfono, una respuesta memorable.

Eso la vuelve **la ruta más corta a una cuenta con MFA**: si la recuperación restablece la contraseña y además desactiva o salta el segundo factor, todo el esfuerzo puesto en el MFA se evita por diseño. Es lo primero que conviene mirar cuando el acceso principal está bien protegido.

## Dónde falla

- **El token es predecible.** Derivado de la marca de tiempo, secuencial, o con poca entropía. Si se puede generar el propio y observar el patrón, se generan los ajenos.
- **El token no expira, o no se invalida al usarse.** Un enlace de restablecimiento de hace seis meses que sigue funcionando es una llave permanente en la bandeja de entrada de la víctima — o de quien haya accedido a ella alguna vez.
- **El destino del envío lo controla el atacante.** El caso más grave: la petición de restablecimiento acepta un parámetro que decide a dónde va el enlace. Ver también la contaminación de la cabecera `Host`, donde el enlace se construye con el nombre de servidor que mandó el cliente.
- **El token no está atado a la cuenta.** Se pide para la cuenta propia y se usa para cambiar la de otro. Es [[CWE-639 - Authorization Bypass Through User-Controlled Key]] dentro del flujo de recuperación.
- **Preguntas de seguridad.** El nombre de la primera mascota es información pública o adivinable, y a diferencia de una contraseña no se puede rotar cuando se filtra.
- **La respuesta revela si la cuenta existe.** Ver [[CWE-204 - Observable Response Discrepancy]].

## La mitigación real

Token aleatorio de alta entropía, de un solo uso, con vida corta, atado a la cuenta y **enviado únicamente al destino registrado** — nunca a uno provisto en la petición. Invalidar todas las sesiones activas al completar el cambio, y exigir el segundo factor también acá, o el flujo entero es un rodeo alrededor del MFA.

## Referencias canónicas

- [CWE-640](https://cwe.mitre.org/data/definitions/640.html)
- [CWE-330](https://cwe.mitre.org/data/definitions/330.html) — valores insuficientemente aleatorios
- WSTG-ATHN-09
