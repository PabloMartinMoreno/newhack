---
tipo: deteccion
tecnicas: ["[[T1649 - Steal or Forge Authentication Certificates]]"]
telemetria: ["[[Windows 4887 - Certificate Services issued]]"]
forma: evento
ventana: 
estado: idea
fidelidad: alta
logica: sigma
validada: 
aliases:
  - detección de ESC1 en la emisión
  - SAN mismatch
tags:
  - dominio/ad
---

# Certificado emitido con sujeto ajeno al solicitante

## Qué detecta

Un certificado emitido cuyo **SAN (nombre alternativo del sujeto) no corresponde a la cuenta que lo pidió**. Es la firma de [[ADCS - certificado con SAN arbitrario]] (ESC1) y del ESC6 en el momento de la emisión: el atacante, con una cuenta no privilegiada, pide un certificado con el UPN de un administrador en el SAN, y ese UPN queda registrado junto al solicitante real en el `4887`.

Es la detección de ADCS de mayor fidelidad y la que llega **a tiempo**: [[Autenticación por certificado a cuenta privilegiada]] ve el uso del cert después de emitido; esta lo ve al nacer, cuando todavía no se usó, y la evidencia —el SAN falso— está en el propio evento.

## Lógica

```yaml
detection:
  selection:
    EventID: 4887
    SubjectAltName|exists: true          # el cert lleva un SAN pedido por el solicitante
  condition: selection and SubjectAltName != Requester_UPN
```

La comparación central es `SubjectAltName` contra el UPN del `Requester`: un usuario pidiendo un certificado que autentica **como otro** es el ataque. En la práctica se resuelve normalizando los dos campos y alertando cuando difieren, con una correlación contra el directorio para saber el UPN real del solicitante.

Refinamiento por plantilla: cruzar con `CertificateTemplate`. Un SAN arbitrario sobre una plantilla que **no** debería permitirlo (ESC6, la bandera de CA) o sobre una plantilla de bajo privilegio pedida para un UPN administrativo (ESC1) sube la señal a casi certeza.

## El requisito previo, que es donde casi siempre falla

> [!important] Esta regla no existe si la auditoría de AD CS está apagada
> [[Windows 4887 - Certificate Services issued]] **no se genera** sin la auditoría de AD CS habilitada en la CA (`certutil -setreg CA\AuditFilter 127` más la directiva de auditoría de objetos). Es el mismo patrón que la auditoría de directorio para DCSync: un segundo paso de configuración, esta vez en el servidor de la CA, que casi nadie hace.
>
> Sin él, toda la emisión de ADCS es invisible y solo queda el uso (la de PKINIT). Verificar que el `4887` se genera es el primer paso; si no, el trabajo es encender la auditoría de la CA, no ajustar la lógica. Otro caso de [[Ausencia de alertas no es ausencia de ataque]].

## Falsos positivos conocidos

- **Autoinscripción y tarjetas inteligentes** donde el SAN sí corresponde al solicitante: no disparan, porque la regla compara y solo alerta la discrepancia.
- **Servicios que solicitan certificados en nombre de otros por diseño** (agentes de inscripción legítimos, ESC3 legítimo): se conocen y se excluyen por cuenta solicitante. Cada uno es una cuenta con poder de emitir por terceros, que conviene inventariar.

## Evasiones conocidas

- **La auditoría de la CA apagada**, el estado por defecto: la evasión más efectiva y la que no controla el atacante.
- **Un SAN que coincida con el solicitante** pero abusando otra vía (ESC9/10, mapeo débil): el SAN no discrepa, así que esta regla no lo ve; lo vería la de PKINIT en el uso.
- **Pedir el cert por un endpoint sin auditar** o en una CA no monitoreada.

## Cómo se prueba

Disparador: [[ADCS - certificado con SAN arbitrario]] en laboratorio —`certipy req` con `-upn administrador`— contra una CA con la auditoría encendida.

Forma `evento`, un disparo la valida **después de confirmar que el `4887` se genera** con la auditoría de AD CS activa. Ese es el paso que decide si la regla es escribible o si el trabajo es configurar la fuente.
