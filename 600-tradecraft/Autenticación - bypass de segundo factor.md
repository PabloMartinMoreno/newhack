---
tipo: tradecraft
clase: "[[CWE-287 - Improper Authentication]]"
eje: fase
implementacion: "Completar el acceso sin verificar el segundo factor, o verificándolo por la fuerza"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [credencial-valida, mfa-mal-integrado]
coste: medio
alternativas: ["[[Autenticación - abuso de recuperación de contraseña]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - bypass de MFA
  - 2FA bypass
tags:
  - dominio/web
---

# Autenticación - bypass de segundo factor

## Cuándo lo elijo

Cuando ya hay una credencial válida —de [[Autenticación - credential stuffing]], de spraying, o entregada por el cliente— y el segundo factor es lo único que separa de la cuenta.

Antes de atacar el MFA conviene **buscar el camino que no lo tiene**, que rinde mucho más seguido: una API, un cliente móvil, un protocolo heredado, un endpoint de integración. Una aplicación con MFA impecable en su formulario web y una API que autentica solo con contraseña no tiene MFA, tiene MFA en un camino. Es lo primero que hay que inventariar.

El otro rodeo por diseño es [[Autenticación - abuso de recuperación de contraseña]]: el flujo de recuperación existe justamente para operar sin los factores habituales.

## Por qué funciona

Casi siempre por lo mismo: **la aplicación trata el segundo factor como un paso de la interfaz y no como una condición para emitir la sesión**.

Si la cookie de sesión ya es válida después del primer paso, el segundo solo decide a qué pantalla se redirige, y saltar la redirección alcanza. Es el mismo fallo estructural de [[Control de acceso - salto de contexto]] aplicado al flujo de acceso: el paso siguiente no verifica que el anterior se haya completado.

Las otras dos familias son de implementación. **La verificación del código sin control de ritmo** convierte seis dígitos en un millón de intentos, que sin límite se agotan en minutos — y en cuatro dígitos, en segundos. **Los mecanismos de respaldo** —códigos impresos, "recordar este dispositivo", el enlace por correo— son puertas legítimas más débiles que el factor principal.

## Cómo falla

- **La sesión no existe hasta que todos los factores están verificados** — la mitigación correcta, y cierra la familia entera de saltos.
- **Control de ritmo sobre el código** — pocos intentos y el código se invalida. Cierra la fuerza bruta.
- **El código está atado a la sesión intermedia** — no se puede pedir para una cuenta y usar en otra.
- **Todos los caminos exigen MFA** — cuando el inventario está completo, el rodeo desaparece.
- **Cada intento fallido alerta al usuario** — el ataque se convierte en un aviso a la víctima, que es peor que fallar.

## Coste

Medio, y muy variable: si es un salto de paso, una petición y está; si es fuerza bruta del código, miles de peticiones contra un control de ritmo que probablemente exista. El trabajo que más rinde es el inventario de caminos, que es reconocimiento y no explotación.

## Un límite operativo

> [!danger] El segundo factor está en el teléfono de una persona
> Los intentos generan notificaciones, mensajes y llamadas a un usuario real. Repetirlos es hostigamiento —y como técnica ofensiva tiene nombre propio, "fatiga de MFA", que es ingeniería social sobre una persona, no una prueba técnica.
>
> Fuera de alcance salvo que el engagement lo autorice explícitamente y la persona objetivo esté al tanto. En una prueba técnica lo que se documenta es que el bypass **es posible**, con la mínima cantidad de intentos que lo demuestre.

## Huella esperada

- [[Log de autenticación de la aplicación]] con **un acceso completado sin evento de verificación del segundo factor**. Es el indicador más limpio del dominio y depende por entero de que el registro tenga el campo de factor verificado — que es justo el que casi nunca está.
- En la fuerza bruta del código: ráfaga de verificaciones fallidas contra la misma sesión intermedia. Muy visible.
- En el camino sin MFA: un acceso exitoso por una vía que casi nadie usa. La anomalía es el **camino**, no la credencial, y solo se ve si se registra.
- Un salto de paso deja la secuencia de eventos incompleta: primer factor, y después actividad de sesión autenticada sin nada en el medio.

Las variantes concretas están en [[MFA bypass - matriz de referencia]].
