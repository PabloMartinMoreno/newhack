---
tipo: deteccion
tecnicas: ["[[CWE-307 - Improper Restriction of Excessive Authentication Attempts]]"]
telemetria: ["[[Log de autenticación de la aplicación]]"]
forma: agregado
ventana: "1h"
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - detección de credential stuffing
tags:
  - dominio/web
---

# Accesos exitosos contra muchas cuentas desde un origen

## Qué detecta

Un mismo origen autenticando **con éxito** contra varias cuentas sin relación entre sí.

Existe porque [[Autenticación - credential stuffing]] rompe la premisa sobre la que está construida toda la defensa de autenticación: **acierta a la primera y no genera fallos**. No hay umbral que cruzar, no hay contador que suba, no hay bloqueo que disparar. Para cualquier regla basada en intentos fallidos, este ataque no ocurre.

La única señal es el éxito mismo, mirado en agregado. Ninguna persona autentica contra cinco cuentas distintas desde una IP en una hora.

## Lógica

```
autenticacion
| where timestamp > ago(1h)
| where resultado == 'exito'
| summarize cuentas = dcount(cuenta), accesos = count() by origen_ip
| where cuentas >= 5
```

El umbral de cinco es bajo a propósito: el coste de un falso positivo acá es una revisión manual, y el de un falso negativo es una toma de cuentas masiva.

Regla complementaria, por cuenta, para cuando el ataque viene distribuido y la de arriba no dispara:

```
autenticacion
| where resultado == 'exito'
| join kind=leftanti (historico_por_cuenta) on cuenta, origen_asn
| where pais !in (paises_habituales_de_la_cuenta)
    or agente_usuario !in (agentes_habituales_de_la_cuenta)
```

Es la detección por **cambio de patrón respecto del histórico de cada cuenta**, y es lo único que queda contra un atacante que distribuye bien. Es cara —necesita el histórico— y es la que de verdad funciona.

## Falsos positivos conocidos

- **NAT corporativo**: una oficina entera sale por una IP y autentica contra decenas de cuentas legítimamente. Es el falso positivo dominante y la razón por la que la regla necesita una lista de rangos propios.
- **VPN corporativa**, mismo efecto.
- **Aplicaciones móviles detrás del NAT de un operador**.
- **Administradores probando cuentas**, o herramientas de soporte que suplantan usuarios.
- **Servicios de agregación** autorizados por el usuario, que acceden en su nombre.

Sin la lista blanca de rangos propios esta regla es inutilizable. Construirla es el trabajo previo.

## Evasiones conocidas

- **Distribuir el origen**, que es la práctica estándar en este ataque: proxies residenciales, una IP por intento. Anula la primera regla por completo. Contra eso solo sirve la segunda.
- **Bajar el ritmo** por debajo del umbral, a costa de tardar semanas.
- **Imitar el agente de usuario y la geografía** de la víctima, que evade también la segunda regla. Es caro y se hace en ataques dirigidos.
- **MFA no la evade**: la vuelve irrelevante, porque el ataque deja de funcionar. Es la mitigación real y esta regla es lo que queda mientras no esté.

## Cómo se prueba

Disparador: [[Autenticación - credential stuffing]] en laboratorio, con varias cuentas de prueba y credenciales conocidas.

Forma `agregado`. La parte que hay que validar no es que dispare —eso es fácil— sino **cuántas veces dispara sin ataque**, que depende enteramente de la topología de red del cliente.
