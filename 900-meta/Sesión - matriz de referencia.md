---
tipo: meta
aliases:
  - Pruebas de sesión
  - Atributos de cookie
tags:
  - meta/referencia
  - dominio/web
---

# Sesión - matriz de referencia

> [!info] Referencia pura, no un zettel
> Pruebas del ciclo de vida de la sesión. Casi todo se verifica con la cuenta propia y sin ninguna vulnerabilidad previa. JWT tiene matriz aparte: [[JWT - matriz de referencia]]. El criterio está en [[MOC - Gestión de sesión]].

## Atributos

```
Set-Cookie: sid=abc; HttpOnly; Secure; SameSite=Lax; Path=/
```

| Atributo | Si falta | Habilita |
|---|---|---|
| `HttpOnly` | script lee la cookie | robo por XSS |
| `Secure` | viaja sin cifrar | captura en red |
| `SameSite` | se envía entre sitios | CSRF |
| `Domain` presente | la reciben los subdominios | robo y fijación desde subdominio |
| `Expires`/`Max-Age` largo | persiste tras cerrar el navegador | reutilización en equipo compartido |

Prefijos de nombre, baratos y casi nunca usados:

```
__Secure-sid    exige Secure
__Host-sid      exige Secure, Path=/, y PROHÍBE Domain
```

`__Host-` es el que cierra la escritura desde subdominios, que es la vía realista de [[Sesión - fijación]].

Y la pregunta que muchas veces vuelve irrelevante toda esta tabla: **¿el token está en el almacenamiento del navegador en vez de en una cookie?** Ahí es siempre legible por script y `HttpOnly` no existe como concepto.

## Análisis del token

Pedir veinte o treinta sesiones nuevas y compararlas. Se decide rápido:

```
¿cambian de a uno?                  secuencial
¿comparten prefijo largo?           derivado de tiempo o contador
¿base64 de algo legible?            decodificar — a veces trae el usuario adentro
¿longitud < 16 bytes?               entropía insuficiente, se recorre
¿formato conocido?                  sesión de marco de trabajo: abandonar esta vía
¿sin ninguna estructura en 30?      probablemente aleatorio: abandonar
```

El descarte temprano importa: [[Sesión - token predecible]] no sale la mayoría de las veces y el análisis es caro.

Si hay estructura, medir cuánto varía entre tokens emitidos en el mismo segundo, con distinto usuario y desde distinta IP: eso separa "derivado del tiempo" de "derivado del usuario".

## Fijación

```
1. Pedir /login sin autenticar → anotar el identificador
2. Autenticarse
3. Comparar
```

Mismo identificador = fijación. Tres pasos y treinta segundos.

Después, si hay fallo, buscar la vía para fijarlo:

```
/login;sid=ATACANTE            parámetro de ruta
/login?sid=ATACANTE            cadena de consulta
Cookie: sid=ATACANTE           ¿adopta un identificador que no emitió?
escritura desde subdominio     la vía realista
```

La tercera es la prueba que decide: mandar un identificador inventado y ver si la aplicación lo adopta en vez de descartarlo.

Y verificar la rotación en los otros cambios de privilegio, no solo en el acceso:

```
elevar a administrador   →  ¿rota?
cambiar de cuenta        →  ¿rota?
completar el segundo factor → ¿rota?
```

## Expiración

Todo con la cuenta propia. Guardar el token, hacer la acción, reusar el token.

```
cerrar sesión              → ¿el token viejo sigue funcionando?
cambiar la contraseña      → ¿siguen vivas las otras sesiones?
restablecer la contraseña  → ídem
cambiar el segundo factor  → ídem
revocar el rol             → ¿la sesión conserva el privilegio viejo?
dejar la sesión inactiva   → ¿hay vencimiento por inactividad?
esperar el vencimiento absoluto → ¿existe?
```

La primera es la que más veces falla y la más fácil de explicar en un informe: **el botón de salir borra la cookie del navegador y no invalida nada en el servidor**.

La segunda es la que más importa, porque anula la reacción defensiva del usuario. Se prueba con dos navegadores: sesión en ambos, cambiar la contraseña en uno, comprobar el otro.

## Concurrencia y vinculación

```
usar el mismo token desde dos IP a la vez  → ¿lo permite?
usar el mismo token con otro agente        → ¿lo permite?
autenticarse dos veces                     → ¿se invalida la sesión previa?
¿hay pantalla de sesiones activas?         → ¿puede el usuario cerrarlas?
```

La última no es un hallazgo si falta, pero recomendarla rinde: es la mejor detección de compromiso que puede tener un usuario, y del lado azul complementa la única detección que funciona sin instrumentar nada — **la misma sesión desde dos orígenes**.
