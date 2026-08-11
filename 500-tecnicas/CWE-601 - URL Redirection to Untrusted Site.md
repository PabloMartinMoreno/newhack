---
tipo: tecnica
taxonomia: cwe
identificador: CWE-601
wstg: WSTG-CLNT-04
tacticas: []
aliases:
  - CWE-601
  - open redirect
  - redirección abierta
tags:
  - dominio/web
---

# CWE-601 - URL Redirection to Untrusted Site

> [!note] Nota paraguas
> Sin contenido operativo. Su uso como primitiva vive en [[MOC - OAuth]]; los payloads, en [[OAuth redirect_uri - matriz de referencia]].

## Qué es

La aplicación redirige al usuario a una dirección que él mismo controla. Sola, la severidad es baja: sirve para dar credibilidad a un enlace de phishing y poco más.

Lo que la hace interesante es que **es una primitiva, no un fin**. Su valor real aparece cuando algo se transporta en la redirección.

## Por qué está acá y no en una nota suelta

Este vault no la modela como hallazgo independiente sino como el eslabón que hace explotables otras cosas. Tres usos, en orden de impacto:

| Qué transporta la redirección | Qué se consigue |
|---|---|
| Un código de autorización de OAuth | La cuenta de la víctima — ver [[OAuth - redirect_uri mal validado]] |
| Un token en el fragmento de la URL | Lo mismo, sin siquiera pasar por el servidor del cliente |
| La cabecera `Referer` con un secreto adentro | Fuga de tokens de restablecimiento o de sesión |

El primero es el que la convierte en crítica. En OAuth, el servidor de autorización manda el código a la dirección que le pidieron; si el cliente acepta una dirección arbitraria —o una que redirige a otro lado—, el código termina en el servidor del atacante y con él se obtiene la cuenta.

Es el mismo patrón que hace a [[Path traversal]] importante: leer un archivo no es gran cosa hasta que el archivo es la clave de firma.

## Por qué la validación falla tanto

Comparar direcciones es más difícil de lo que parece, y las tres formas de hacerlo mal aparecen en producción con la misma frecuencia:

- **Por subcadena.** `startsWith` sin anclar acepta `https://objetivo.com.atacante.com`; `contains` acepta cualquier cosa con el dominio adentro.
- **Por prefijo de ruta.** Aceptar todo lo que empiece con la ruta registrada permite recorrerla hacia arriba, o colgar un segundo esquema detrás.
- **Confiando en el parseo del navegador.** Las barras invertidas, las arrobas, los caracteres de control y la codificación doble se resuelven distinto en cada analizador. La comparación se hace sobre una cadena y la navegación sobre otra.

La mitigación correcta es una **lista blanca de direcciones completas**, comparadas exactas, sin comodines y sin partes variables. En OAuth eso está en la especificación desde el principio y se incumple igual.

## Referencias canónicas

- [CWE-601](https://cwe.mitre.org/data/definitions/601.html)
- WSTG-CLNT-04
- RFC 6749 § 3.1.2 — el registro de la dirección de redirección
- RFC 9700 — buenas prácticas de seguridad para OAuth 2.0
