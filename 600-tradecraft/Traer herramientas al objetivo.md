---
tipo: tradecraft
clase: "[[T1105 - Ingress Tool Transfer]]"
eje: ingress
implementacion: "Subir binarios/scripts al host comprometido por el canal que el entorno permita"
opsec: ruidoso
telemetria: ["[[Sysmon EID 1 - ProcessCreate]]", "[[Sysmon EID 3 - NetworkConnect]]"]
requisitos: [ejecucion-de-codigo]
coste: bajo
alternativas: []
probado: nunca
contexto: [win11-defender, ubuntu22-auditd]
aliases:
  - ingress de herramientas
tags:
  - dominio/post-explotacion
---

# Traer herramientas al objetivo

## Cuándo lo elijo

Apenas tengo ejecución y necesito algo que no está en el host. La decisión no es *cómo descargar* sino **qué canal me deja el entorno**, y se resuelve en ese orden:

1. **Hay salida a internet** → descarga directa con la utilidad que exista (`curl`, `certutil`, `wget`, `Invoke-WebRequest`). Lo más rápido.
2. **No hay internet pero alcanzo mi box** → sirvo el archivo desde mi máquina y lo traigo: SMB (`impacket-smbserver`) o un HTTP efímero (`python -m http.server`).
3. **Egress filtrado** → no es un problema de transferencia sino de canal: pivotar, o traer el binario codificado por el canal que quede (ver [[Exfiltración por canal encubierto]] al revés).

Los comandos de cada vía, por sistema, en [[Transferencia de archivos - matriz de referencia]].

## Por qué funciona

Las utilidades firmadas del sistema tienen capacidad de red, y el defensor no puede bloquearlas sin romper el SO: es el principio **LOLBin** (living off the land). `certutil` descarga certificados —y cualquier archivo—; `bitsadmin` agenda transferencias; PowerShell y Python son clientes HTTP completos. Ninguno requiere instalar nada.

Cuando no hay internet, SMB y HTTP servidos desde el box del atacante convierten la falta de salida en un problema de alcanzar una sola IP: la tuya.

## Cómo falla

- **Application allowlisting** que impide ejecutar binarios no aprobados, o que restringe los intérpretes.
- **EDR** con reglas sobre LOLBins: `certutil` con una URL en la línea de comando es una firma conocida — ver [[Descarga de herramienta por utilidad del sistema]].
- **Egress totalmente cerrado** y sin ruta al box del atacante: no hay canal, hay que pivotar primero.
- Host mínimo sin ninguna utilidad de red ni intérprete (raro, pero pasa en contenedores).

## Coste

Bajo. Un comando. El costo real no es esfuerzo sino **opsec**: casi toda vía de ingress deja una utilidad del sistema haciendo algo que normalmente no hace —conectarse a una IP externa y escribir un ejecutable—, que es exactamente lo que la telemetría de endpoint busca.

## Huella esperada

- La utilidad con una URL o IP en la línea de comando, en [[Sysmon EID 1 - ProcessCreate]] — la firma que cubre [[Descarga de herramienta por utilidad del sistema]].
- La conexión saliente, en [[Sysmon EID 3 - NetworkConnect]].
- El archivo nuevo en disco, en [[Sysmon EID 11 - FileCreate]].
