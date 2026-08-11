---
tipo: tradecraft
clase: "[[T1558.003 - Kerberoasting]]"
eje: credencial
implementacion: "Pedir tickets de servicio de cuentas con SPN y romperlos fuera de línea"
opsec: ruidoso
telemetria: ["[[Windows 4769 - Kerberos service ticket requested]]"]
requisitos: [una-credencial-de-dominio, cuentas-de-servicio-con-contraseña-débil]
coste: medio
alternativas: ["[[AS-REP roasting]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - kerberoast
tags:
  - dominio/ad
---

# Kerberoasting

## Cuándo lo elijo

Cuando hay una credencial de dominio cualquiera y la enumeración —[[Enumeración LDAP del directorio]]— mostró cuentas con nombre de servicio registrado que corren bajo una **cuenta de usuario**. Ese detalle es la condición: las cuentas de máquina también tienen nombre de servicio pero su contraseña no se rompe.

Es de las primeras cosas que se prueban en un dominio, porque no necesita privilegios y el ataque de fuerza pasa fuera de línea, donde no hay nada que lo detenga.

## Por qué funciona

Porque cualquier usuario autenticado puede pedir un ticket para cualquier servicio, y ese ticket viene cifrado con la contraseña de la cuenta del servicio. Ver [[T1558.003 - Kerberoasting]].

El material se ataca sin conexión: no hay bloqueo de cuenta, no hay límite de intentos, no hay ninguna señal mientras se rompe. La única parte observable es **pedir los tickets**.

Se fuerza pedir el cifrado más débil disponible —RC4 en vez de AES— porque se rompe mucho más rápido, y muchos dominios lo siguen aceptando por compatibilidad.

## Cómo falla

- **Contraseñas largas y aleatorias** — cuentas de servicio administradas por el directorio. El ticket se pide igual y no se rompe nunca. Es la mitigación real.
- **Solo AES** — encarece muchísimo el ataque fuera de línea.
- **No hay cuentas de servicio bajo usuario** — sin ellas, no hay superficie: solo cuentas de máquina, que no valen la pena.
- **Pedir todo de golpe es ruidoso** — una cuenta pidiendo tickets para decenas de servicios en segundos es exactamente lo que delata. Se puede ir despacio, a costa de tiempo.

## Coste

Medio. Pedir es instantáneo; romper depende de la contraseña — de segundos para una débil a inviable para una fuerte. La incertidumbre está toda del lado del crackeo, y se sabe recién después.

## Huella esperada

Ruidoso en un punto y silencioso en el resto, lo que define dónde detectarlo.

- [[Windows 4769 - Kerberos service ticket requested]] es el artefacto, y tiene dos señales: **tipo de cifrado RC4** en un dominio que soporta AES —degradación deliberada— y **volumen anormal**, una cuenta pidiendo tickets para muchos servicios distintos en poco tiempo.
- La detección es de forma `agregado`: un ticket suelto es rutina, la ráfaga es el ataque. Necesita línea base de cuántos servicios pide un usuario normal, que varía muchísimo entre dominios.
- **El crackeo es invisible**: pasa fuera de línea y no genera nada. Lo siguiente que se ve es un acceso exitoso con la cuenta de servicio ya comprometida, que es la fase posterior.

La ventana de detección es la petición. Después de eso, hasta que la contraseña se use, no hay nada.
