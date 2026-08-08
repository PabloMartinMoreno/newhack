---
tipo: tecnica
taxonomia: cwe
identificador: CWE-384
wstg: WSTG-SESS-03
tacticas: []
aliases:
  - CWE-384
  - Session fixation
  - Fijación de sesión
tags:
  - dominio/web
---

# CWE-384 - Session Fixation

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Gestión de sesión]]; la variante, en [[Sesión - fijación]].

## Qué es

La aplicación **no cambia el identificador de sesión al autenticar**. El atacante fija un identificador conocido en el navegador de la víctima antes de que entre; cuando la víctima se autentica, ese mismo identificador queda asociado a su cuenta, y el atacante ya lo tiene.

## Por qué es distinta del robo de sesión

En el robo, el atacante **obtiene** un token que ya existe. Acá lo **provee** de antemano, y por eso no necesita robar nada: espera a que la víctima le agregue valor autenticándose.

La consecuencia práctica es que las defensas contra el robo no aplican. `HttpOnly` protege el token de un XSS; no impide que el atacante ponga un token que él eligió. Es un ataque sobre el ciclo de vida del identificador, no sobre su confidencialidad.

## Por qué existe

Porque emitir el identificador antes de autenticar es cómodo: la aplicación necesita estado desde la primera visita —para el carrito, el idioma, el token anti-CSRF— y lo natural es crear la sesión ahí y reutilizarla cuando el usuario entra.

Reutilizarla es exactamente el fallo. La sesión anónima y la autenticada tienen que ser identificadores distintos, y el momento de la autenticación es la frontera.

## Cómo se fija el identificador

Depende de qué acepte la aplicación, y el orden refleja lo que sigue siendo viable:

- **Parámetro en la URL.** Si acepta el identificador por query string, el enlace enviado a la víctima lo fija. Es el caso clásico y hoy es raro.
- **Escritura de cookie desde un subdominio.** Un subdominio comprometido o de terceros puede escribir cookies para el dominio padre. Es la vía más realista hoy, y la razón por la que los subdominios son parte del perímetro.
- **Vía XSS**, aunque con XSS ya se puede leer el token directamente y este camino sobra.
- **Encabezado o campo aceptado por la aplicación**, en implementaciones propias de manejo de sesión.

## La mitigación real

**Regenerar el identificador en cada cambio de nivel de privilegio**: al autenticar, al elevar permisos, al cambiar de cuenta. Una línea en casi todos los marcos de trabajo, y cierra la clase entera.

Complementos: no aceptar identificadores de sesión por URL, y no aceptar identificadores que el servidor no haya emitido — si llega uno desconocido, se descarta y se emite uno nuevo en vez de adoptarlo.

## Referencias canónicas

- [CWE-384](https://cwe.mitre.org/data/definitions/384.html)
- WSTG-SESS-03
