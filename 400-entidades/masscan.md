---
tipo: entidad
clase-entidad: herramienta
tecnicas: ["[[T1046 - Network Service Discovery]]", "[[T1018 - Remote System Discovery]]"]
aliases: []
tags:
  - dominio/red
---

# masscan

## Qué es

Escáner de puertos asíncrono con **pila TCP propia**. No usa la del sistema operativo: arma y lee los paquetes por su cuenta, y de ahí sale tanto la velocidad —hasta millones de paquetes por segundo— como su lista de problemas particulares.

Sintaxis completa en [[Masscan - matriz de referencia]].

## Qué técnicas implementa

- [[Escaneo - sondeo SYN de puertos TCP]] sobre rangos grandes, y nada más.
- [[Escaneo - identificación de servicio y versión]] sólo a medias: `--banners` lee el banner en puertos estándar, sin las sondas de `-sV`.
- Descubrimiento como efecto secundario: un host que contesta algo está vivo. Para hacerlo bien, [[Escaneo - descubrimiento de hosts]].

## Cuándo NO usarla

**Cuando el rango es chico.** Por debajo de una /24, [[nmap]] con `--min-rate` alto llega casi igual de rápido y encima identifica servicio en la misma pasada. Masscan gana en /16 para arriba, y ahí gana por mucho.

**Cuando el resultado tiene que ser confiable sin revisar.** A tasas altas pierde puertos: los paquetes se descartan en la cola y un puerto abierto aparece como no-contestado, sin que nada lo avise. Es estadístico y silencioso.

**Cuando importa el ruido.** Es lo más estruendoso del dominio: diez mil paquetes por segundo desde un origen es la firma más obvia que existe — [[Abanico de conexiones fallidas desde un host]]. Y el `--ttl 255` por defecto es un valor que casi ningún sistema usa de salida: firma por sí solo.

**Cuando el alcance es estricto.** A esa tasa, un CIDR mal tipeado sale entero antes de que llegues a Ctrl-C. Las exclusiones van en `--excludefile`, siempre.

## Estado

Mantenida. El uso normal es de frente: masscan barre y **nmap relee** lo que encontró. Alternativa más cómoda para un solo host: [[rustscan]].

> [!tip] Por qué esta nota es corta
> El vault **no se organiza por herramienta**. El criterio vive en [[MOC - Reconocimiento de red]] y la sintaxis en su matriz; esta nota sólo mapea qué cubre masscan y cuándo estorba.
