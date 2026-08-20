---
tipo: deteccion
tecnicas: ["[[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]]"]
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]"]
forma: correlacion
ventana: 
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - detección de LLMNR poisoning
tags:
  - dominio/ad
---

# Conexión a host de resolución de nombres no autorizado

## Qué detecta

Un endpoint que, tras una consulta de resolución de nombres por difusión, se **autentica o conecta a un host que no es un servidor legítimo**. Es la firma de [[Envenenamiento de resolución de nombres]] vista desde el endpoint de la víctima: el envenenamiento redirige la conexión a la máquina del atacante, y esa conexión hacia una IP que no está en el inventario de servidores es la anomalía.

Es la única ventana de detección del envenenamiento, porque la captura y el crack del NetNTLMv2 son fuera de línea e invisibles. Como todo lo de AD fuera de línea: se detecta la conexión, no el ataque.

## Lógica

```kql
DeviceNetworkEvents
| where Timestamp > ago(1h)
| where RemotePort in (445, 139)                        // SMB, donde llega la auth
| where InitiatingProcessFileName in~ ("System","lsass.exe","explorer.exe")
| where RemoteIP !in (ListaServidoresConocidos)         // no es un servidor legítimo
| where RemoteIP !startswith "10.0.0."                  // ajustar a los rangos de servidores reales
| summarize conexiones = count(), destinos = make_set(RemoteIP)
    by DeviceName, bin(Timestamp, 5m)
```

La clave es la **lista blanca de servidores conocidos**: una conexión SMB de un endpoint a un host que no es un servidor de archivos ni un DC no tiene explicación legítima —esos son justamente los destinos que el envenenamiento suplanta—. Sin la lista blanca la regla es inservible por ruido; con ella, la conexión a un host desconocido es el ataque casi con certeza.

`forma: correlacion` porque la señal fuerte es el fallo de resolución (DNS que no resuelve) **seguido** de la conexión al host rogue. Si se instrumenta el DNS ([[Sysmon EID 22 - DnsQuery]]), correlacionar "consulta DNS fallida → conexión SMB a IP no-servidor" sube mucho la fidelidad.

## Por qué la fidelidad es media

Una conexión SMB a un host que no está en la lista blanca ocurre legítimamente: un recurso compartido nuevo, una impresora, un servidor no inventariado. Por eso la regla necesita línea base y curación de la lista de servidores conocidos. No es de alta fidelidad como la de RBCD —donde el atributo casi nunca se escribe—; acá el tráfico SMB es normal y lo anómalo es el destino.

## Falsos positivos conocidos

- **Servidores no inventariados** — la lista blanca incompleta genera falsos. Mantenerla es el trabajo de la regla.
- **Recursos compartidos nuevos o temporales** entre estaciones.
- **Impresoras y dispositivos** que hablan SMB.

## Evasiones conocidas

- **Envenenar solo con relay inmediato**, sin dejar que la conexión persista: la conexión igual ocurre y deja el evento, pero de forma más breve.
- **Coacción a un objetivo específico** en vez de envenenamiento amplio: menos ruido, misma conexión anómala.
- La **captura pasiva** con Responder deja la conexión de la víctima igual; lo que no se ve es el crack posterior, que es fuera de línea.

## Cómo se prueba

Disparador: [[Envenenamiento de resolución de nombres]] con Responder en un laboratorio, y una víctima que intente resolver un nombre inexistente.

`forma: correlacion` — se valida con el par consulta-fallida + conexión-anómala, no con un evento suelto. Necesita la lista blanca de servidores curada antes de que la regla sirva.
