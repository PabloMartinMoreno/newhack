---
tipo: tradecraft
clase: "[[CWE-942 - Permissive Cross-domain Policy with Untrusted Domains]]"
eje: validacion-del-origen
implementacion: "Registrar o construir un dominio que satisface la comparación de cadenas del servidor"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [validacion-por-prefijo-sufijo-o-subcadena, allow-credentials-true]
coste: medio
alternativas: ["[[CORS - reflejo del origen con credenciales]]", "[[CORS - null y comodín de subdominio]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - CORS substring bypass
  - suffix match
tags:
  - dominio/web
---

# CORS - validación por subcadena

## Cuándo lo elijo

Cuando el `Origin` inventado **no** se refleja —así que [[CORS - reflejo del origen con credenciales]] no aplica— pero el `Origin` legítimo sí se autoriza, y variantes cercanas al dominio también pasan. La señal es que el servidor devuelve el origen en la cabecera solo cuando contiene el nombre del dominio en alguna parte.

Es el paso siguiente cuando el reflejo ciego está cerrado pero la validación sigue siendo por cadena y no por comparación exacta.

## Por qué funciona

El servidor sí valida, pero valida mal: en vez de comparar el origen completo contra una lista, comprueba si **contiene**, **empieza con** o **termina con** el dominio. Cada una de las tres se rompe registrando un dominio que la satisface:

- **Sufijo** — `endsWith("objetivo.com")` acepta `atacanteobjetivo.com`, que es un dominio que se puede registrar.
- **Prefijo** — `startsWith("https://objetivo.com")` acepta `https://objetivo.com.atacante.com`, un subdominio del atacante.
- **Subcadena** — `contains("objetivo.com")` acepta cualquiera de los dos, y también `https://atacante.com?objetivo.com`.

Todas están en [[CORS bypass de origen - matriz de referencia]], y son las mismas que abusan [[OAuth - redirect_uri mal validado]] y [[CWE-601 - URL Redirection to Untrusted Site]] — la comparación de orígenes falla igual en los tres dominios, y el catálogo de payloads se comparte.

Confirmada la variante, el resto es idéntico a la rama del reflejo: la página del atacante hace `fetch` con `credentials:'include'` desde el dominio que pasa la validación, y lee la respuesta autenticada.

## Cómo falla

Falla contra comparación de origen completo. Ahí ninguna construcción de cadena sirve, porque `https://atacanteobjetivo.com` no es igual a `https://objetivo.com` aunque lo contenga.

Falla cuando la variante que pasa la validación **no se puede poseer**: si el único bypass es un prefijo que exige controlar `objetivo.com.algo`, y `objetivo.com` no delega subdominios al atacante, no hay dominio que registrar. El sufijo es el más explotable porque `atacanteobjetivo.com` está libre; el prefijo depende de conseguir un subdominio bajo el dominio real.

Y falla, como toda la familia, sin `Access-Control-Allow-Credentials`: se lee la respuesta pública y nada más.

## Coste

Medio, y el costo está en el dominio, no en las peticiones. Confirmar qué variante pasa son cinco peticiones con `Origin` construidos a mano. Explotarla puede exigir **registrar un dominio** —`atacanteobjetivo.com` para el caso del sufijo—, lo que cuesta dinero y deja rastro a nombre de alguien.

Por eso conviene confirmar primero cuál es la regla exacta de validación, y solo registrar el dominio cuando se sabe que la prueba de concepto lo va a necesitar. Muchas veces alcanza con demostrar el bypass usando la extensión del navegador que fuerza el `Origin`, sin llegar a registrar nada.

## Huella esperada

Igual que la rama del reflejo: la señal es una cabecera `Origin` que no corresponde, y depende de que se registre ese campo, cosa que por defecto no ocurre.

La diferencia sutil, y aprovechable del lado defensivo, es que acá el `Origin` malicioso **se parece** al dominio legítimo —`atacanteobjetivo.com`, `objetivo.com.evil.net`—. Una regla que compare el `Origin` contra la lista blanca real y alerte cuando un origen autorizado no está en ella tendría alta fidelidad, porque el ataque necesita un dominio parecido pero distinto. No existe esa detección en el vault porque la fuente no captura `Origin`; queda anotado como el mismo hueco de instrumentación que la rama anterior, en [[MOC - CORS]].

Durante la prueba, la ráfaga de `Origin` construidos contra la misma API es lo visible. El ataque final es una sola petición desde el dominio registrado.
