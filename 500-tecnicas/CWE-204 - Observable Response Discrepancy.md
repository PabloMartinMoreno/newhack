---
tipo: tecnica
taxonomia: cwe
identificador: CWE-204
wstg: WSTG-IDNT-04
tacticas: []
aliases:
  - CWE-204
  - Enumeración de usuarios
  - user enumeration
tags:
  - dominio/web
---

# CWE-204 - Observable Response Discrepancy

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Autenticación]]; la variante, en [[Autenticación - enumeración de usuarios]].

## Qué es

La aplicación responde de forma **distinguible** según si un dato existe o no, y con eso confirma su existencia a quien no debería poder saberlo. En autenticación, el dato es la cuenta.

## Por qué importa aunque parezca menor

Sola, no es gran cosa: saber que una dirección de correo está registrada no da acceso a nada. Su valor es de **multiplicador**, y por eso se busca primero.

Convierte [[Autenticación - password spraying]] de un ataque a ciegas contra un espacio enorme en uno dirigido contra una lista corta de cuentas confirmadas. La diferencia práctica es de órdenes de magnitud: cien mil intentos contra usuarios inventados, o doscientos contra usuarios reales. Lo segundo pasa por debajo de casi cualquier control de ritmo; lo primero no.

También alimenta [[Autenticación - abuso de recuperación de contraseña]] y, fuera del dominio, cualquier ataque que necesite saber a quién apuntar.

## Dónde aparece

No solo en el formulario de acceso, y esa es la clave: **la aplicación tiene que ser consistente en todos los puntos donde toca la lista de cuentas**. Alcanza con que uno filtre.

Los cuatro habituales: el acceso, el registro —"ese correo ya está en uso"—, la recuperación de contraseña, y cualquier flujo de invitación o de compartir.

## Los tres oráculos

- **Mensaje distinto.** "Usuario no encontrado" contra "contraseña incorrecta". El caso obvio, y el que casi todos arreglaron.
- **Tiempo distinto.** El que casi nadie arregla. Si el usuario no existe la aplicación responde de inmediato; si existe, calcula el hash de la contraseña antes de rechazarla, y eso lleva cientos de milisegundos deliberados. La diferencia es medible y es la misma idea de [[La latencia como canal de datos]].
- **Comportamiento distinto.** Códigos de estado, redirecciones, cabeceras, longitud de respuesta, o que el control de ritmo se aplique solo a cuentas reales.

## La mitigación real

Respuesta idéntica en contenido, código y **tiempo** para los dos casos. El tiempo obliga a calcular el hash siempre, incluso contra un hash falso cuando la cuenta no existe — es contraintuitivo y es la parte que suele faltar.

En registro y recuperación, la respuesta correcta no es un mensaje distinto sino el mismo mensaje neutro con la información yendo por correo: "si la cuenta existe, te escribimos".

## Referencias canónicas

- [CWE-204](https://cwe.mitre.org/data/definitions/204.html)
- [CWE-208](https://cwe.mitre.org/data/definitions/208.html) — discrepancia por tiempo
- WSTG-IDNT-04
