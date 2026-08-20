---
tipo: tradecraft
clase: "[[T1558 - Steal or Forge Kerberos Tickets]]"
eje: lateral
implementacion: "Extraer la clave de la confianza y forjar un TGT de referencia inter-reino para autenticarse en el dominio o bosque que confía"
opsec: requiere-bypass
telemetria: ["[[Windows 4769 - Kerberos service ticket requested]]", "[[Windows 4624 - Successful logon]]"]
requisitos: [admin-de-dominio, una-confianza-saliente-explotable]
coste: medio
alternativas: ["[[Escalada intra-bosque por SID History]]", "[[Golden ticket]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - inter-realm TGT
  - trust key abuse
  - trust ticket
tags:
  - dominio/ad
---

# Movimiento entre bosques por la clave de confianza

## Cuándo lo elijo

Cuando ya soy administrador de un dominio y la enumeración muestra una **confianza** hacia otro dominio o bosque, y quiero moverme a través de ella. Es la vía entre bosques distintos, donde el filtrado de SID bloquea la escalada por SID History de [[Escalada intra-bosque por SID History]].

La elijo para cruzar el límite de confianza usando la relación misma como puente. Dentro del mismo bosque, el SID History es más directo; entre bosques, o cuando quiero un ticket de referencia limpio, esta es la rama.

## Por qué funciona

Cada confianza tiene una **clave** —la contraseña de la cuenta de confianza, que los dos dominios comparten para firmar los tickets que cruzan—. Con acceso de administrador al dominio de origen se extrae esa clave (por [[DCSync]] del objeto de confianza `DOMINIO$`), y con ella se **forja un TGT de referencia inter-reino**: el ticket que un dominio le da a un usuario para pedir servicios en el dominio que confía.

La cadena:

1. DCSync para sacar la clave de la confianza —el hash de la cuenta `DOMINIO-CONFIABLE$`—.
2. Forjar un TGT de referencia inter-reino firmado con esa clave, a nombre de un usuario del dominio de origen.
3. Presentarlo al dominio que confía para pedir tickets de servicio ahí.

El dominio que confía acepta el ticket porque está firmado con la clave que comparten. El comando —`ticketer.py` con `-domain` y `-domain-sid` del origen apuntando al destino, o Rubeus— está en [[AD confianzas - matriz de referencia]].

Un detalle sobre el alcance según el tipo y la dirección de la confianza: una confianza **saliente** (el otro confía en mí) es la explotable para entrar allá; una **entrante** deja que el otro entre a lo mío. Y el **filtrado de SID entre bosques** limita qué se puede hacer una vez cruzado —no se puede inyectar el SID de un grupo privilegiado del bosque destino—, así que el acceso es como el usuario forjado, no como administrador del destino, salvo que el filtrado esté mal configurado.

## Cómo falla

Falla cuando el filtrado de SID entre bosques está bien configurado —el defecto— y además el destino no tiene recursos accesibles al usuario que se puede forjar: se cruza, pero sin privilegio útil.

Falla contra confianzas **selectivas** (`selective authentication`), donde el destino exige que cada cuenta tenga permiso explícito para autenticarse, no basta con cruzar la confianza.

Y presupone administrador del dominio de origen para sacar la clave: como la escalada por SID History, es un paso de movimiento tras el compromiso, no de acceso inicial.

## Coste

Medio. Sacar la clave de la confianza es un DCSync dirigido; forjar el TGT inter-reino es un comando. Lo que agrega costo es el reconocimiento de la confianza —dirección, tipo, si el filtrado está activo, qué hay del otro lado— porque decide si el cruce rinde o deja en un dominio sin nada útil.

El impacto es muy variable: entre bosques con filtrado, acceso limitado; contra una confianza mal configurada o dentro de un modelo laxo, puede ser control del destino.

## Huella esperada

Requiere-bypass, con la señal en los tickets que cruzan:

- El TGT de referencia forjado y su uso dejan [[Windows 4769 - Kerberos service ticket requested]] en el dominio destino, con un ticket inter-reino cuyo origen es el dominio confiado. La anomalía es de contexto: un ticket que cruza la confianza a nombre de una cuenta que no debería estar cruzando, o hacia recursos inusuales.
- El acceso resultante deja [[Windows 4624 - Successful logon]] en el destino, con una identidad del otro dominio.

Como el resto de la forja de tickets, hereda parcialmente las detecciones de golden ([[Ticket de servicio sin ticket inicial previo]]) cuando el ticket forjado no tiene un TGT legítimo previo. Pero la detección específica de abuso de confianza —un ticket inter-reino anómalo por dirección o por cuenta— no tiene regla propia en el vault, y queda como hueco declarado en [[MOC - Active Directory]]. La telemetría (`4769` inter-reino) existe; falta anclar en la relación de confianza. La mitigación de fondo es el filtrado de SID y la autenticación selectiva, que acotan qué puede hacer un ticket que cruza.
