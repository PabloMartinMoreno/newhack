---
tipo: tradecraft
clase: "[[CWE-235 - Improper Handling of Extra Parameters]]"
eje: uso-de-la-discrepancia
implementacion: "Inyectar un & en un valor que la aplicación reenvía, para agregar parámetros a una petición al backend o a una URL generada"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]", "[[Conexión saliente del servidor de aplicación]]"]
requisitos: [entrada-reenviada-a-una-petición-o-url-que-la-app-construye]
coste: medio
alternativas: ["[[HPP - bypass por discrepancia de parseo]]", "[[SSRF - escaneo de la red interna]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - server-side HPP
  - client-side HPP
  - inyección de parámetro
tags:
  - dominio/web
---

# HPP - inyección de parámetros

## Cuándo lo elijo

Cuando la aplicación toma un valor del usuario y lo **inserta en una petición o una URL que ella construye** —una llamada a un backend, un enlace, un formulario—. Inyectar un `&` en ese valor agrega parámetros nuevos a la petición o URL generada, que el atacante no ponía.

Se reconoce cuando un parámetro termina reflejado dentro de otra URL —en un `Location`, en un enlace de la página, en una llamada interna—. Si el objetivo es colar un payload por un filtro que discrepa, la rama es [[HPP - bypass por discrepancia de parseo]]; esta es cuando la aplicación reenvía la entrada y se le inyectan parámetros.

## Por qué funciona

Dos variantes según dónde se construye la URL:

**Del lado del servidor (segundo orden).** La aplicación recibe un parámetro y arma con él una petición a un servicio interno:

```
petición: /api?user=juan
la app construye: http://backend/getUser?id=juan
```

Si `user` no se sanea, inyectar un `&` agrega un parámetro a la petición al backend:

```
petición: /api?user=juan%26admin=true
la app construye: http://backend/getUser?id=juan&admin=true
```

El `admin=true` inyectado llega al backend como si fuera legítimo. Con esto se sobrescriben parámetros que el frontend no expone —un rol, un límite, un identificador—, y se cruza con [[MOC - SSRF]] cuando lo que se inyecta cambia el destino de la petición.

**Del lado del cliente.** La aplicación refleja el parámetro dentro de un enlace o formulario de la página:

```
la página genera: <a href="/accion?id=INPUT">
```

Inyectar `id=1%26admin=true` produce `<a href="/accion?id=1&admin=true">`, así que cuando la víctima clickea, la petición lleva el parámetro inyectado. Es HPP como vector para modificar acciones que la víctima dispara, y se cruza con [[MOC - CSRF]] —el enlace envenenado ejecuta con la sesión de quien lo clickea—.

Las construcciones y las codificaciones del `&` —`%26`, `%3B`, doble codificación según la capa— están en [[HPP - matriz de referencia]].

## Cómo falla

Falla cuando la aplicación **codifica** el valor antes de insertarlo en la URL construida —un `&` codificado como `%26` no separa parámetros—. Es la mitigación correcta y la que va en el informe: codificar la entrada al construir una URL, igual que se escapa al construir HTML o SQL.

Falla cuando el backend **ignora** los parámetros que no espera, o valida el que importa del lado del servidor sin confiar en lo que llega en la URL interna.

Y falla cuando la entrada no se reenvía a ninguna URL construida —si solo se usa localmente, no hay dónde inyectar—.

## Coste

Medio. Encontrar el punto donde la entrada se reenvía a una URL es reconocimiento: observar redirecciones, enlaces generados, y sospechar llamadas a backend por el comportamiento. Una vez ubicado, inyectar el `&` es una petición.

El segundo orden es más caro de confirmar porque la petición al backend no se ve —hay que inferir el efecto—, parecido a la inyección ciega de otros dominios.

## Huella esperada

Firma sobre la entrada, y efecto según a dónde vaya el parámetro inyectado:

- El valor lleva un **`&` o `%26` codificado en medio de un parámetro** que normalmente es un identificador o un nombre. Un `&` dentro de un valor que se refleja en una URL es la firma, sobre [[Registro del WAF]] y [[Log de acceso del servidor web]].
- Si la inyección del lado del servidor cambia el destino de una petición al backend, la conexión resultante la ve [[Conexión saliente del servidor de aplicación]] —el mismo artefacto que cubre el SSRF—, cuando el parámetro inyectado redirige la llamada interna.
- El efecto del parámetro inyectado —un privilegio sobrescrito, una acción modificada— queda en [[Log de auditoría de la aplicación]] con el perfil de [[MOC - Broken access control]], si el log registra el valor efectivo y no el de entrada.

La detección aprovechable es la firma del `&` inyectado sobre la entrada. El caso del lado del cliente comparte el límite de los ataques del navegador —la petición final la dispara la víctima con su sesión— pero, a diferencia de clickjacking, deja la firma del parámetro envenenado en la generación del enlace. Anotado en [[MOC - HTTP parameter pollution]].
