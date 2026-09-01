---
tipo: deteccion
tecnicas: ["[[T1046 - Network Service Discovery]]", "[[T1018 - Remote System Discovery]]"]
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Sysmon EID 1 - ProcessCreate]]"]
forma: agregado
ventana: "5m"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - detección de escaneo de puertos
  - port scan detection
tags:
  - dominio/red
---

# Abanico de conexiones fallidas desde un host

## Qué detecta

Un proceso que intenta conectarse a **muchos pares IP:puerto distintos en poco tiempo**, con la mayoría de los intentos sin prosperar. Es la firma de [[Escaneo - sondeo SYN de puertos TCP]] y de [[Escaneo - descubrimiento de hosts]] vista desde el host que escanea, no desde el escaneado.

Esa elección de punto de vista no es preferencia: es donde está la señal. El host escaneado casi no ve nada —un sondeo `SYN` no completa el handshake y por lo tanto no llega a ninguna aplicación—, mientras que el que escanea genera un patrón de tráfico saliente que no se parece a nada legítimo.

## Lógica

Agregación por proceso y ventana corta, sobre cardinalidad de destinos y no sobre volumen de eventos:

```kql
DeviceNetworkEvents
| where Timestamp > ago(1h)
| summarize
    destinos = dcount(strcat(RemoteIP, ":", RemotePort)),
    ips      = dcount(RemoteIP),
    fallidos = countif(ActionType == "ConnectionFailed"),
    total    = count()
    by InitiatingProcessId, InitiatingProcessFileName, DeviceName, bin(Timestamp, 5m)
| where destinos > 50 and todouble(fallidos) / total > 0.7
```

Los dos umbrales son la regla, y ninguno funciona solo: la cardinalidad separa el escaneo de un cliente que habla mucho con un solo servidor, y la proporción de fallos lo separa de un proceso legítimamente hablador —un navegador, un agente de monitoreo— que también toca muchos destinos pero acierta casi siempre.

Los números concretos son de arranque y hay que ajustarlos contra el entorno: sin línea base no significan nada, ver [[Sin línea base no hay anomalía]].

## Falsos positivos conocidos

- **Escáneres de vulnerabilidades y agentes de inventario autorizados.** Son el falso positivo dominante y la única mitigación que funciona es una lista de hosts y procesos autorizados, mantenida.
- **Descubrimiento de red legítimo**: sistemas de monitoreo, orquestadores, backup.
- **Navegadores y clientes P2P** con muchos destinos pero baja proporción de fallo — los saca el segundo umbral.
- **Un servidor recién levantado** cuyos destinos todavía no responden.

## Evasiones conocidas

- **Bajar la velocidad por debajo de la ventana.** Un escaneo repartido en horas cae por debajo de cualquier umbral de cinco minutos. Es la evasión estructural del `forma: agregado` y no se resuelve subiendo la sensibilidad: se resuelve con una segunda ventana larga y umbral más bajo.
- **Acotar el objetivo.** Sondear cinco puertos elegidos en vez de mil no dispara nada, y es lo que hace un atacante que ya sabe qué busca.
- **Escanear desde fuera del parque instrumentado**, que anula la regla entera. Cubrir ese caso exige telemetría de flujo, que hoy el vault no modela — el hueco anotado en [[MOC - Red]].
- **Usar un proceso confiable** como origen, si el umbral se afloja por nombre de imagen.

## Cómo se prueba

Correr un barrido acotado desde un host instrumentado de laboratorio y verificar que la agregación dispara. Un disparador único no valida nada acá: como toda regla de agregado, necesita volumen y una línea base del entorno antes de tener un umbral defendible. Ver [[Detección por forma - matriz de referencia]].
