---
tipo: tradecraft
clase: "[[CWE-640 - Weak Password Recovery Mechanism for Forgotten Password]]"
eje: uso-del-host
implementacion: "Cambiar el Host del pedido de restablecimiento para que el enlace del correo apunte a un dominio propio y capturar el token"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [enlace-de-reset-construido-con-el-host]
coste: bajo
alternativas: ["[[Host header - SSRF por enrutamiento]]", "[[Autenticación - abuso de recuperación de contraseña]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - password reset poisoning
  - envenenamiento de reset
tags:
  - dominio/web
---

# Host header - envenenamiento del restablecimiento

## Cuándo lo elijo

Cuando la aplicación tiene "olvidé mi contraseña", envía un enlace por correo, y ese enlace se construye con el `Host` de la petición. Se reconoce probando el flujo de reset con un `Host` modificado y viendo si el enlace del correo —o el error, o cualquier reflejo— usa el dominio inyectado.

Es el uso más directo del abuso de Host y el de mayor impacto: termina en toma de cuenta. Si el Host no construye el enlace pero sí enruta la petición, la rama es [[Host header - SSRF por enrutamiento]]; si gobierna un control de acceso, [[Host header - bypass de acceso por confianza]].

## Por qué funciona

El servidor genera el enlace de restablecimiento con un token de un solo uso y un dominio. Muchas implementaciones toman ese dominio del **`Host` de la petición** en vez de una configuración fija, porque es lo más cómodo —"usá el host con el que te pidieron"—. El atacante pide el reset de la cuenta de la víctima con un `Host` propio:

```http
POST /reset HTTP/1.1
Host: atacante.com
...
email=victima@objetivo.com
```

El servidor manda a la víctima un correo con el enlace `https://atacante.com/reset?token=SECRETO`. Si la víctima lo abre —o si un escáner de enlaces del correo lo visita, que pasa seguido—, el token válido llega al servidor del atacante, que lo usa para fijar una contraseña nueva. Cuenta tomada.

Las formas de inyectar el `Host` cuando el directo no pasa —`X-Forwarded-Host`, doble Host, URL absoluta en la línea de petición— están en [[Host header inyección - matriz de referencia]]. `X-Forwarded-Host` es la más frecuente: la aplicación valida el `Host` real pero construye el enlace con la cabecera de reenvío, que no valida.

Es primo de [[Autenticación - abuso de recuperación de contraseña]] —misma `clase:` `CWE-640`— pero por un vector distinto: allá se abusa la lógica del flujo, acá el dominio del enlace.

## Cómo falla

Falla cuando el enlace se construye con un **dominio configurado**, no con el `Host` de la petición. Es la mitigación correcta y la que va en el informe: el dominio del reset no debe salir de una cabecera.

Falla cuando el `Host` y todas sus variantes de reenvío se validan contra una lista blanca antes de usarse.

Y depende de que la víctima —o un cliente automático— abra el enlace. A diferencia de un ataque directo, hay un requisito de interacción, aunque los escáneres de enlaces de muchos clientes de correo lo cumplen solos, lo que sube la fiabilidad respecto de otros ataques del lado del cliente.

## Coste

Bajo. Confirmar que el enlace usa el `Host` es un pedido de reset con `Host` o `X-Forwarded-Host` propio y mirar el correo —o el reflejo en la respuesta—. La cadena completa son pocas peticiones.

El costo real es de reconocimiento del correo: hace falta poder observar el enlace generado, sea porque se refleja en la respuesta, porque se prueba contra una cuenta propia primero, o porque el token viaja también en un `Referer` filtrable.

## Huella esperada

Firma escribible y de fuente disponible, poco vigilada:

- El pedido de reset lleva un **`Host` o `X-Forwarded-Host` que no corresponde al dominio de la aplicación**. Una petición de restablecimiento con un Host externo no ocurre en tráfico legítimo, así que es una firma de buena fidelidad sobre las cabeceras, que registra [[Log de acceso del servidor web]] si guarda el `Host`. Es análoga a la firma del `Origin` de [[CORS - reflejo del origen con credenciales]] y a la del handshake de [[WebSocket - secuestro entre sitios]]: la cabecera que no matchea la lista blanca es el ataque.
- El correo enviado apunta a un dominio externo, señal que solo se ve si se auditan los dominios de los enlaces de reset — [[Log de auditoría de la aplicación]] si registra el enlace generado.

Es de los pocos huecos recientes que es de trabajo y no de fuente: el `Host` de la petición se registra más seguido que los cuerpos. Alertar pedidos de reset con `Host` fuera de la lista blanca es candidato a detección propia, anotado en [[MOC - Host header]].
