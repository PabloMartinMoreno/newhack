---
tipo: deteccion
tecnicas: ["[[CWE-918 - Server-Side Request Forgery]]"]
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Log de acceso del servidor web]]"]
forma: agregado
ventana: "5m"
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - escaneo interno desde la app
tags:
  - dominio/web
---

# Barrido de puertos internos desde el servidor de aplicación

## Qué detecta

Muchas conexiones salientes fallidas desde el proceso de la aplicación hacia direcciones o puertos internos, en progresión, dentro de una ventana corta.

Lo que la hace fiable no es ninguna conexión individual: es **la proporción de fallos**. Una aplicación habla con un puñado corto y estable de destinos y casi todas sus conexiones tienen éxito. Cientos de intentos fallidos hacia destinos distintos es un perfil que ninguna aplicación legítima produce.

## Lógica

```
conexiones_salientes
| where timestamp > ago(5m)
| where proceso in ('php-fpm', 'node', 'java', 'python3', 'w3wp.exe')
| where ipv4_is_private(destino_ip) or destino_ip startswith '127.'
| summarize
    intentos = count(),
    fallidos = countif(estado != 'establecida'),
    destinos = dcount(destino_ip),
    puertos  = dcount(destino_puerto)
  by proceso, origen_host
| where intentos > 50 and fallidos * 1.0 / intentos > 0.8 and (destinos > 10 or puertos > 10)
```

El refuerzo que cierra el caso es la **correlación uno a uno**: cada conexión saliente precedida en milisegundos por una petición HTTP entrante al mismo endpoint con el parámetro variando. Eso establece causa y efecto, y convierte la alerta en un caso ya investigado.

## Falsos positivos conocidos

- **Descubrimiento de servicios y comprobaciones de salud** — una aplicación que consulta un registro de servicios o comprueba réplicas genera conexiones a muchos destinos. Se distingue porque **tienen éxito**, y el filtro de proporción de fallos las descarta.
- **Reintentos durante una caída de la base o de la caché**: muchos fallos hacia **un** destino. El filtro de cardinalidad los descarta.
- **Arranque de la aplicación**, cuando prueba dependencias.
- **Orquestadores y mallas de servicio**, que generan tráfico interno abundante — se excluyen por proceso.

## Evasiones conocidas

- **Bajar el ritmo** por debajo del umbral. La ventana de cinco minutos define cuán lento hay que ir, y a un escaneo lento le sobra tiempo.
- **Barrer solo destinos concretos** en vez de un rango. Es lo que recomienda [[SSRF destinos - matriz de referencia]] por eficiencia, y de paso evade la condición de cardinalidad: veinte puertos elegidos no son un barrido.
- **[[SSRF - metadatos de instancia cloud]]** la evade por completo: **una** conexión, exitosa. Por eso esa variante tiene detección propia.
- **Apuntar a un destino que responde** — un panel interno accesible produce conexiones exitosas y cae fuera del filtro de fallos.

Esta regla detecta el reconocimiento torpe. El SSRF dirigido lo evade, y ahí la detección que queda es la de destino.

## Cómo se prueba

Disparador: [[SSRF - escaneo de la red interna]] contra un laboratorio con varios servicios internos.

Forma `agregado`: el disparo tiene que ser un barrido real, no una conexión. Y el umbral hay que derivarlo de la línea base — cuántos destinos internos toca esta aplicación en cinco minutos cuando nadie la ataca.
