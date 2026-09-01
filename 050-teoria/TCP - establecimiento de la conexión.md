---
tipo: teoria
habilita: ["[[SSRF - escaneo de la red interna]]", "[[Barrido de puertos internos desde el servidor de aplicación]]", "[[Race - superación de límite]]", "[[Request smuggling - CL.TE y TE.CL]]"]
relacionadas: ["[[HTTP - el modelo de conexión]]", "[[HTTP - delimitación del cuerpo]]", "[[ICMP - el canal de error de IP]]"]
aliases:
  - three-way handshake
  - TCP handshake
tags: []
---

# TCP - establecimiento de la conexión

## Qué dice la especificación

TCP promete un **flujo de bytes ordenado y confiable** sobre IP, que no ofrece ninguna de las dos cosas. Para cumplirlo, los dos extremos tienen que ponerse de acuerdo en un número de secuencia inicial antes de transmitir un solo byte de datos. Eso es el handshake:

```
cliente                                      servidor
   │  SYN, seq=x                                 │
   ├────────────────────────────────────────────►│   LISTEN → SYN-RECEIVED
   │                                             │
   │              SYN-ACK, seq=y, ack=x+1        │
   │◄────────────────────────────────────────────┤
   │                                             │
   │  ACK, ack=y+1                               │
   ├────────────────────────────────────────────►│   ESTABLISHED
```

**Por qué tres y no dos.** Cada dirección del flujo tiene su propio número de secuencia y cada uno tiene que ser reconocido por el otro extremo. El `SYN` sincroniza la dirección cliente→servidor; el `SYN-ACK` reconoce esa y sincroniza la inversa; el `ACK` final reconoce la inversa. Dos segmentos alcanzarían para un flujo unidireccional, no para uno dúplex.

Tres consecuencias que se usan después:

- **El ISN se elige al azar** (RFC 6528). No es higiene: un número predecible permite inyectar segmentos en una conexión ajena sin verla, que es el ataque que la aleatorización cierra.
- **El cierre es asimétrico.** Abrir son tres segmentos; cerrar ordenadamente son cuatro (`FIN`/`ACK` en cada sentido), porque cada dirección se cierra por separado. `RST` es el aborto, inmediato y sin negociación.
- **El handshake responde en tres estados, no dos.** `SYN-ACK` es *hay algo escuchando*; `RST` es *llegué al host y no hay nadie en ese puerto*; el silencio es *no llegué, o alguien me descartó*. Esa ternaria es el oráculo entero del escaneo de puertos.

## Dónde el estándar deja lugar

- **La diferencia entre cerrado y filtrado no la define TCP.** Que un puerto sin servicio conteste `RST` o no conteste nada es política del host y de los equipos del medio — y cuando el problema es anterior a TCP, quien contesta es [[ICMP - el canal de error de IP]]. TCP sólo garantiza que las dos respuestas son distinguibles — y son distinguibles **por tiempo** incluso cuando la aplicación de arriba no reporta la diferencia.
- **Cuánto se espera un `SYN-ACK`** es configuración del cliente, no del protocolo. Un timeout de segundos contra un `RST` de milisegundos es una diferencia observable de tres órdenes de magnitud.
- **Cuándo se envían los bytes.** TCP no define cuándo la capa de arriba vacía el buffer: Nagle, `TCP_NODELAY` y el MSS deciden si tres escrituras salen en tres segmentos o en uno. Nadie prometió una correspondencia entre escritura y paquete.
- **Dónde termina un mensaje: en ningún lado.** TCP entrega bytes, no mensajes. Puede partir un envío en varios segmentos y juntar varios envíos en uno, y el receptor no tiene forma de saber cuál fue cuál. La delimitación es **enteramente** problema de la capa de arriba.

## Qué habilita

- **El escaneo interno por SSRF.** Lo que se lee no es una respuesta de la aplicación destino: es el resultado del handshake que hizo el servidor vulnerable, reflejado como diferencia de mensaje de error o de tiempo. Abierto responde rápido con algo, cerrado responde rápido con un error de conexión, filtrado tarda hasta el timeout → [[SSRF - escaneo de la red interna]]. Sin la ternaria del handshake el SSRF ciego no tendría oráculo y el dominio se quedaría en "se pueden hacer peticiones".
- **La detección de ese escaneo.** El artefacto no es una petición sino la **forma** del tráfico saliente: muchos destinos distintos desde un proceso que normalmente habla con tres → [[Barrido de puertos internos desde el servidor de aplicación]].
- **Las races de ventana chica.** Que dos peticiones lleguen efectivamente juntas depende de que quepan en el mismo segmento: se retienen los últimos bytes de cada una y se envían todos juntos, colapsando la variación de red por debajo de la ventana de la aplicación → [[Race - superación de límite]]. El "single-packet attack" es exactamente esto y su nombre es literal.
- **La raíz del smuggling.** Que dos servidores puedan discrepar sobre dónde termina una petición sólo es posible porque **TCP no marca el final de nada**. HTTP tuvo que inventar `Content-Length` y `chunked` porque el transporte no se lo daba, y ahí nació el desacuerdo → [[Request smuggling - CL.TE y TE.CL]] y [[HTTP - delimitación del cuerpo]].

Fuera de alcance del vault: `SYN` flood y agotamiento de la cola de conexiones a medio abrir. Son denegación de servicio, no acceso.

## Cómo se ve en la práctica

El handshake vive **por debajo del log de la aplicación**. El servidor web registra peticiones que se completaron; el `SYN` que nunca recibió respuesta no aparece en ningún lado. Es un punto ciego estructural: para verlo hace falta telemetría de conexión del host o de la red —conntrack, flow logs, eBPF—, que casi nunca está del lado de las aplicaciones web.

Lo observable, cuando hay con qué, es agregado y no puntual:

- **Abanico de destinos**: un proceso que abre conexiones a muchos pares IP:puerto distintos en poco tiempo, con la mayoría fallando. Ninguna conexión individual es sospechosa; la distribución sí. Es el caso de manual de [[La detección vive en el agregado, no en el evento]].
- **Bimodalidad de latencia**: la separación entre `RST` inmediato y timeout largo se ve como dos picos en la distribución de tiempos, del mismo modo que en [[Latencia bimodal en un endpoint]]. Es [[La latencia como canal de datos]] una capa más abajo.

## Fuente

RFC 9293 §3.5 (Establishing a Connection) y §3.6 (Closing a Connection); RFC 6528 (Defending Against Sequence Number Attacks). Los destinos que pagan al escanear están en [[SSRF destinos - matriz de referencia]].
