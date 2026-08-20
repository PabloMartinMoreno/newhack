---
tipo: telemetria
plataforma: [windows]
producto: AD Certificate Services
identificador: "4887"
por-defecto: false
coste: bajo
aliases:
  - 4887
  - 4886
  - emisión de certificado
tags:
  - plataforma/windows
---

# Windows 4887 - Certificate Services issued

## Qué lo genera

Cada certificado que la entidad certificadora (AD CS) **emite**. Su par `4886` registra la **petición** que llega; `4887` registra la aprobación y emisión; `4888` la denegación. Es el registro operativo de la CA, y la única fuente que ve el momento en que un certificado nace —antes de que se lo use para autenticar—.

Es el flanco que le faltaba a la detección de ADCS: [[Autenticación por certificado a cuenta privilegiada]] ve el **uso** del cert (en el `4768`), tardío; `4887` ve la **emisión**, que ocurre antes y es donde está la evidencia del abuso —el sujeto o el SAN pedido—.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Requester` | Quién pidió el certificado | La cuenta que ejecutó el ataque |
| `Subject` | El sujeto del certificado emitido | A nombre de quién quedó |
| `SubjectAltName` | El SAN pedido | **El campo del ataque**: un UPN que no es el del solicitante |
| `CertificateTemplate` | La plantilla usada | Qué `ESCx` se abusó |
| `SerialNumber` | Serie del cert | Une con el `4768` del uso posterior |
| `Disposition` | Emitido / pendiente / denegado | Solo `4887` es emisión |

El `SubjectAltName` es lo que hace valiosa la fuente: en ESC1 y ESC6 el atacante pide un SAN con el UPN de un administrador, y ese UPN queda registrado acá, junto a la cuenta —no privilegiada— que lo pidió. La discrepancia entre `Requester` y `SubjectAltName` es la firma.

## Coste de recolección

Bajo. Una CA emite pocos certificados comparada con el volumen de autenticación de un DC, así que el registro es manejable. El costo real no es de volumen sino de **activación**: hay que encender la auditoría de AD CS explícitamente.

## Cómo se activa

No viene por defecto. Se habilita en la CA: auditoría de "Emitir y administrar solicitudes de certificado" (`certutil -setreg CA\AuditFilter 127` y la directiva de auditoría de objetos), y los eventos aparecen en el registro de seguridad del servidor de la CA. Es el mismo patrón que la auditoría de directorio para DCSync: un segundo paso que casi nadie hace, y sin el cual la emisión no deja rastro.

## Limitaciones

- **No viene activado**, y sin la auditoría de AD CS encendida no existe. Es el punto ciego por defecto de toda la PKI.
- **Vive en el servidor de la CA**, no en los DC ni en los endpoints: hay que recolectar de esa máquina, que a veces se olvida.
- **No ve el uso posterior**: dice que el cert se emitió, no que se usó. El par es [[Windows 4768 - Kerberos TGT requested]] con PKINIT.
- **La emisión legítima es constante en entornos con tarjetas inteligentes o autoinscripción**: la señal está en la anomalía del SAN o la plantilla, no en la emisión sola.

## Quién lo emite / quién lo consume

Rojo: [[ADCS - certificado con SAN arbitrario]], [[ADCS - plantilla abusable por propósito o ACL]], [[ADCS - abuso de la configuración de la CA]] — toda inscripción abusiva pasa por la CA y deja el `4887`.
Azul: [[Certificado emitido con sujeto ajeno al solicitante]] — ancla en la discrepancia entre `Requester` y `SubjectAltName`.
