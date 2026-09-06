---
tipo: teoria
habilita: ["[[Exfiltración por canal encubierto]]"]
relacionadas: ["[[Exfiltración por subdominios de alta entropía]]", "[[TCP - establecimiento de la conexión]]"]
aliases:
  - DNS
  - resolución recursiva
  - resolutor recursivo
tags: []
---

# DNS - resolución recursiva

## Qué dice la especificación

DNS traduce nombres a datos (IP y más) sobre una base **jerárquica y distribuida**: nadie tiene la tabla entera, cada zona la sirve su servidor **autoritativo**. Resolver un nombre es recorrer el árbol desde la raíz.

La cadena, cuando un cliente pide `www.ejemplo.com`:

1. El **stub resolver** del cliente pregunta a su **resolutor recursivo** (el que dan DHCP/`/etc/resolv.conf`).
2. El recursivo, si no lo tiene cacheado, pregunta a un servidor **raíz** → le devuelve el de `.com` (TLD).
3. Pregunta al TLD `.com` → le devuelve el autoritativo de `ejemplo.com`.
4. Pregunta al autoritativo → le devuelve el registro. El recursivo lo **cachea** por el TTL y se lo pasa al cliente.

La distinción clave: el cliente pide **recursión** (resolvémelo entero); el recursivo hace **iteración** (va saltando de servidor en servidor). Sobre UDP 53 por defecto; pasa a TCP 53 cuando la respuesta supera el límite o para transferencia de zona.

## Dónde el estándar deja lugar

- **El recursivo persigue cualquier nombre hasta su autoritativo.** No importa que el nombre sea absurdo o de alta entropía: si no está cacheado, va a buscarlo. Esa obediencia es el canal encubierto — quien controla el autoritativo de un dominio recibe lo que sea que se consulte bajo él.
- **A quién le hace recursión** es política: un recursivo abierto responde a cualquiera; uno cerrado, solo a su red. Un interno sin salida no llega a autoritativos externos.
- **El caché y el TTL** son superficie propia: envenenar una entrada cacheada afecta a todos los que usan ese recursivo hasta que expira.

## Qué habilita

- **La exfiltración por DNS.** [[Exfiltración por canal encubierto]] funciona **por esto**: aunque el host no tenga ninguna salida directa, si resuelve nombres, su recursivo reenvía la consulta por la cadena hasta el autoritativo del atacante. Los datos van codificados en las etiquetas del subdominio y llegan sin una conexión directa. Si el recursivo es solo interno y sin salida, el canal se corta — el límite exacto que anota esa nota.
- **La detección vive en el mismo lugar.** Los subdominios de alta entropía que genera el túnel son justo lo que ancla [[Exfiltración por subdominios de alta entropía]] — el caso raro donde la firma rinde.

## Cómo se ve en la práctica

Cada consulta con su proceso, en [[Sysmon EID 22 - DnsQuery]]; la consulta saliente, en [[Consulta DNS saliente]]. La recursión se ve como el host hablando **solo con su recursivo** —no con los autoritativos—: el salto por la cadena lo hace el recursivo, no el endpoint. Por eso la telemetría de host ve el nombre consultado y el volumen, no la topología de la resolución.

## Fuente

- RFC 1034 / 1035 (DNS: conceptos y formato).
