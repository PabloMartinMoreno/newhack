---
tipo: zettel
relacionadas: ["[[Registro del WAF]]", "[[Violación de CSP por script inline]]", "[[Detectar el efecto sobrevive a la evasión]]"]
aliases:
  - el silencio no prueba nada
  - cobertura de detección
tags: []
---

# Ausencia de alertas no es ausencia de ataque

## Idea

Un panel en cero puede significar dos cosas opuestas: que no pasó nada, o que **nada de lo que pasó era visible**. Los dos estados se ven idénticos desde el lado del defensor, y por defecto se lee el primero.

Es el error de interpretación más peligroso del oficio, porque es tranquilizador y no cuesta nada creerlo.

## Por qué importa

Porque cada fuente tiene un punto ciego, y el punto ciego no emite un aviso diciendo que existe. Del vault, tres casos concretos:

- **Un WAF silencioso.** Toda evasión de firmas existe precisamente para no coincidir con ninguna regla. Y las clases que son peticiones legítimas —acceso a datos ajenos, reutilización de credenciales, uso de una sesión robada— **ninguna regla las toca**, no porque el WAF esté mal configurado sino porque no son ataques reconocibles.
- **Pocas violaciones de CSP.** Puede ser que no haya XSS, o que la política sea tan débil que el ataque ejecute dentro de lo permitido. Distinguirlas exige revisar la política, no los informes.
- **Ningún proceso hijo anómalo.** La inyección de argumentos no crea ninguna anomalía en el árbol de procesos, por diseño. Y un XXE que lee un archivo local no emite absolutamente nada: sin red, sin proceso, sin error.

Los dos últimos están declarados como huecos en el vault. **Nombrar lo que no se detecta es parte del trabajo**, porque de lo contrario la cobertura se estima mirando lo que sí llega.

## La inversión incómoda

En varios dominios, **lo fallido es más visible que lo exitoso**:

- Una cadena de gadgets que no funciona lanza excepción; la que funciona, no.
- Un blob con firma inválida deja error; el firmado con la clave correcta, no.
- Un payload mal formado rompe el parser; el correcto pasa limpio.

O sea que el volumen de alertas puede **caer** justo cuando el atacante empieza a acertar. Un descenso de errores después de una ráfaga no es una buena noticia: es el momento a mirar.

## Consecuencias

- **Medir cobertura por lo que no se puede ver, no por lo que llega.** La pregunta útil es "¿qué técnica no dejaría rastro acá?", y hay que responderla técnica por técnica.
- **Toda detección necesita su sección de evasiones.** Si no se sabe cómo se esquiva, no se sabe qué significa su silencio.
- **Un artefacto ausente no es un hueco de contenido.** A veces la regla no se puede escribir porque **no hay fuente**, y eso se resuelve encendiendo telemetría, no escribiendo reglas.
- **Probar las propias reglas es la única forma de saber.** Ejecutar la técnica en laboratorio y verificar que la alerta llega es lo que convierte una suposición en un dato.

## Fuente

Destilado de escribir la cara azul de este vault, y de las dos técnicas que quedaron declaradas como no detectables.
