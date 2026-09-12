---
tipo: moc
dominio: red
aliases:
  - MOC reconocimiento
  - MOC escaneo
tags:
  - dominio/red
---

# MOC - Reconocimiento de red

> [!abstract] Nota de referencia paraguas
> La definición vive en [[T1046 - Network Service Discovery]] y [[T1018 - Remote System Discovery]]. La sintaxis, en [[Nmap - matriz de referencia]]. Acá vive **la decisión**.

Es la primera fase de cualquier engagement interno y la única del vault donde **no se explota nada**: se hacen preguntas que la pila TCP/IP está obligada a contestar. Todo el conocimiento sale de las reglas del protocolo, no de un fallo — por eso el dominio se apoya entero en [[MOC - Red]] y casi no tiene contenido propio más allá de la decisión.

| Eje | Valores |
|---|---|
| Alcance | descubrimiento de hosts · sin descubrimiento (todo vivo) |
| Sondeo | `SYN` · `connect()` · UDP · bandera anómala · `ACK` |
| Profundidad | estado del puerto · identificación de servicio y versión |
| Sigilo | velocidad · fragmentación · señuelos · origen → matriz |

**El sondeo es el eje raíz** porque decide qué se puede saber y a qué costo. El sigilo va a matriz: es ortogonal —cualquier sondeo se puede hacer lento o con señuelos— y es sintaxis, no criterio.

## Árbol de decisión — qué le pregunto a la red

```
¿Dónde estoy parado?
├─ Dentro del segmento
│  └─ barrido ARP: exacto, nadie lo filtra, nadie lo registra
│     → [[Escaneo - descubrimiento de hosts]]
└─ Fuera del segmento
   └─ el silencio es ambiguo → no confiar; tratar el rango como vivo

¿Tengo privilegios para raw sockets?
├─ Sí → [[Escaneo - sondeo SYN de puertos TCP]]        ← el caso base
└─ No → caída a connect(): completa el handshake,
        llega a la aplicación y puede quedar en su log

¿El TCP no dio nada, o busco un servicio que sólo vive en UDP?
└─ → [[Escaneo - sondeo de puertos UDP]]   lista corta de puertos, nunca 65535

¿Quiero entender el filtro que tengo delante, no el puerto?
└─ ACK suelto → [[Escaneo - sondeos de bandera anómala]]
   (los sondeos FIN/NULL/Xmas, sólo si la pila cumple el RFC — no Windows)

¿Ya sé qué puertos importan?
└─ → [[Escaneo - identificación de servicio y versión]]   ← acá se deja de ser invisible
```

Tres cosas que este orden codifica:

**El descubrimiento se saltea más seguido de lo que se hace.** Fuera del segmento, un host que no contesta puede estar apagado o protegido, y son los protegidos los que interesan. Creerle al silencio es el falso negativo más caro de la fase.

**`SYN` no es sigiloso, es preciso.** La fama de *half-open* viene de cuando lo único que registraba conexiones era la aplicación. Se elige por rápido y exacto, no por invisible.

**La identificación de versión es la frontera.** Todo lo anterior se queda en la pila del objetivo; acá se completan handshakes y se llega a la aplicación, con línea en su log. Es el punto donde el reconocimiento se vuelve evidente, y por eso se hace sobre una lista corta.

## Orden de aprendizaje

1. [[TCP - establecimiento de la conexión]] — la ternaria abierto/cerrado/filtrado
2. [[TCP - respuestas a segmentos inesperados]] — de dónde sale cada tipo de sondeo
3. [[ICMP - el canal de error de IP]] — por qué UDP es lento y por qué el silencio es ambiguo
4. [[Escaneo - descubrimiento de hosts]] — qué existe
5. [[Escaneo - sondeo SYN de puertos TCP]] — qué escucha
6. [[Escaneo - sondeo de puertos UDP]] — la mitad que nadie mira
7. [[Escaneo - sondeos de bandera anómala]] — mapear el filtro
8. [[Escaneo - identificación de servicio y versión]] — qué corre

## Cheatsheets

- [[Sondeos de red - matriz de referencia]] — qué manda cada sondeo, qué significa cada respuesta y cada silencio, coste y qué ve el defensor. Sin herramienta de por medio
- [[Nmap - matriz de referencia]] — la traducción a flags: objetivos, temporización, evasión y NSE
- [[Rustscan - matriz de referencia]] — lote, timeout y `ulimit`, el `-Pn` que agrega solo, y el motor de scripts
- [[Masscan - matriz de referencia]] — tasa, exclusiones, el `RST` del kernel que rompe `--banners`, y el formato de `-oL`
- [[DNS - matriz de referencia]] — `dig`/`host`/`nslookup`, registros, transferencia de zona (AXFR) y fuerza bruta de subdominios
- [[SMTP - matriz de referencia]] — enumeración de usuarios (VRFY/EXPN/RCPT), open relay y envío/spoofing con `swaks`
- [[IMAP y POP3 - matriz de referencia]] — leer buzones: comandos por protocolo, `SEARCH` de IMAP, TLS y fuerza bruta
- [[SNMP - matriz de referencia]] — community brute, enum por OID (incluida la fuga de credenciales en la línea de comando) y escritura con RW
- [[MySQL - matriz de referencia]] — conectar, enumerar, `LOAD_FILE`/`OUTFILE` (webshell → RCE) y credenciales en config
- [[MSSQL - matriz de referencia]] — `mssqlclient`, `xp_cmdshell` (RCE), impersonación, linked servers y captura/relay de NetNTLM
- [[Oracle TNS - matriz de referencia]] — listener TNS, adivinar el SID, `odat` para credenciales y RCE (utlfile/externaltable/scheduler)
- [[IPMI - matriz de referencia]] — BMC (iDRAC/iLO/Supermicro): volcado de hash RAKP, cipher zero y credenciales por defecto
- [[SSH - matriz de referencia]] — acceso remoto: métodos de auth, brute, clave privada (+ crack), túneles/pivoting y `sshd_config`
- [[XML de escaneo a HTML]] — del `-oX` a un informe HTML legible. Sirve para las dos herramientas

## Cara roja

Las herramientas son entidades, no la organización del conocimiento: si desaparecen mañana, las ocho notas de arriba siguen valiendo.

- [[nmap]] — la de referencia, y la única que identifica servicio
- [[masscan]] — sólo velocidad sobre rangos enormes; resigna precisión
- [[rustscan]] — frente rápido que delega en nmap

## Cara azul

| Fase | Emite | Detección |
|---|---|---|
| Descubrimiento por ARP | — | ninguna posible con la telemetría actual |
| Descubrimiento y sondeo desde host instrumentado | [[Sysmon EID 3 - NetworkConnect|EID 3]] | [[Abanico de conexiones fallidas desde un host]] |
| Identificación de servicio web | [[Log de acceso del servidor web|acceso web]] | [[Ráfaga de errores del servidor desde un mismo origen]] |

La asimetría que ordena todo: **el escaneo se ve mucho mejor en el que escanea que en el escaneado**. Un sondeo `SYN` no completa el handshake, así que no llega a ninguna aplicación y no hay log de servicio que lo registre. La señal está en el tráfico saliente del host que corre la herramienta — lo que sirve cuando el atacante ya está adentro y no sirve en absoluto cuando escanea desde afuera.

Todas las detecciones del dominio son `forma: agregado` por la misma razón: una conexión rechazada no es anómala, la distribución de cien sí. Ver [[La detección vive en el agregado, no en el evento]].

## Huecos conocidos

- **Escaneo desde fuera del parque instrumentado**: sin cubrir, y no es por falta de regla sino de fuente. Pide telemetría de flujo —NetFlow, conntrack, VPC flow logs—, el hueco de `550-telemetria/` anotado en [[MOC - Red]].
- **Barrido ARP**: invisible para la telemetría de endpoint. Necesita DAI en el switch o un sensor pasivo en el segmento.
- **Reconocimiento pasivo** —lo que se averigua sin mandar un paquete al objetivo— sin escribir. Es otro eje, no otro sondeo.
