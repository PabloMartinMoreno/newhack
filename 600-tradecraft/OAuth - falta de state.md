---
tipo: tradecraft
clase: "[[CWE-352 - Cross-Site Request Forgery]]"
eje: fase-del-flujo
implementacion: "Entregar a la víctima un código de autorización propio para que su cuenta quede vinculada a la identidad del atacante"
opsec: ruidoso
telemetria: ["[[Log de auditoría de la aplicación]]", "[[Log de autenticación de la aplicación]]"]
requisitos: [sin-parametro-state, funcion-de-vinculacion-de-cuenta]
coste: bajo
alternativas: ["[[OAuth - redirect_uri mal validado]]", "[[CSRF - token ausente o no ligado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - account linking CSRF
  - OAuth sin state
tags:
  - dominio/web
---

# OAuth - falta de state

## Cuándo lo elijo

Cuando la petición de autorización no lleva `state`, o lo lleva y no se comprueba al volver. Se ve en dos peticiones: se mira la URL de autorización, y si el parámetro está, se cambia su valor y se observa si el cliente protesta.

Es la rama más barata del dominio y la que más veces está presente, porque `state` es opcional en la especificación y muchas bibliotecas lo dejan librado al que integra.

El objetivo natural es la función de **vincular una cuenta social a una cuenta existente**, que es donde el impacto se vuelve serio. Si la aplicación no tiene esa función, el hallazgo baja a inicio de sesión forzado y la severidad cae bastante.

## Por qué funciona

`state` es el token anti-CSRF del flujo de OAuth. Sin él, la petición de retorno —la que trae el código— es una petición de origen cruzado como cualquier otra, y el cliente la procesa porque llega con la sesión de la víctima.

La inversión respecto de lo que se espera es la parte que hay que entender: **el atacante no roba el código de la víctima, le entrega el suyo**. Inicia el flujo con su propia identidad social, se queda con el código sin canjearlo, y hace que la víctima —ya autenticada en la aplicación— visite la dirección de retorno con ese código.

El cliente canjea el código, obtiene la identidad del atacante, y la vincula a la cuenta que tiene la sesión abierta: la de la víctima. A partir de ahí el atacante entra a la cuenta de la víctima con su propio inicio de sesión social, sin contraseña y sin segundo factor.

Es exactamente [[CSRF - token ausente o no ligado]] aplicado al flujo de OAuth, y por eso la `clase:` de esta nota es la de CSRF y no una de OAuth: la vulnerabilidad es la falta de token anti-CSRF, el flujo de OAuth es el vector.

La variante sin función de vinculación es el **inicio de sesión forzado**: autenticar a la víctima en la cuenta del atacante para que su actividad quede registrada donde el atacante la lee. Mismo criterio que el CSRF de inicio de sesión del [[MOC - CSRF]].

## Cómo falla

Falla cuando `state` existe, está ligado a la sesión del navegador y se compara al volver. Son las tres condiciones juntas: un `state` aleatorio que no se guarda contra la sesión no prueba nada, igual que un token de CSRF no ligado.

Falla cuando la vinculación pide reautenticación —la contraseña actual— antes de asociar la identidad externa. Es la mitigación de fondo y la que sobrevive incluso a un XSS.

Y falla, en el sentido de que el impacto se desploma, cuando la aplicación no permite tener más de una identidad vinculada o cuando avisa por correo de cada vinculación nueva.

## Coste

Bajo. Dos peticiones para confirmar que `state` no se valida, y la cadena completa son cuatro pasos que se preparan en una página propia.

El requisito caro no es técnico: la víctima tiene que estar autenticada y abrir el enlace. Como en todo el dominio de CSRF, eso pone un techo real a la severidad y hay que decirlo en el informe en vez de reportarlo como toma de cuenta directa.

## Huella esperada

La señal está en [[Log de auditoría de la aplicación]] y es de las más claras del vault: **una identidad externa vinculada a una cuenta sin que el usuario haya pasado por la pantalla de configuración**. La acción existe y la navegación que debería precederla, no.

Es el mismo perfil que cubre [[Cambio de privilegio fuera del flujo administrativo]], y la regla la ve sin saber que hubo OAuth de por medio: un cambio de estado sensible fuera de su flujo.

En [[Log de autenticación de la aplicación]] queda además una asociación que llama la atención al mirarla: **la misma identidad externa vinculada a dos cuentas distintas**, o inicios de sesión de una cuenta desde una identidad social recién agregada. Ninguna de las dos alerta sola; las dos son buenos puntos de partida para cazar hacia atrás.
