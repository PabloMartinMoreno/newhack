---
tipo: teoria
habilita: ["[[SSRF - escaneo de la red interna]]", "[[SSRF - canal ciego]]", "[[Barrido de puertos internos desde el servidor de aplicación]]"]
relacionadas: ["[[TCP - establecimiento de la conexión]]", "[[ARP - resolución de direcciones en el segmento]]"]
aliases:
  - ICMP
  - destination unreachable
tags: []
---

# ICMP - el canal de error de IP

## Qué dice la especificación

IP entrega paquetes sin garantías y sin forma de avisar cuando algo sale mal. ICMP es ese aviso: **no es un protocolo de transporte sino el canal de control del propio IP**. No tiene puertos, no lleva datos de aplicación, y su trabajo es que el emisor se entere de por qué su paquete no llegó.

Los mensajes que importan:

| Tipo | Qué dice | Dónde aparece |
|---|---|---|
| 8 / 0 | Echo request / reply | `ping`, descubrimiento de hosts |
| 3 código 1 | Host inalcanzable | No hay quien conteste el ARP del último salto |
| 3 código 3 | Puerto inalcanzable | UDP contra un puerto sin servicio |
| 3 código 4 | Fragmentación necesaria con DF | Descubrimiento de MTU |
| 3 código 13 | Prohibido administrativamente | Un firewall que contesta en vez de descartar |
| 11 | Tiempo excedido (TTL) | `traceroute` |

La pieza de diseño que lo hace utilizable: **un error ICMP incluye la cabecera IP y los primeros bytes del paquete que lo causó**. Con eso el emisor identifica a qué conexión suya corresponde el error, y lo convierte en un fallo local inmediato en vez de una espera.

Una precisión que se confunde seguido: **un puerto TCP cerrado no responde ICMP, responde `RST`** — eso vive en [[TCP - establecimiento de la conexión]]. ICMP entra cuando el problema es *anterior* a TCP: no hay ruta, no hay host, o alguien decidió prohibirlo.

## Dónde el estándar deja lugar

En lo único que importa: **si el error se manda o no**.

- Un firewall puede contestar `tipo 3 código 13` —correcto y cortés— o **descartar en silencio**. Las dos conductas son legítimas y la diferencia entre ellas es toda la distinción entre *cerrado* y *filtrado*. Esa decisión no la toma ningún RFC: la toma quien escribió la regla.
- **La limitación de tasa de errores ICMP** es recomendada pero sin números fijos. Un contador global compartido entre destinos es a su vez un canal lateral: se puede inferir actividad ajena por cuántos errores dejan de llegar.
- **Qué error se elige** cuando varios aplican, y si se revela `host inalcanzable` —que confirma que la red existe— en vez de `prohibido`, es criterio de implementación y filtra topología.

## Qué habilita

Todo el oráculo del escaneo interno por SSRF sale de acá. La aplicación vulnerable no informa el estado de un puerto: informa **cuánto tardó y con qué error falló**, y ese error lo dictó ICMP o su ausencia.

- **Rápido con error** — llegó un ICMP, o un `RST` de TCP: el host existe y contestó algo. La red hasta ahí es alcanzable.
- **Lento hasta el timeout** — silencio: alguien descartó sin avisar. Filtrado, o el host no existe.
- **Rápido y exitoso** — hay servicio.

Esa ternaria es lo que hace que [[SSRF - escaneo de la red interna]] sea un escáner de verdad y no una lista de esperas indistinguibles. En [[SSRF - canal ciego]] es todavía más determinante: cuando la respuesta no vuelve, la **diferencia de tiempo entre un error inmediato y un descarte silencioso** es el único bit disponible por petición — [[La latencia como canal de datos]] aplicada a la capa de red.

Del lado azul, [[Barrido de puertos internos desde el servidor de aplicación]] detecta el abanico de intentos; el detalle que ICMP aporta es **por qué la mayoría falla rápido**, que es lo que separa un barrido de un cliente con un destino mal configurado.

Fuera de alcance por ahora: ICMP como canal encubierto —túneles y exfiltración sobre `echo`—. Hoy no hay tradecraft en el vault que lo consuma, y una nota sin consumidor es un apunte. Se escribe cuando exista la técnica, no antes.

## Cómo se ve en la práctica

En el log de la aplicación, ICMP no existe. Lo que sí sobrevive, y es el hallazgo incómodo, es que **el mensaje de error que la aplicación devuelve al usuario suele ser la traducción literal del ICMP recibido**: `Connection refused`, `No route to host`, `Network is unreachable` y un timeout son cuatro estados distintos filtrados hacia afuera por la capa de errores de la propia aplicación. El oráculo no se filtra por la red: se filtra por el `catch` que imprime el mensaje.

Con telemetría de red —flow logs, conntrack—, la firma es la de siempre: agregada. Muchos destinos, mayoría con error inmediato, en una ventana corta, desde un proceso que normalmente habla con tres.

## Fuente

RFC 792 (Internet Control Message Protocol); RFC 4443 para ICMPv6, que además carga la resolución de vecinos que en IPv4 hace [[ARP - resolución de direcciones en el segmento]]. Los puertos que pagan al escanear están en [[SSRF destinos - matriz de referencia]].
