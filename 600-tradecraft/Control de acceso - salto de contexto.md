---
tipo: tradecraft
clase: "[[CWE-862 - Missing Authorization]]"
eje: direccion
implementacion: "Saltar pasos de un flujo de varios pasos pidiendo el paso final directamente"
opsec: limpio
telemetria: ["[[Log de auditoría de la aplicación]]"]
requisitos: [flujo-multipaso, estado-no-verificado]
coste: medio
alternativas: ["[[Control de acceso - escalada vertical]]"]
probado: nunca
contexto: [api-rest]
aliases:
  - salto de contexto
  - business logic bypass
  - state machine bypass
tags:
  - dominio/web
---

# Control de acceso - salto de contexto

## Cuándo lo elijo

Cuando la aplicación tiene un proceso de varios pasos y cada paso asume que el anterior ocurrió. Compras, altas con verificación, aprobaciones, procesos de recuperación de contraseña, cualquier asistente.

Es el caso de [[CWE-862 - Missing Authorization]] que menos se busca, y la razón es que **no hay ninguna ruta que parezca administrativa**. Todas las rutas involucradas son del usuario común y todas son legítimas; lo que falta es la verificación de que se llegó a ellas en el orden correcto.

La señal para buscar acá: cualquier flujo que muestre un indicador de progreso, o que dependa de un estado guardado entre peticiones.

## Por qué funciona

El estado del flujo vive en algún lado, y la pregunta es si el servidor lo verifica o lo cree.

Tres formas de que falle, de más a menos común:

**El estado es del cliente.** Un campo oculto, un parámetro o una cookie llevan el paso actual. Se edita y listo.

**El estado es del servidor pero no se verifica.** La sesión sabe que el usuario está en el paso dos, y el endpoint del paso cuatro nunca lo consulta. Se pide directamente y responde.

**El estado se verifica mal.** Se comprueba que exista un proceso en curso, no que esté en el paso correcto. Alcanza con iniciar el flujo y saltar.

En los tres, el impacto es el mismo: se obtiene el resultado del proceso sin cumplir las condiciones que lo justificaban. Comprar sin pagar, verificar sin recibir el código, aprobar sin la aprobación.

## Cómo falla

- **Cada paso verifica el estado del servidor** — la mitigación correcta y no cuesta nada implementarla bien de entrada.
- **El estado va firmado** — un token que el cliente lleva pero no puede modificar. Cambia el problema al dominio de sesiones y firmas.
- **Hay idempotencia y detección de duplicados** — repetir o reordenar peticiones se descarta.
- **El resultado se reconcilia después** — el salto funciona en el momento y un proceso posterior detecta la inconsistencia y revierte. El hallazgo sigue siendo válido, y hay que documentar la ventana.
- **El flujo tiene efectos secundarios reales.** Es el problema práctico: probar un salto en un proceso de compra puede generar un pedido real. Ver la advertencia de abajo.

## Coste

Medio a alto, y es casi todo comprensión. No hay payload ni truco: hay que **entender el proceso de negocio** lo bastante bien como para saber qué condición se está saltando y por qué importa. Es el trabajo menos automatizable de todo el vault, y por eso el que más sobrevive a las herramientas.

Mapear el flujo completo con las peticiones en orden, antes de intentar nada, es lo que separa una hora de trabajo de tres.

## Un límite operativo

> [!danger] Los flujos hacen cosas en el mundo
> Un salto en un proceso de compra genera un pedido; en uno de aprobación, aprueba algo; en uno de alta, crea una cuenta con permisos. Estos efectos no se revierten solos y a veces salen del sistema — un correo enviado, un pago iniciado, un aviso a un tercero.
>
> Se prueba en entorno de pruebas si existe, y si no, se acuerda de antemano qué flujos se pueden tocar y quién limpia. Es la clase de hallazgo donde conviene avisar antes, no después.

## Huella esperada

- [[Log de auditoría de la aplicación]] con la secuencia de eventos del flujo **incompleta**: aparece el paso final sin los intermedios. Esa ausencia es toda la señal, y solo se ve si el registro cubre cada paso y no únicamente el resultado.
- Marcas de tiempo imposibles: un proceso que normalmente lleva minutos, completado en dos segundos.
- Ningún error, ningún `403`, ninguna anomalía técnica. Como el resto del dominio, lo que delata es la **relación entre eventos**, no un evento suelto.

La detección natural acá no es una regla sobre una petición: es una verificación de invariante sobre la secuencia, que es un tipo de detección que el vault todavía no modela.
