---
tipo: deteccion
tecnicas: ["[[CWE-613 - Insufficient Session Expiration]]"]
telemetria: ["[[Log de autenticación de la aplicación]]"]
forma: invariante
ventana: "por sesión"
estado: idea
fidelidad: alta
logica: kql
validada: 
aliases:
  - sesión zombi
tags:
  - dominio/web
---

# Actividad de sesión posterior a su cierre

## Qué detecta

Uso de un identificador de sesión **después** del evento que debería haberlo invalidado: un cierre de sesión, un cambio de contraseña, un cambio de segundo factor, una revocación de rol o una baja de cuenta.

Es la detección de forma `invariante` del vault, y por eso está: la condición no se evalúa sobre un evento ni sobre una ventana de tiempo, sino sobre la **secuencia de vida de cada sesión**. La afirmación que se verifica es simple y no debería violarse nunca — *ninguna sesión está activa después del evento que la termina*.

Detecta dos cosas a la vez que conviene separar al reportar:

- **Una vulnerabilidad**, si la aplicación acepta el token: es [[Sesión - expiración insuficiente]] y el hallazgo es de la aplicación.
- **Un ataque**, si además el token viene de un origen distinto del que cerró la sesión: alguien lo tenía guardado.

## Lógica

```
eventos_sesion
| where tipo in ('logout', 'password_change', 'mfa_change', 'role_revoke', 'account_disable')
| project session_id, cuenta, fin = timestamp, evento = tipo
| join kind=inner (
    actividad_sesion
    | project session_id, uso = timestamp, client_ip, ruta
  ) on session_id
| where uso > fin
| project cuenta, session_id, evento, fin, uso, retraso = uso - fin, client_ip, ruta
```

El caso grave y el que hay que alertar con prioridad: `evento == 'password_change'` con uso posterior desde **otra IP**. Eso es un compromiso que sobrevivió a la reacción del usuario, y significa que la víctima cree que resolvió el problema y no lo resolvió.

Para JWT sin estado hay que reconstruir la equivalencia por sujeto y momento de emisión, porque no hay identificador de sesión que unir:

```
| where jwt_iat < password_change_time and jwt_uso > password_change_time
```

## Falsos positivos conocidos

- **Peticiones en vuelo** al momento del cierre de sesión: llegan segundos después y son legítimas. Se descartan con un margen de gracia corto —diez o treinta segundos— sobre `retraso`.
- **Múltiples pestañas** cerrando sesión de forma desordenada.
- **Reintentos del cliente** con el token viejo antes de recibir el nuevo estado.
- **Trabajos en segundo plano** iniciados antes del cierre que siguen usando el contexto de la sesión.

Ninguno de estos aparece minutos después. El margen de gracia resuelve casi todo.

## Evasiones conocidas

- **Usarlo antes del cierre.** La regla detecta permanencia, no acceso: un atacante que entra, actúa y sale antes de que la víctima reaccione nunca la dispara.
- **Cierre de sesión que no emite evento.** Si el botón de salir solo borra la cookie del navegador y no registra nada, no hay `fin` con el que comparar y la regla no tiene entrada. Es el caso más común, y es la misma causa que la vulnerabilidad que se busca.
- **Sin identificador de sesión en el registro de actividad** no hay nada que unir.
- **Rotación de token**: si el atacante obtiene un token nuevo tras el cambio de contraseña, el viejo deja de importar.

## Cómo se prueba

Disparador: [[Sesión - expiración insuficiente]] con la cuenta propia, en dos navegadores.

Es forma `invariante` y se valida con un caso, pero **requiere que ambos extremos se registren con el identificador de sesión**: el evento que termina la sesión y la actividad posterior. Si falta cualquiera de los dos, la regla no se puede escribir — y verificar eso es el primer paso, no el último.
