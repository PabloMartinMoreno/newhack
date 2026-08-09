---
tipo: deteccion
tecnicas: ["[[T1558.001 - Golden Ticket]]"]
telemetria: ["[[Windows 4769 - Kerberos service ticket requested]]", "[[Windows 4768 - Kerberos TGT requested]]"]
forma: invariante
ventana: "por sesión de ticket"
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - detección de golden ticket
tags:
  - dominio/ad
---

# Ticket de servicio sin ticket inicial previo

## Qué detecta

Una petición de ticket de servicio para la que **nunca hubo una petición de ticket inicial**. Es una de las pocas señales de [[Golden ticket]], y es de forma `invariante` porque afirma algo que en Kerberos legítimo no puede pasar: no se pide acceso a un servicio sin haberse autenticado primero.

## Por qué es la detección posible, y no una mejor

Un golden ticket está firmado con la clave correcta, así que el ticket en sí es **criptográficamente perfecto**: no hay nada malo que inspeccionar en él. La detección no puede mirar el ticket; tiene que mirar **la secuencia** alrededor de su uso.

El atacante fabrica el ticket inicial fuera de línea y lo inyecta en memoria. Nunca lo pide al controlador, así que en el controlador no hay evento de emisión. Pero cuando ese ticket se usa para pedir acceso a un servicio, **eso** sí llega al controlador. El resultado es un ticket de servicio pedido por una identidad que el controlador nunca vio autenticarse.

## Lógica

```
let tgs = kerberos // 4769, peticiones de ticket de servicio
    | project cuenta = TargetUserName, tgs_time = timestamp, ServiceName, IpAddress;
let tgt = kerberos // 4768, peticiones de ticket inicial
    | project cuenta = TargetUserName, tgt_time = timestamp;
tgs
| join kind=leftouter tgt on cuenta
| where isempty(tgt_time) or tgt_time > tgs_time
| project cuenta, ServiceName, IpAddress, tgs_time
```

La condición es que **no exista un ticket inicial previo** para la misma cuenta. Requiere una ventana de correlación amplia, porque un ticket inicial legítimo dura horas.

Dos señales de refuerzo, más fáciles y de alta fidelidad:

- **La cuenta del ticket no existe o está deshabilitada** en el directorio. Un golden ticket puede afirmar cualquier identidad, incluida una borrada. Un acceso de una cuenta que no existe no tiene explicación.
- **Vigencia del ticket fuera de lo normal.** Las herramientas viejas ponían vidas larguísimas por defecto. Se compara contra la vida configurada en el dominio.

## Falsos positivos conocidos

- **La ventana de correlación se quedó corta.** Si el ticket inicial legítimo se pidió antes del inicio de la ventana, parece que no existió. Es el falso positivo dominante de la regla principal, y obliga a ventanas largas — que son caras.
- **Delegación de Kerberos**, donde un servicio pide tickets en nombre de un usuario, produce secuencias que se parecen. Hay que conocer los servicios con delegación configurada y excluirlos.
- **Recolección incompleta de controladores.** Si el ticket inicial se pidió a un controlador cuyos registros no se recolectan, parece que no hubo — un falso positivo que en realidad es un hueco de cobertura. Ver [[Windows 4768 - Kerberos TGT requested]].

## Evasiones conocidas

- **Pedir también un ticket inicial legítimo** con una cuenta válida antes de usar el golden ticket, para que la secuencia parezca completa.
- **Ajustar la vigencia** a valores normales — evade el refuerzo de vida del ticket, que es lo que delataba las herramientas viejas.
- **Usar una cuenta que existe y está activa** — evade el refuerzo de cuenta inexistente, dejando solo la correlación de secuencia, que es la parte cara y frágil.
- **La variante de ticket de servicio forjado** no habla con el controlador en ningún momento: no genera ni 4768 ni 4769. Esta regla no la ve en absoluto.

> [!warning] La detección de golden ticket llega tarde por diseño
> Cuando el ticket se usa, el compromiso que consiguió la clave de firma **ya ocurrió** —fue un [[DCSync]] o un volcado del controlador—. Esta regla detecta el uso posterior, no el compromiso. La detección temprana está aguas arriba, en el momento de robar la clave; acá ya es contención, no prevención.

## Cómo se prueba

Disparador: [[Golden ticket]] en laboratorio, forjando un ticket e inyectándolo para acceder a un servicio.

Forma `invariante` sobre la secuencia de vida de la sesión de ticket. Necesita que se recolecten **4768 y 4769 de todos los controladores** con una ventana de correlación amplia — sin eso, la regla principal produce falsos positivos por huecos de datos, no por ataques.
