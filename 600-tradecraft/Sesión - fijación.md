---
tipo: tradecraft
clase: "[[CWE-384 - Session Fixation]]"
eje: fallo
implementacion: "Fijar un identificador conocido antes de que la víctima se autentique"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [sin-rotacion-al-autenticar, via-para-fijar-el-token]
coste: medio
alternativas: ["[[Sesión - robo de token]]"]
probado: 2026-08-08
contexto: [web-generica]
aliases:
  - fijar el identificador
tags:
  - dominio/web
---

# Sesión - fijación

## Cuándo lo elijo

Cuando la aplicación **no rota el identificador de sesión al autenticar** y hay alguna vía para poner un token en el navegador de la víctima. Las dos condiciones son necesarias: la primera se verifica en treinta segundos, la segunda es la que suele faltar.

Se comprueba así: pedir la página de acceso sin autenticar, anotar el identificador, autenticarse, y comparar. Si es el mismo, hay fijación.

Frente a [[Sesión - robo de token]], la diferencia es de requisitos, no de resultado. El robo necesita capturar algo que existe —XSS, red, un descuido—; la fijación necesita **escribir** algo antes. Cuando hay un XSS disponible, el robo es más directo y esta técnica sobra.

## Por qué funciona

Porque la aplicación emite sesión antes de saber quién es el usuario, y después le agrega la identidad **al mismo identificador** en vez de emitir uno nuevo. El atacante no necesita robar nada: aporta el token y espera a que la víctima lo cargue de valor autenticándose.

Es un ataque sobre el ciclo de vida del identificador, no sobre su confidencialidad, y por eso las defensas habituales no aplican: `HttpOnly` impide leer la cookie, no impide ponerla.

La vía realista hoy es la **escritura de cookie desde un subdominio**. Una cookie con dominio del padre se escribe desde cualquier subdominio, lo que convierte un subdominio olvidado, de un tercero o comprometido en superficie de este ataque. La vía clásica —identificador aceptado por query string— casi no existe ya.

## Cómo falla

- **Rotación al autenticar** — la mitigación, y es una línea en casi todos los marcos de trabajo. Cierra la clase entera.
- **La aplicación no adopta identificadores desconocidos** — si llega uno que el servidor no emitió, lo descarta y emite otro. Igual de efectivo.
- **`__Host-` como prefijo del nombre de la cookie** — el navegador la rechaza si tiene atributo de dominio, lo que impide escribirla desde un subdominio. Barato y muy poco usado.
- **No hay subdominio ni parámetro por donde fijar** — hay fallo y no hay vía. Sigue siendo reportable, con severidad menor.
- **Requiere que la víctima se autentique después.** Es la limitación práctica: hay que fijar y esperar, lo que implica ingeniería social y una ventana de tiempo.

## Coste

Medio, y casi todo en la entrega. Verificar el fallo cuesta una prueba; **explotarlo cuesta conseguir que una persona use el token fijado y se autentique**, que es la parte incierta y la que suele exceder el alcance de una prueba técnica.

## Un límite operativo

> [!warning] Explotarlo requiere una víctima real
> Demostrar que el identificador no rota es un hallazgo completo y se prueba con la cuenta propia. Fijar un token en el navegador de un empleado y esperar a que entre es ingeniería social sobre una persona.
>
> Se documenta el fallo con la prueba de la cuenta propia y se describe la cadena; se ejecuta contra terceros solo si el engagement lo autoriza explícitamente.

## Huella esperada

- [[Log de autenticación de la aplicación]] con un acceso exitoso cuyo identificador de sesión **ya existía antes** del evento. Detectarlo requiere registrar el identificador antes y después, que casi nadie hace.
- El mismo identificador de sesión usado desde **dos orígenes distintos** —el del atacante que lo fijó y el de la víctima que se autenticó—. Es la señal más práctica, y es la misma que delata el robo de sesión: no distingue una técnica de la otra, y para el defensor esa distinción tampoco importa mucho.
- Si la fijación fue por parámetro en la URL, [[Log de acceso del servidor web]] lo tiene entero.

Las pruebas concretas están en [[Sesión - matriz de referencia]] § Fijación.
