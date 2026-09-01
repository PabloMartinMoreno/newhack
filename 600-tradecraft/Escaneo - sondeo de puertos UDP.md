---
tipo: tradecraft
clase: "[[T1046 - Network Service Discovery]]"
eje: sondeo
implementacion: "Enviar datagramas al puerto y clasificar por el ICMP de vuelta o por la respuesta de la aplicación"
opsec: ruidoso
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Sysmon EID 1 - ProcessCreate]]"]
requisitos: [acceso-a-la-red]
coste: alto
alternativas: ["[[Escaneo - sondeo SYN de puertos TCP]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - UDP scan
  - sondeo UDP
tags:
  - dominio/red
---

# Escaneo - sondeo de puertos UDP

## Cuándo lo elijo

Cuando el TCP no dio nada, o cuando busco algo que **sólo vive en UDP**: DNS, SNMP, NetBIOS, Kerberos, IKE, TFTP. Es la mitad del mapa que casi todo el mundo omite por lento, y por eso es donde queda lo no auditado.

La decisión no es *si* escanear UDP sino **cuántos puertos**. Barrer los 65535 en UDP no es una opción realista; se eligen los treinta o cuarenta que tienen servicios reales y se acepta el punto ciego del resto. Esa lista acotada es la que hace la diferencia entre un escaneo de horas y uno de días.

## Por qué funciona

Porque UDP no tiene handshake, así que la clasificación no la da el transporte sino [[ICMP - el canal de error de IP]]: un puerto cerrado se delata con `tipo 3 código 3`, y uno abierto sólo se delata si la aplicación decide contestar.

De ahí la asimetría del sondeo: **cerrado se confirma, abierto se infiere**. El silencio no distingue entre abierto-y-callado y filtrado, y por eso los resultados vienen con estados combinados en vez de una respuesta limpia.

Lo que sí rinde es hablarle a cada servicio en su idioma: un sondeo con una consulta DNS válida al 53 obtiene respuesta donde un datagrama vacío no obtiene nada. Las cargas por puerto están en [[Nmap - matriz de referencia]].

## Cómo falla

Falla por diseño en el caso más común —el silencio ambiguo— y falla por lentitud en el resto. La lentitud no es del escáner: es la **limitación de tasa de errores ICMP** del destino, que obliga a esperar entre sondeos porque si no los `port unreachable` dejan de llegar y los puertos cerrados empiezan a parecer abiertos.

Es el único sondeo del dominio donde apurarse **corrompe el resultado** en vez de sólo hacerlo ruidoso.

## Coste

El más alto del dominio, y es coste de reloj: órdenes de magnitud sobre TCP para el mismo número de puertos. La contrapartida es que lo que aparece suele ser lo que nadie miró — y la lista corta de puertos que vale la pena es lo que vuelve la decisión razonable.
