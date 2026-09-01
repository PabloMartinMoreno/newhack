---
tipo: meta
aliases:
  - Masscan - flags
  - masscan cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# Masscan - matriz de referencia

> [!info] Referencia pura, no un zettel
> Sintaxis. Qué cubre la herramienta y cuándo estorba, en [[masscan]]; el criterio de sondeo, en [[MOC - Reconocimiento de red]].
>
> Los ejemplos usan `10.10.10.0/24` de laboratorio.

## 1. Cómo se usa

```sh
masscan 10.10.10.0/24 -p1-65535 --rate 10000 -oL barrido.txt
```

> [!warning] La tasa por defecto son **100 paquetes por segundo**
> No 10000, ni "lo más rápido que pueda". Correr masscan sin `--rate` es más lento que nmap: los 65535 puertos de **un solo host** a 100 pps son once minutos. La fama de rápido es del techo, no del arranque, y `--rate` es obligatorio en la práctica aunque no lo sea en la sintaxis.

Tiene su propia pila TCP y no usa la del sistema. De ahí vienen la velocidad y casi todos sus problemas — § 4.

## 2. Objetivos, puertos y exclusiones

| Flag | Qué hace |
|---|---|
| `10.0.0.0/8`, `--range` | Objetivo: IP, rango `a-b` o CIDR |
| `-iL`, `--includefile` | Objetivos desde archivo — millones de rangos |
| `-p`, `--ports` | `80`, `20-25`, `80,443`, y UDP con `U:161` |
| `--exclude` | Sacar una IP o rango |
| `--excludefile` | Sacar los de un archivo |
| `--shards 1/3` | Repartir el mismo barrido entre instancias |

**No existe `--top-ports`.** Es de nmap; acá se escribe la lista.

> [!important] `--excludefile` es control de alcance, no una comodidad
> Las exclusiones **ganan** sobre los objetivos. En un engagement, la lista de fuera-de-alcance va en un archivo y se pasa siempre: a 10000 pps, un CIDR mal tipeado sale antes de que llegues a Ctrl-C.

## 3. Velocidad y fiabilidad

| Flag | Default | Qué controla |
|---|---|---|
| `--rate` | **100** | Paquetes por segundo |
| `--retries` | — | Reintentos, a 1 por segundo |
| `--wait` | 10 | Segundos de espera final por respuestas rezagadas |
| `--seed` | tiempo | Semilla del orden aleatorio |
| `--ttl` | 255 | TTL de salida |
| `--pfring` | — | Exige el driver PF_RING; sale si no está |

Techos reales según la documentación: ~250k pps en Windows, ~2.5M en Linux, ~25M con PF_RING.

**A tasa alta pierde puertos.** Es estadístico y silencioso: los paquetes se descartan en la cola y un puerto abierto sale como no-contestado. `--retries` lo compensa a costa de tiempo. La tasa es un compromiso entre reloj y falsos negativos, no un acelerador gratis.

`--wait 0` corta la espera final y **tira respuestas** que venían en camino. Bajarlo es de las formas más fáciles de perder resultados.

El `--ttl 255` por defecto es un valor que casi ningún sistema operativo usa de salida: es firma por sí solo.

## 4. El problema del `RST` del kernel

Masscan manda sus `SYN` por fuera del sistema operativo, pero las respuestas vuelven a la pila del sistema — que no sabe nada de esa conexión y contesta `RST`. El objetivo ve el `RST` y corta antes de que masscan pueda hacer nada más.

Con `-oL` de puertos abiertos no molesta. **Con `--banners` lo rompe todo**, porque la conexión se cierra antes del banner.

> [!example] Dejar que masscan complete la conexión
> ```sh
> # 1. que el kernel no conteste por el puerto de origen que va a usar masscan
> sudo iptables -A INPUT -i eth0 -p tcp --dport 44444 -j DROP
>
> # 2. decirle a masscan que use exactamente ese puerto
> sudo masscan 10.10.10.0/24 -p80,443 --banners --adapter-port 44444 --rate 5000
> ```
>
> Sin el paso 1, `--banners` devuelve poco y nada y parece que los servicios no responden. El síntoma no dice nada de la causa.

| Flag | Para qué |
|---|---|
| `-e`, `--adapter` | Interfaz de salida |
| `--adapter-port` | Puerto de origen — el que se filtra arriba |
| `--adapter-ip`, `--source-ip` | IP de origen; el rango debe ser potencia de 2 |
| `--router-mac` | MAC de destino, si el ARP del gateway falla |
| `--iflist` | Listar interfaces y salir |

## 5. Banners

| Flag | Default | Qué hace |
|---|---|---|
| `--banners` | — | Completa la conexión y lee el banner |
| `--connection-timeout` | 30 | Segundos que sostiene la conexión |
| `--hello-string[PORT]` | — | Saludo propio en base64 |
| `--hello-file[PORT]` | — | Ídem, desde archivo |
| `--capture cert` | — | Guardar el certificado TLS entero |
| `--http-user-agent` | — | Cambiar el `User-Agent` |

Sólo reconoce protocolos en sus **puertos estándar**: HTTP, FTP, IMAP4, POP3, SMTP, SSH, SSL, SMB, Telnet, RDP, VNC, memcached. Un servicio en un puerto raro sale sin identificar — para eso está [[nmap]] con `-sV`.

## 6. Salida y reanudación

| Flag | Formato |
|---|---|
| `-oL` | Lista — el que se parsea |
| `-oG` | Grepeable |
| `-oX` | XML |
| `-oJ` | JSON |
| `-oB` | Binario, el más chico y rápido |
| `--readscan` | Convertir el binario a otro formato después |
| `--rotate hourly` | Rotar el archivo por tiempo |
| `--interactive` | Ver los resultados en vivo |

El `-oL` es una línea por hallazgo, con este orden exacto:

```
#masscan
open tcp 80 10.10.10.5 1663258234
# end
```

| Campo | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Contenido | estado | protocolo | **puerto** | IP | marca de tiempo |

Confundir el 3 con el 4 es el error de parseo del formato: `$4` es la IP, no el puerto.

**Reanudación**: con Ctrl-C escribe `paused.conf` y se sigue con `--resume paused.conf`, que activa `--append-output` solo. Es lo que hace tolerable un barrido de días.

## 7. Encadenar con nmap

Masscan encuentra, [[nmap]] identifica:

```sh
masscan 10.10.10.5 -p1-65535 --rate 10000 -oL m.txt
nmap -sV -sC -p "$(awk '/^open/{print $3}' m.txt | sort -un | paste -sd,)" 10.10.10.5
```

`$3` es el puerto. Con varios hosts en el mismo archivo hay que agrupar por IP —campo `$4`— antes de armar el `-p`, porque si no se le pasan a un host los puertos de otro.

## 8. Depuración

| Flag | Para qué |
|---|---|
| `--echo` | Imprimir la configuración efectiva, en formato `-c` |
| `--offline` | No transmitir; para probar sin tocar la red |
| `--packet-trace` | Cada paquete; inservible a tasa alta |
| `--pcap archivo` | Guardar lo recibido en formato libpcap |
| `-c`, `--conf` | Archivo de configuración propio |

Por defecto lee `/etc/masscan/masscan.conf`. Igual que en [[Rustscan - matriz de referencia]], un archivo de configuración olvidado explica escaneos que dan distinto con el mismo comando: `--echo` muestra qué está aplicando de verdad.
