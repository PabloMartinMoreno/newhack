---
tipo: teoria
habilita: ["[[Relay de NTLM]]", "[[Traer herramientas al objetivo]]"]
relacionadas: ["[[SMB - sesión nula e IPC$]]", "[[TCP - establecimiento de la conexión]]"]
aliases:
  - SMB signing
  - firma SMB
tags: []
---

# SMB - dialectos y firma

## Qué dice la especificación

SMB es el protocolo de compartición de archivos, impresoras y **canalizaciones con nombre** (named pipes) de Windows, sobre TCP 445. Cada sesión empieza con una **negociación de dialecto**: cliente y servidor acuerdan la versión más alta que ambos soportan —SMB1 (CIFS), SMB2, SMB2.1, SMB3.x—. La versión no es cosmética: fija qué cifrado, qué integridad y qué features hay.

La **firma SMB** (SMB signing) es el control que autentica cada mensaje de la sesión con una clave derivada de la autenticación. Con firma exigida, un tercero no puede insertar ni modificar mensajes en una sesión ajena: cada paquete lleva una firma que solo las dos puntas legítimas pueden calcular.

Tres estados de la firma, y son lo que define el riesgo:

| Estado | Qué significa |
|---|---|
| Deshabilitada | No se firma nada |
| Habilitada, no requerida | Se firma si el otro lado quiere; se puede negociar a la baja |
| Requerida | Sin firma no hay sesión |

En controladores de dominio la firma es **requerida** por defecto; en servidores miembro y estaciones, históricamente **habilitada pero no requerida**.

## Dónde el estándar deja lugar

En dos puntos, y de los dos sale ataque:

- **La firma no requerida se negocia a la baja.** Si el servidor la acepta pero no la exige, un atacante en el medio de la autenticación puede pedir que no se firme, y el servidor acepta. Esa es la precondición exacta del relay: no hay que romper nada criptográfico, solo que la firma no sea obligatoria.
- **El dialecto lo elige la negociación, y SMB1 sigue existiendo.** SMB1 no tiene la integridad de las versiones modernas y arrastra fallos de implementación históricos. Mientras un servidor lo acepte por compatibilidad, la punta más débil manda.

## Qué habilita

- **El relay de NTLM depende enteramente de esto.** [[Relay de NTLM]] funciona cuando el objetivo **no exige firma**: la autenticación capturada se reenvía y la sesión resultante no se puede alterar solo si está firmada. Por eso el primer paso del relay es enumerar qué hosts tienen la firma en *habilitada, no requerida*. La firma requerida no rompe la captura, rompe el reenvío.
- **La transferencia por SMB depende del dialecto.** [[Traer herramientas al objetivo]] sirviendo un recurso desde el box del atacante falla contra Windows moderno si se ofrece SMB1: hay que forzar SMB2+ (`-smb2support`), justamente porque SMB1 está deshabilitado del lado cliente.

## Cómo se ve en la práctica

La negociación es el primer intercambio de la sesión y es observable: `Negotiate Protocol Request/Response` lleva el dialecto acordado y los flags de firma. Herramientas de enumeración leen ese handshake para reportar, por host, versión de SMB y si la firma es requerida — el insumo que decide contra quién se puede hacer relay. En [[Sysmon EID 3 - NetworkConnect]] se ve la conexión a 445; el detalle del dialecto y la firma vive en la captura de red, que el vault todavía no modela como telemetría.

## Fuente

- MS-SMB2 (Microsoft Open Specifications).
