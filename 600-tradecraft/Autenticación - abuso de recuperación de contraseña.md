---
tipo: tradecraft
clase: "[[CWE-640 - Weak Password Recovery Mechanism for Forgotten Password]]"
eje: fase
implementacion: "Tomar la cuenta por el flujo de restablecimiento, sin conocer la credencial"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [flujo-de-recuperacion-expuesto]
coste: medio
alternativas: ["[[Autenticación - bypass de segundo factor]]", "[[Autenticación - credential stuffing]]"]
probado: 2026-08-08
contexto: [web-generica]
aliases:
  - password reset abuse
  - toma de cuenta por recuperación
tags:
  - dominio/web
---

# Autenticación - abuso de recuperación de contraseña

## Cuándo lo elijo

Cuando el acceso principal está bien protegido. Es contraintuitivo y es el orden correcto: **cuanto mejor es el MFA, más vale mirar acá**, porque el flujo de recuperación existe precisamente para funcionar sin los factores habituales.

Es la ruta más corta a una cuenta con segundo factor cuando el restablecimiento además lo desactiva o lo omite, cosa frecuente por comodidad de soporte. Todo el esfuerzo puesto en el MFA se evita por diseño, no por un fallo.

También es el flujo que menos se prueba, porque tiene efectos visibles —le llega un correo a alguien— y eso hace que la gente lo evite. Ver el límite operativo abajo.

## Por qué funciona

El mecanismo tiene que autenticar a quien perdió lo único que probaba quién era, así que se apoya en algo más débil que la contraseña. Ese "algo más débil" es la superficie.

Las cinco formas, de más a menos grave:

**El destino lo controla el atacante.** La petición acepta un parámetro que decide a dónde va el enlace, o el enlace se construye con la cabecera `Host` que mandó el cliente. El correo llega a la víctima y el enlace apunta al atacante. Es la variante crítica y no requiere adivinar nada.

**El token es predecible.** Derivado de marca de tiempo o con poca entropía: se generan tokens propios, se observa el patrón y se predicen los ajenos.

**El token no está atado a la cuenta.** Se pide para la cuenta propia y se usa para cambiar la de otro. Es [[Control de acceso - IDOR]] dentro de este flujo.

**El token no expira ni se invalida.** Un enlace viejo que sigue sirviendo es una llave permanente en una bandeja de entrada.

**Preguntas de seguridad.** Información pública o adivinable, que además no se puede rotar cuando se filtra.

## Cómo falla

- **Token aleatorio, de un solo uso, corto de vida y atado a la cuenta** — la implementación correcta cierra todo salvo el acceso al correo.
- **El destino se toma del registro, nunca de la petición** — mata la variante crítica.
- **Se exige el segundo factor también en el restablecimiento** — cierra el rodeo alrededor del MFA.
- **Respuesta neutra** — "si la cuenta existe, te escribimos" quita el oráculo de enumeración.
- **Control de ritmo en el envío** — evita el bombardeo de correos y ralentiza cualquier ataque de predicción.

## Coste

Medio. La variante de destino controlado es una petición; la de token predecible exige generar muchos y analizarlos, y a veces no llega a nada. El trabajo previo —entender exactamente cómo se arma el enlace— es lo que decide cuál aplica.

## Un límite operativo

> [!danger] Este flujo le manda correos a personas y les cambia la contraseña
> Cada prueba genera un mensaje real a un buzón real. Completar el restablecimiento **deja al usuario fuera de su cuenta**, lo que en una cuenta administrativa es un incidente operativo.
>
> Se prueba contra cuentas propias creadas para eso. Cuando hay que demostrarlo sobre una cuenta real, se acuerda cuál, con quién, y cómo se restaura, **antes**. Y no se completa el cambio si alcanza con demostrar que el token es predecible o que el enlace apunta a donde uno quiere.

## Huella esperada

Es ruidoso hacia el lado que menos se mira: **el usuario**.

- La víctima recibe un correo de restablecimiento que no pidió. Es la detección más efectiva del dominio y no pasa por ningún SIEM: pasa por que alguien avise.
- [[Log de autenticación de la aplicación]] con peticiones de restablecimiento en volumen, o repetidas contra la misma cuenta.
- Un evento de restablecimiento completado **sin sesión previa de esa cuenta**, seguido de acceso desde un origen nuevo, es la secuencia completa de una toma de cuenta.
- [[Log de acceso del servidor web]] muestra la contaminación de la cabecera `Host` si el registro incluye esa cabecera — que rara vez es el caso, y es barato de agregar.

Las variantes concretas están en [[Autenticación - matriz de referencia]] § Recuperación.
