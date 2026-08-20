---
tipo: tradecraft
clase: "[[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]]"
eje: credencial
implementacion: "Responder a las consultas por difusión de LLMNR/NBT-NS para capturar el NetNTLMv2 de la víctima y romperlo fuera de línea"
opsec: ruidoso
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]"]
requisitos: [acceso-a-la-red-en-el-mismo-dominio-de-difusión]
coste: bajo
alternativas: ["[[Relay de NTLM]]", "[[AS-REP roasting]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - LLMNR poisoning
  - Responder
  - captura de NetNTLMv2
tags:
  - dominio/ad
---

# Envenenamiento de resolución de nombres

## Cuándo lo elijo

Es la primera técnica del pentest interno cuando no se tiene ninguna credencial, solo acceso a la red. Se pone Responder a escuchar y se espera: cualquier fallo de resolución de nombres en la red —constantes en un entorno real— se convierte en un NetNTLMv2 capturado.

El objetivo es conseguir la **primera credencial**: capturar un hash y romperlo fuera de línea. Si la contraseña es fuerte y no se rompe, o si se quiere escalar sin depender de romper nada, la rama es [[Relay de NTLM]] —el mismo hash capturado, reenviado en vez de roto—. Es la alternativa a [[AS-REP roasting]] como primer paso sin credencial.

## Por qué funciona

Cuando DNS no resuelve un nombre, Windows pregunta por difusión con LLMNR y NBT-NS, sin autenticar quién responde. Responder contesta a todas las consultas afirmando ser el host buscado, y la víctima se autentica hacia él:

1. La víctima intenta llegar a `\\servidor-inexistente` —un recurso viejo, un error de tipeo, un mapeo automático—.
2. DNS falla; Windows pregunta por difusión.
3. Responder contesta "ese soy yo".
4. La víctima se autentica, mandando su usuario y un **NetNTLMv2** —el desafío-respuesta—.
5. El hash se rompe fuera de línea: `hashcat -m 5600`.

Los eventos que más disparan capturas: recursos compartidos mapeados que ya no existen, errores de tipeo en rutas UNC, y —el más jugoso— **coacción activa**, forzar a una máquina a autenticarse (el mismo `PetitPotam`/printer bug de [[Delegación sin restricciones]]) en vez de esperar. Los comandos están en [[AD envenenamiento y relay - matriz de referencia]].

El NetNTLMv2 **no es reutilizable** como un hash NTLM —no sirve para [[Pass-the-hash]]—: solo se rompe o se retransmite. Es la diferencia que decide entre esta rama (romper) y [[Relay de NTLM]] (retransmitir).

## Cómo falla

Falla cuando **LLMNR y NBT-NS están deshabilitados** por directiva de grupo: sin la caída a difusión, no hay consultas que envenenar. Es la mitigación directa y cada vez más común en entornos maduros.

Falla cuando la contraseña capturada es **fuerte**: el NetNTLMv2 no se rompe en tiempo razonable, y la captura no rinde. Ahí el relay es la salida, porque no depende de romper.

Y falla si el atacante no está en el mismo dominio de difusión que las víctimas —una red segmentada—: la difusión no cruza subredes.

## Coste

Bajo. Poner Responder es un comando y esperar. Con coacción, se fuerza la captura en vez de esperar, y es casi inmediato.

El costo variable es romper el hash: depende de la fortaleza de la contraseña, como en [[Kerberoasting]]. Una cuenta de servicio o un usuario con contraseña débil cae rápido; una fuerte no cae, y hay que pasar al relay.

## Huella esperada

Ruidosa en la red, y con una señal de host aprovechable:

- La víctima **se conecta al host del atacante** tras el fallo de resolución, lo que deja una [[Sysmon EID 3 - NetworkConnect]] hacia una IP que no es un servidor legítimo. Es la señal más directa: un endpoint conectándose a un host de resolución de nombres no autorizado, que cubre [[Conexión a host de resolución de nombres no autorizado]].
- Los intentos de autenticación fallidos —cuando el NetNTLMv2 no completa un login real— pueden dejar [[Windows 4625 - Failed logon]].

La captura y el crack posterior son **fuera de línea e invisibles**, igual que en kerberoasting: no hay nada que ver mientras se rompe el hash. La única ventana de detección es el momento del envenenamiento —la conexión anómala al host del atacante—, no el uso posterior. Es el mismo principio que el resto de AD: cuando el ataque es fuera de línea, se detecta la petición, no el ataque. Anotado en [[MOC - Active Directory]].
