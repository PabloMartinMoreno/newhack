---
tipo: meta
aliases:
  - Matriz de pruebas de autorización
  - Método de prueba de control de acceso
tags:
  - meta/referencia
  - dominio/web
---

# Control de acceso - matriz de pruebas

> [!info] Referencia pura, no un zettel
> **Esta matriz no tiene payloads porque el dominio no tiene payloads.** Lo que se repite acá es un método, no una sintaxis. El criterio de qué buscar está en [[MOC - Broken access control]]; los bypass concretos, en [[Control de acceso bypass - matriz de referencia]].

## 0. Preparación — lo que decide todo lo demás

**Dos cuentas del mismo nivel, y una de cada nivel que exista.** Es la inversión que más rinde del dominio y hay que hacerla antes de tocar nada. Sin dos cuentas horizontales no se puede distinguir "no tengo permiso" de "no existe"; sin una de cada nivel vertical no se sabe qué debería estar permitido.

Si el cliente solo entrega una cuenta, pedir la segunda **al inicio**, con este argumento: sin ella, la clase de vulnerabilidad más frecuente de la web no se puede probar y queda fuera del informe.

Registrar para cada cuenta: identificador de usuario, identificadores de sus objetos, rol, y el conjunto de rutas que su interfaz le muestra.

## 1. La matriz

Tres dimensiones. Cada celda es una petición.

```
        actor        ×  objeto        ×  operación
        ─────────       ──────          ──────────
        usuario A       de A            leer
        usuario B       de B            crear
        admin           de admin        modificar
        anónimo         inexistente     borrar
```

Lo que se busca no es un error: es una celda que responde **cuando no debería**. La tabla de referencia de qué debería pasar:

| Actor | Objeto | Esperado |
|---|---|---|
| A | de A | permitido |
| A | de B | **denegado** ← el caso de [[Control de acceso - IDOR]] |
| A | de admin | **denegado** |
| anónimo | cualquiera | **denegado** |
| admin | de A | permitido, y **auditado** |

La última fila no es un hallazgo: es una verificación de que existe registro de auditoría. Si un administrador puede leer datos de un usuario sin que quede rastro, eso es un hallazgo propio aunque el control funcione.

## 2. Recorrido sistemático

Por cada endpoint que la aplicación expone:

1. **Capturar la petición legítima** con la sesión de A sobre un objeto de A. Es la línea base.
2. **Cambiar el identificador** por uno de B. ¿Devuelve el objeto de B?
3. **Cambiar la sesión** por la de B, dejando el identificador de A. Misma pregunta, al revés.
4. **Quitar la sesión** entera. ¿Responde igual?
5. **Cambiar el verbo.** Si `GET` está protegido, probar `POST`, `PUT`, `PATCH`, `DELETE`.
6. **Repetir sobre la versión anterior de la API**, si existe.

Los pasos 4 a 6 son los que más se saltean y los que más veces pagan.

## 3. Interpretar la respuesta

| Respuesta con identificador ajeno | Qué significa |
|---|---|
| `200` con datos de otro | IDOR confirmado |
| `403` / `401` | Control presente en este endpoint |
| `404` | Ambiguo: puede ser control correcto o el objeto no existe |
| `500` | Se llegó a la consulta sin control y algo falló después |
| `200` vacío o parcial | El control está en la vista, no en los datos: revisar la respuesta cruda |

El `404` es el caso que hay que resolver y no asumir: se pide un identificador que **con certeza no existe** —muy alto, o de otro formato— y se compara con el de un objeto ajeno que sí existe. Si las respuestas difieren en algo (tiempo, tamaño, cabeceras), hay oráculo y probablemente hay hallazgo.

## 4. Priorizar

No todos los endpoints valen lo mismo. En orden de retorno:

1. **Los que devuelven datos personales** — el impacto en el informe se argumenta solo.
2. **Los de escritura** — modificar lo ajeno pesa más que leerlo.
3. **Los de exportación y listados masivos** — un solo fallo expone todo de una.
4. **Los administrativos** — impacto máximo aunque el fallo sea uno.
5. **Los de solo lectura sobre datos poco sensibles** — último.

## 5. Documentar

Por cada hallazgo, lo que hace falta para que sea reportable y reproducible:

- La petición exacta, con la sesión de A y el objeto de B.
- **Prueba de que B es de otro**: la misma petición desde la sesión de B mostrando que es su objeto.
- El alcance: cuántos objetos son alcanzables, calculado **sin enumerarlos**.
- Si el identificador era predecible o dónde se filtraba.

> [!warning] El alcance se calcula, no se extrae
> Demostrar que se accede a un objeto ajeno cierra el hallazgo. Bajar diez mil registros no lo hace más grave y convierte la prueba en una fuga real, con obligación de notificación para el cliente. Ver la advertencia de [[Control de acceso - IDOR]].
