---
tipo: meta
aliases:
  - Sondeos - comparación
  - tipos de escaneo
  - scan types
tags:
  - meta/referencia
  - dominio/red
---

# Sondeos de red - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué manda cada sondeo y qué significa cada respuesta, sin herramienta de por medio. El criterio —cuál elegir— está en [[MOC - Reconocimiento de red]]; el porqué protocolar, en [[TCP - respuestas a segmentos inesperados]]; los flags, en [[Nmap - matriz de referencia]].

## 1. Los sondeos no comparan entre sí

Antes de la tabla, la distinción que la ordena: **ARP e ICMP contestan si el host existe; los sondeos TCP y UDP contestan si el puerto escucha**. Son preguntas de capas distintas y no son alternativas una de otra.

| Capa | Sondeos | Pregunta |
|---|---|---|
| Enlace | ARP | ¿existe esta dirección en mi segmento? |
| Red | ICMP echo, timestamp | ¿este host responde? |
| Transporte | SYN, connect, UDP, FIN/NULL/Xmas, ACK | ¿este puerto escucha? |

Un `-Pn` no es "un escaneo distinto": es saltear la primera pregunta.

## 2. Descubrimiento — ¿hay alguien?

| Sondeo | Manda | Vivo | No vivo | Silencio |
|---|---|---|---|---|
| ARP | *who-has* difusión | ARP reply | — | **no existe** |
| ICMP echo | echo request | echo reply | — | ambiguo |
| ICMP timestamp | timestamp req. | timestamp reply | — | ambiguo |
| TCP SYN ping | `SYN` a puerto | `SYN-ACK` o `RST` | — | ambiguo |
| TCP ACK ping | `ACK` suelto | `RST` | — | ambiguo |

**ARP es el único exacto del vault.** No hay firewall que lo filtre porque el firewall vive una capa más arriba, así que el silencio significa de verdad *no hay nadie*. Fuera del segmento el silencio no significa nada: ver [[ARP - resolución de direcciones en el segmento]].

Los sondeos de descubrimiento por TCP existen porque atraviesan filtros que descartan ICMP. Se combinan varios y basta que uno vuelva.

## 3. Estado de puerto — ¿hay algo escuchando?

| Sondeo | Manda | Abierto | Cerrado | Silencio |
|---|---|---|---|---|
| SYN | `SYN` | `SYN-ACK` | `RST` | filtrado |
| connect | `SYN` (pila) | conexión | `RST` | filtrado |
| UDP | datagrama | respuesta app | ICMP 3/3 | abierto\|filtrado |
| FIN / NULL / Xmas | sin `SYN` | **silencio** | `RST` | abierto\|filtrado |
| ACK | `ACK` suelto | `RST` | `RST` | **filtrado** |

## 4. Las tres cosas que confunden

**La inversión.** En `FIN`, `NULL` y Xmas el silencio significa **abierto** y la respuesta significa cerrado, al revés que en todos los demás. Sale de que el RFC manda descartar en silencio un segmento sin `SYN`, `ACK` ni `RST` cuando el puerto escucha.

**El `ACK` no mide puertos.** Devuelve `RST` esté abierto o cerrado, así que su columna *abierto* y su columna *cerrado* son la misma. Lo que informa es si el `RST` volvió: mapea el **firewall**, no el servicio. Es el único sondeo de la tabla cuya salida no habla del host.

**El silencio no es un estado, son cuatro.** Qué significa depende del sondeo:

| Sondeo | Silencio significa |
|---|---|
| ARP | no existe — conclusión firme |
| ICMP | no sé |
| SYN | filtrado |
| UDP, FIN/NULL/Xmas | abierto **o** filtrado, indistinguible |

## 5. Coste y privilegio

| Sondeo | Privilegio | Velocidad | Comentario |
|---|---|---|---|
| ARP | root | muy alta | /24 en segundos |
| ICMP | root | muy alta | primero en caer por filtro |
| SYN | root | alta | caso base |
| connect | ninguno | media | completa el handshake |
| FIN / NULL / Xmas | root | alta | resultado a validar aparte |
| ACK | root | alta | mapea filtro, no puertos |
| UDP | root | **muy baja** | limitado por tasa de ICMP ajena |

En UDP la lentitud no es del escáner: es la limitación de tasa de errores ICMP del destino. Apurarlo **corrompe** el resultado — los cerrados dejan de contestar y pasan a parecer abiertos.

## 6. Qué ve el defensor

| Sondeo | Llega a la app | Telemetría de endpoint |
|---|---|---|
| ARP | no | **nada** |
| ICMP | no | nada |
| SYN | no | conexión saliente en el que escanea |
| connect | sí | ídem, y log del servicio |
| FIN / NULL / Xmas | no | ídem; firma de IDS trivial |
| ACK | no | ídem |
| UDP | según el servicio | ídem |

Ninguno de los sondeos que no completan el handshake llega a una aplicación, así que del lado escaneado no hay log de servicio que los registre. La señal vive en el host que escanea — la asimetría que explica [[Abanico de conexiones fallidas desde un host]].

Y una advertencia contraintuitiva: los sondeos de bandera anómala son **más** detectables que un `SYN`, no menos. No existe tráfico legítimo con esa forma, así que cualquier IDS tiene firma.

## 7. Sondeo sin herramienta

Sin poder subir un binario al host comprometido, queda el `connect()` que ya trae el sistema. Los dos completan el handshake: llegan a la aplicación y pueden quedar en su log.

```bash
# bash, no zsh: /dev/tcp es una construcción del propio bash, no un archivo
for p in 22 80 443 445 3389; do (echo >/dev/tcp/10.10.10.5/$p) 2>/dev/null && echo "$p abierto"; done
```

```powershell
445,3389,5985 | % { if ((New-Object Net.Sockets.TcpClient).ConnectAsync("10.10.10.5",$_).Wait(300)) {"$_ abierto"} }
```

Sólo distinguen abierto de todo lo demás: sin `raw sockets` no hay forma de separar *cerrado* de *filtrado*, porque el sistema devuelve un error único para las dos cosas.

## 8. Qué entrega cada puerto UDP

Vale sin importar con qué se haya escaneado. En orden de retorno:

| Puerto | Servicio | Qué se saca |
|---|---|---|
| 161 | SNMP | Con `public`: interfaces, procesos, usuarios |
| 53 | DNS | Versión, recursión abierta, transferencia de zona |
| 137 | NetBIOS | Nombre de máquina y de dominio, sin credencial |
| 88 | Kerberos | Confirma controlador de dominio |
| 500 | IKE | VPN, y a veces modo agresivo |
| 623 | IPMI | Gestión fuera de banda; hashes sin autenticar |
| 69 | TFTP | Archivos sin autenticación |
| 123 | NTP | `monlist`: lista de pares que hablaron |
| 1900 | SSDP | Inventario de dispositivos de la red |

Son los que justifican pagar el coste del sondeo UDP de § 5: pocos, conocidos, y varios entregan sin credencial.

## 9. Puerto abierto → a dónde seguir en el vault

El reconocimiento termina donde empieza otro dominio, sea cual sea la herramienta que encontró el puerto.

| Puerto | Servicio | Seguir en |
|---|---|---|
| 80 · 443 · 8080 | HTTP | [[MOC - HTTP]], y la familia web de [[Inicio]] |
| 88 · 464 | Kerberos | [[MOC - AD roasting]] |
| 135 · 139 · 445 | RPC / SMB | [[MOC - AD envenenamiento y relay]] |
| 389 · 636 · 3268 | LDAP | [[MOC - AD enumeración]] · [[MOC - LDAP injection]] |
| 3389 | RDP | [[MOC - AD movimiento lateral]] |
| 5985 · 5986 | WinRM | [[MOC - AD movimiento lateral]] |
| 1433 · 3306 · 5432 | Bases SQL | [[MOC - SQL injection]] |
| 27017 | MongoDB | [[MOC - NoSQL injection]] |
| 25 · 587 | SMTP | [[MOC - Email header injection]] |
| 6379 · 11211 | Redis / memcached | [[MOC - SSRF]] — destinos internos |
| 443 con AD detrás | ADCS web enrollment | [[MOC - ADCS]] |
