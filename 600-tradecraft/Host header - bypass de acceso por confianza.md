---
tipo: tradecraft
clase: "[[CWE-290 - Authentication Bypass by Spoofing]]"
eje: uso-del-host
implementacion: "Falsificar el Host o una cabecera de reenvío que la aplicación usa para decidir acceso o confianza"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [decisión-de-acceso-basada-en-una-cabecera-del-cliente]
coste: bajo
alternativas: ["[[Host header - SSRF por enrutamiento]]", "[[Control de acceso - escalada vertical]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - X-Forwarded-For bypass
  - trusted header bypass
tags:
  - dominio/web
---

# Host header - bypass de acceso por confianza

## Cuándo lo elijo

Cuando la aplicación decide algo de seguridad —conceder acceso a `/admin`, saltar autenticación, tratar la petición como interna— mirando una cabecera que el cliente controla: el `Host`, o una de reenvío como `X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Host`. Se reconoce cuando un recurso restringido responde distinto según esas cabeceras.

Es la rama que abusa la **confianza** en la cabecera, no el enrutamiento ni la construcción de enlaces. Se elige cuando el reconocimiento muestra que un control depende de un valor que el atacante puede poner.

## Por qué funciona

Un proxy inverso agrega cabeceras de reenvío para decirle a la aplicación de dónde vino la petición, y la aplicación las lee como verdad. El error es no distinguir las que agregó el proxy de las que **trajo el cliente**: si la aplicación confía en `X-Forwarded-For` para saber la IP de origen, el atacante la falsifica.

Los patrones que rinden:

- **Acceso interno spoofeado.** El panel admin se restringe a "IP interna" y se comprueba con `X-Forwarded-For: 127.0.0.1` o `Host: localhost`. Poner esa cabecera concede el acceso.
- **Bypass de límite de tasa o de bloqueo por IP.** Rotar `X-Forwarded-For` hace parecer que cada intento viene de una IP distinta, anulando el conteo — se cruza con [[Autenticación - password spraying]].
- **Confianza en el `Host` para autorizar.** Algunas apps tratan `Host: localhost` o el dominio interno como sesión privilegiada.
- **Inyección en cabeceras de seguridad derivadas del Host**, cuando el `Host` se refleja en una decisión.

El catálogo de cabeceras de reenvío y dónde se confía en cada una está en [[Host header cabeceras de confianza - matriz de referencia]]. Es exactamente [[CWE-290 - Authentication Bypass by Spoofing]]: falsificar un dato que la aplicación toma por confiable.

## Cómo falla

Falla cuando la aplicación **no decide acceso por cabeceras del cliente**: la identidad y la autorización van por la sesión. Es la mitigación de fondo.

Falla cuando el proxy **sobrescribe** las cabeceras de reenvío —borrando las que trajo el cliente— antes de reenviar, de modo que la aplicación solo ve las del proxy. Es la configuración correcta y la que hay que verificar en el informe.

Y falla cuando el control real está en otra capa —una lista de IP a nivel de red, no de aplicación— que la cabecera no toca.

## Coste

Bajo, el más bajo del dominio. Probar el bypass es agregar una cabecera y ver si el recurso restringido responde. `X-Forwarded-For: 127.0.0.1` contra `/admin` es una petición.

El reconocimiento es igual de barato: probar el catálogo de cabeceras de reenvío contra los recursos restringidos y ver cuál cambia el resultado. La mayor parte del trabajo es saber qué recursos vale la pena probar.

## Huella esperada

Firma escribible y de alta fidelidad para algunos casos:

- Una petición con **`X-Forwarded-For: 127.0.0.1` o `Host: localhost` que llega desde afuera** es contradictoria por definición: si de verdad viniera de localhost no habría cruzado el perímetro. Es una firma tan limpia como el `Origin: null` de [[CORS - null y comodín de subdominio]], y la ve [[Log de acceso del servidor web]] si registra esas cabeceras. Detectar la contradicción —cabecera de origen interno en tráfico externo— es candidato a detección propia.
- El acceso concedido queda en [[Log de auditoría de la aplicación]] como acción de rol elevado, con el perfil de [[Cambio de privilegio fuera del flujo administrativo]], si el log registra el acceso al recurso restringido.

El bypass de límite de tasa por rotación de `X-Forwarded-For` es el más difícil de ver: cada intento parece de una IP distinta, así que las reglas de fuerza bruta por IP —como [[Fallos de acceso contra cuentas inexistentes]]— se evaden justamente por diseño. La detección ahí tiene que agrupar por algo que no sea la IP declarada —la sesión, el objetivo—, lo que refuerza que **confiar en `X-Forwarded-For` rompe tanto el control como su detección**. Anotado en [[MOC - Host header]].
