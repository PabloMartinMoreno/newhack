---
tipo: tradecraft
clase: "[[CWE-502 - Deserialization of Untrusted Data]]"
eje: impacto
implementacion: "Editar campos del objeto serializado sin buscar ejecución"
opsec: limpio
telemetria: ["[[Log de auditoría de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [blob-controlado, sin-firma-o-firma-rota]
coste: bajo
alternativas: ["[[Deserialización - cadena de gadgets]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - edición del blob serializado
  - object injection sin gadget
tags:
  - dominio/web
---

# Deserialización - manipulación de objeto

## Cuándo lo elijo

Primero, siempre. Es la rama barata del árbol de [[MOC - Deserialización]] y la que más veces alcanza: **no hace falta ninguna cadena de gadgets**, solo editar los campos del objeto y devolverlo.

Se pasa por alto todo el tiempo porque el dominio tiene fama de ser sobre RCE. Pero un objeto de sesión serializado con un campo `role` adentro es escalada de privilegios completa, y no requiere ni una biblioteca vulnerable ni una cadena disponible.

La condición es la misma que la de todo el dominio: que el blob no esté firmado, o que la firma se pueda reproducir — ver [[Deserialización - firma débil]].

## Por qué funciona

Porque el objeto serializado **es el estado de la aplicación**, escrito en un formato que el atacante puede leer y editar. Los formatos nativos de PHP, Java y Ruby incluyen los nombres de los campos y sus valores en texto plano o casi, así que editarlos es cuestión de encontrar el campo y ajustar el prefijo de longitud.

Lo que falla no es la deserialización en sí: es haber puesto **estado de confianza del lado del cliente**. Es el mismo error que [[Control de acceso - mass assignment]] visto desde otro lado — un campo que gobierna privilegios, escribible por quien no debería.

Por eso es la variante más silenciosa: la petición es válida, el objeto es válido, el servidor lo reconstruye correctamente. Nada falla.

## Cómo falla

- **El blob va firmado y la firma se verifica bien.** La mitigación correcta y la que cierra esta rama de golpe.
- **El objeto no contiene nada que valga la pena** — solo preferencias de interfaz o estado de un carrito. Es el caso común y hay que mirar antes de invertir.
- **El servidor revalida contra la base** en vez de confiar en el objeto. Deserializa el rol y después lo consulta de verdad, con lo que el campo editado no hace nada.
- **Prefijos de longitud mal ajustados.** En el formato de PHP, cada cadena declara su largo; cambiar `user` por `administrator` sin corregir el número rompe el blob entero. Es el error mecánico más frecuente.
- **El formato es binario y opaco** — Java y .NET nativos no se editan a mano con la misma facilidad, aunque siguen siendo editables con herramienta.

## Coste

Bajísimo. Decodificar, editar, recodificar, enviar. Lo caro es lo previo: darse cuenta de que ese parámetro es un objeto serializado. Ver [[Deserialización - matriz de identificación]].

## Huella esperada

`opsec: limpio` con la salvedad de siempre: no hay nada técnicamente anómalo. El objeto está bien formado y el servidor lo procesa sin error.

- [[Log de auditoría de la aplicación]] es la única que lo ve, y solo si registra **el rol efectivo** o los campos del estado reconstruido. Es el mismo requisito de instrumentación de [[Cambio de privilegio fuera del flujo administrativo]], y la misma detección sirve: un privilegio que cambió sin pasar por el flujo administrativo.
- [[Log de acceso del servidor web]] no ve nada útil: el blob va en una cookie o en un POST, y es opaco.
- Si el prefijo de longitud queda mal, hay excepción de deserialización en [[Log de errores del servidor web]]. Los intentos fallidos son bastante más visibles que los exitosos, que es una inversión incómoda para el defensor.

Los formatos y cómo editar cada uno están en [[Deserialización - matriz de identificación]].
