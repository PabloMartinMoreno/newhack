---
tipo: teoria
habilita: ["[[Envenenamiento de resolución de nombres]]", "[[Relay de NTLM]]", "[[Conexión a host de resolución de nombres no autorizado]]"]
relacionadas: ["[[ICMP - el canal de error de IP]]"]
aliases:
  - ARP
  - address resolution
tags: []
---

# ARP - resolución de direcciones en el segmento

## Qué dice la especificación

Un host que quiere hablar con `10.0.0.5` tiene una dirección IP y necesita una MAC: la trama Ethernet no sabe qué es una IP. ARP es la traducción, y es de una simpleza que explica todo lo demás:

1. El host pregunta **por difusión**, a toda la red local: *¿quién tiene `10.0.0.5`? Contestale a `10.0.0.3`*.
2. El dueño de esa IP contesta **en unicast**: *soy yo, esta es mi MAC*.
3. El que preguntó guarda el par IP↔MAC en una caché con vencimiento de minutos.

Eso es todo. No hay más protocolo. Y de esa ausencia salen las tres propiedades que importan:

- **No hay autenticación ni noción de titularidad.** Nada en ARP dice quién *tiene derecho* a una dirección. Una respuesta es válida por ser una respuesta.
- **No hay estado.** El que responde no necesita haber sido preguntado. Muchas pilas aceptan respuestas no solicitadas —el *gratuitous ARP*, que existe para casos legítimos como un failover de IP— y actualizan la caché con ellas.
- **El alcance es exactamente el dominio de difusión.** ARP no cruza un router. El segmento no es una división administrativa: es el límite físico de lo que este protocolo puede afectar.

En IPv6 no hay ARP: la función la cumple NDP, sobre ICMPv6. Cambia el encuadre, no el problema — sigue sin autenticar salvo que se despliegue SEND o protecciones del switch.

## Dónde el estándar deja lugar

Todo lo que decide si el segmento es abusable está fuera de la especificación, en la pila y en el switch:

- **Si se aceptan respuestas no solicitadas**, y si una consulta ajena también actualiza la caché. Varía por sistema operativo y por versión.
- **Cuánto vive una entrada.** Como la caché vence, una afirmación falsa hay que **sostenerla**: el dueño legítimo va a reclamar su dirección y la última respuesta gana. El envenenamiento no es un disparo, es una carrera continua.
- **Si el switch valida algo.** DAI (*Dynamic ARP Inspection*), *port security* y el binding DHCP-snooping son la mitigación real, y son configuración de infraestructura que la mayoría de las redes internas no tiene.

## Qué habilita

ARP es el caso más puro de un patrón que el vault ya usa una capa más arriba: **resolución sin autenticar significa que cualquiera puede contestar.**

- **El requisito que da por sentado el pentest interno.** [[Envenenamiento de resolución de nombres]] pide `acceso-a-la-red-en-el-mismo-dominio-de-difusión` — esa línea no significa nada sin saber qué delimita un dominio de difusión y por qué un router lo termina. LLMNR y NBT-NS son ARP con nombres en vez de direcciones: la misma pregunta a gritos, la misma ausencia de titularidad, el mismo *contesto yo primero*.
- **La posición en el camino.** [[Relay de NTLM]] necesita que el tráfico de la víctima llegue al atacante. LLMNR se lo regala porque la víctima pregunta; ARP es el mecanismo general de conseguir esa posición cuando nadie pregunta nada.
- **Por qué la detección mira la conexión y no el envenenamiento.** [[Conexión a host de resolución de nombres no autorizado]] ancla en que la víctima terminó hablando con una IP que no es de un servidor legítimo. Ese desplazamiento —detectar el efecto y no la causa— es forzado: la causa vive en una capa que el endpoint no registra. Es [[Detectar el efecto sobrevive a la evasión]] por necesidad, no por elección.

## Cómo se ve en la práctica

**No se ve.** Ni el visor de eventos de Windows ni Sysmon registran ARP: [[Sysmon EID 3 - NetworkConnect]] ve la conexión TCP que *resulta* del envenenamiento, nunca la trama que la desvió. Es el punto ciego más profundo de los que toca el vault, y no es una falta de configuración: la telemetría de endpoint arranca por encima de esta capa.

Lo observable vive en la red, no en el host, y siempre es agregado: una MAC que reclama muchas IPs, o una IP que cambia de MAC y vuelve, en ventanas cortas. El switch con DAI lo ve como violación; sin DAI hace falta un sensor pasivo en el segmento. Es otra instancia de [[La detección vive en el agregado, no en el evento]].

## Fuente

RFC 826 (Address Resolution Protocol); RFC 4861 (Neighbor Discovery for IPv6), que es la misma función sin ARP. Una nota sola alcanza para ARP: no tiene ejes ortogonales que descomponer — es un protocolo de dos mensajes, y lo que se le hace encima es tradecraft, no teoría.
