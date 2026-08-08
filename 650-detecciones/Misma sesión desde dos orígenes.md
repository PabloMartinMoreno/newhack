---
tipo: deteccion
tecnicas: ["[[CWE-522 - Insufficiently Protected Credentials]]", "[[CWE-384 - Session Fixation]]"]
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Log de acceso del servidor web]]"]
forma: correlacion
ventana: 
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - sesión compartida
  - viaje imposible de sesión
tags:
  - dominio/web
---

# Misma sesión desde dos orígenes

## Qué detecta

Un mismo identificador de sesión usado desde dos orígenes distintos, especialmente si la separación geográfica es incompatible con el tiempo transcurrido.

Es **la detección de mayor retorno de [[MOC - Gestión de sesión]]**, y por dos razones: funciona sin instrumentar nada nuevo —el identificador de sesión y la IP ya están en cualquier registro— y cubre a la vez [[Sesión - robo de token]] y [[Sesión - fijación]], que es la única detección del vault que atrapa dos técnicas distintas con la misma condición.

Que no las distinga no es un defecto: al defensor le importa que la sesión esté comprometida, no cómo llegó a estarlo.

## Lógica

```
actividad_sesion
| summarize
    origenes = dcount(client_ip),
    paises = dcount(pais),
    primera = min(timestamp),
    ultima = max(timestamp)
  by session_id
| where origenes > 1
| where paises > 1 or (ultima - primera) < 5m
```

Refinamiento de viaje imposible, que es el que sube la fidelidad a casi perfecta: calcular la distancia entre los dos orígenes y la diferencia de tiempo, y alertar si la velocidad implícita es imposible.

```
| extend km = geo_distance(ip1, ip2), horas = (t2 - t1) / 1h
| where km / horas > 900
```

Complemento barato: **cambio de agente de usuario** dentro de la misma sesión. Un navegador no cambia de identidad a mitad de sesión.

## Falsos positivos conocidos

- **Móvil cambiando de red** — de wifi a datos y de vuelta, con IP de operador que puede geolocalizar lejos. Es el falso positivo dominante y el que obliga al refinamiento por velocidad en lugar de por simple diferencia de IP.
- **VPN corporativa** que se conecta y desconecta.
- **Redes con IP dinámica** o balanceo entre salidas.
- **Geolocalización de IP imprecisa**, especialmente en operadores móviles y en direcciones de nube.
- **Usuarios que legítimamente viajan** con una sesión persistente.

Los umbrales de velocidad y ventana hay que calibrarlos: en una población con mucho trabajo remoto y móvil, la fidelidad baja bastante.

## Evasiones conocidas

- **Usar el token desde la misma red que la víctima**, o desde el mismo país. Anula la condición geográfica y deja solo el agente de usuario.
- **Copiar el agente de usuario** de la víctima, que un atacante con XSS obtiene junto con el token.
- **Esperar a que la víctima no esté activa**, lo que evita el solapamiento temporal y deja solo la señal geográfica.
- **[[Sesión - token predecible]]** la evade parcialmente: el atacante usa una sesión que la víctima nunca usó, así que no hay dos orígenes para el mismo token. Contra esa variante hay que detectar la **recolección**, no el uso.
- **[[Sesión - falsificación de JWT]]** también: el token forjado nunca perteneció a nadie. Su detección es otra — actividad de una cuenta sin evento de acceso previo.

## Cómo se prueba

Disparador: [[Sesión - robo de token]] en laboratorio, usando el mismo token desde dos redes.

Es forma `correlacion` y se valida con un caso. Lo que necesita calibración no es la regla sino los umbrales, y eso pide la línea base de movilidad real de los usuarios.
