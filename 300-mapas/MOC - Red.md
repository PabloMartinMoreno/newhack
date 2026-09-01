---
tipo: moc
dominio: protocolo
aliases:
  - MOC red
  - fundamentos de red
tags: []
---

# MOC - Red

> [!abstract] Mapa de teoría, no de ataque
> Contesta *qué presupone lo que estoy por explotar*, no *cómo lo exploto*. Cada nota existe porque hay al menos un ataque del vault que no se entiende sin ella — la regla de admisión de [[Estructura del vault]].

Las tres capas que están debajo de todo lo demás. Se leen de abajo hacia arriba y cada una aporta exactamente una cosa al conocimiento ofensivo del vault:

| Capa | Nota | Lo que aporta |
|---|---|---|
| Enlace | [[ARP - resolución de direcciones en el segmento]] | Por qué el segmento es una frontera de confianza |
| Red | [[ICMP - el canal de error de IP]] | Por qué *cerrado* y *filtrado* se distinguen |
| Transporte | [[TCP - establecimiento de la conexión]] | Por qué hay que delimitar mensajes, y la ternaria del handshake |

El hilo que las une: **ninguna de las tres autentica nada, y las tres responden distinto según quién esté escuchando**. De ahí salen los dos oráculos que el vault usa —el del escaneo interno y el de la posición en el segmento— y la raíz del smuggling.

## Árbol de decisión — qué capa contesta

```
¿Qué pregunta tengo?
├─ ¿Puedo hacerme pasar por otro sin credencial?
│  └─ ¿Estoy en el mismo dominio de difusión?
│     ├─ Sí → nadie valida titularidad → [[ARP - resolución de direcciones en el segmento]]
│     │        el mismo patrón con nombres → [[Envenenamiento de resolución de nombres]]
│     └─ No → el router terminó el alcance; hace falta otra posición
├─ ¿Qué hay del otro lado, y por qué tarda lo que tarda?
│  ├─ Falló rápido con error → alguien contestó → [[ICMP - el canal de error de IP]]
│  ├─ Falló lento, sin nada  → descarte silencioso → misma nota
│  └─ Conectó → hay servicio → [[TCP - establecimiento de la conexión]]
└─ ¿Por qué dos servidores leen distinto la misma petición?
   └─ Porque el transporte no marca el final de nada
      → [[TCP - establecimiento de la conexión]] → [[HTTP - delimitación del cuerpo]]
```

## Orden de aprendizaje

1. [[ARP - resolución de direcciones en el segmento]] — resolución sin autenticar, y qué delimita un segmento
2. [[ICMP - el canal de error de IP]] — el canal de control de IP; de dónde sale cada estado del escaneo
3. [[TCP - establecimiento de la conexión]] — handshake, flujo de bytes sin fronteras

Y de ahí para arriba, [[MOC - HTTP]].

## Qué ataque habilita cada pieza

| Pieza | Notas que la presuponen |
|---|---|
| ARP | [[Envenenamiento de resolución de nombres]] · [[Relay de NTLM]] · [[MOC - AD envenenamiento y relay]] |
| ICMP | [[SSRF - escaneo de la red interna]] · [[SSRF - canal ciego]] · [[MOC - SSRF]] |
| TCP | [[SSRF - escaneo de la red interna]] · [[Race - superación de límite]] · [[MOC - Request smuggling]] |

## Cara azul

Las tres capas comparten el mismo punto ciego y conviene decirlo de una vez: **la telemetría de endpoint del vault arranca por encima de ellas**. [[Sysmon EID 3 - NetworkConnect]] registra una conexión establecida; no registra el ARP que la desvió, ni el ICMP que explica por qué otras cien fallaron.

Consecuencias:

- Lo que se detecta es siempre el **efecto** —la conexión a un host que no corresponde, el abanico de destinos—, nunca la causa. [[Detectar el efecto sobrevive a la evasión]] acá no es una elección de diseño: es lo único disponible.
- Todas las firmas son agregadas. Una conexión fallida no dice nada; la distribución de cien sí. Ver [[La detección vive en el agregado, no en el evento]].
- Cubrir estas capas de verdad pide telemetría que el vault todavía no modela: flow logs, conntrack, DAI del switch. Es un hueco de `550-telemetria/`, no de las detecciones.

## Huecos conocidos

- **TCP**: escrita la pieza del establecimiento. Faltan ventana y control de flujo, los estados de cierre, y MSS y fragmentación. Cuando estén, TCP se lleva su propio MOC y este mapa lo enlaza como hermano.
- **DNS**: sin abrir, y es el que más deuda tiene — [[Exfiltración por subdominios de alta entropía]] y [[Sysmon EID 22 - DnsQuery]] ya existen y ninguna nota explica la resolución recursiva.
- **TLS**: sin abrir. SNI, verificación de cadena y ALPN; ALPN además toca la degradación de HTTP/2.
- **IPv6 / NDP**: sin abrir. Es ARP sin ARP, y en redes internas suele estar activo y sin vigilar.
