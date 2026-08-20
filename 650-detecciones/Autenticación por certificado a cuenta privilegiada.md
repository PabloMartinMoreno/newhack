---
tipo: deteccion
tecnicas: ["[[T1649 - Steal or Forge Authentication Certificates]]"]
telemetria: ["[[Windows 4768 - Kerberos TGT requested]]"]
forma: evento
ventana: 
estado: idea
fidelidad: media
logica: sigma
validada: 
aliases:
  - detección de PKINIT malicioso
  - detección de abuso ADCS
tags:
  - dominio/ad
---

# Autenticación por certificado a cuenta privilegiada

## Qué detecta

Una solicitud de TGT hecha con un **certificado** (PKINIT) para una cuenta privilegiada. Es la firma del uso de un certificado obtenido por cualquiera de las ramas de ADCS —[[ADCS - certificado con SAN arbitrario]], [[ADCS - plantilla abusable por propósito o ACL]], [[ADCS - abuso de la configuración de la CA]]—: todas terminan en `certipy auth`, que pide un TGT presentando el certificado, y el `4768` resultante lleva la información del certificado en campos que una autenticación por contraseña no tiene.

Cierra parcialmente el hueco de "autenticación por certificado" del dominio: no distingue el cert legítimo del forjado —los dos son PKINIT válido—, pero ancla en que **una cuenta privilegiada se autentique con certificado**, que es raro y sospechoso cuando el administrador normalmente usa contraseña.

## Lógica

```yaml
detection:
  selection:
    EventID: 4768
    CertIssuerName|exists: true          # el TGT se pidió con certificado (PKINIT)
  privileged:
    TargetUserName|contains:
      - 'Administrator'
      - 'Admin'
      - 'krbtgt'
    # o, con más precisión, una lista de cuentas privilegiadas por SID
  condition: selection and privileged
```

La presencia de `CertIssuerName` (o `CertSerialNumber`/`CertThumbprint`, según la fuente) es lo que marca PKINIT: una autenticación por contraseña no rellena esos campos. El filtro por cuenta privilegiada es lo que sube la señal — un usuario común autenticándose con cert puede ser legítimo (tarjeta inteligente), un administrador no tanto.

Refinamiento de mayor precisión: en vez de nombres, una **lista blanca de cuentas que usan certificado legítimamente** (tarjetas inteligentes conocidas). Cualquier PKINIT fuera de esa lista para una cuenta sensible es el ataque casi con certeza.

## Falsos positivos conocidos

- **Autenticación con tarjeta inteligente** — el uso legítimo de PKINIT. Si el entorno usa tarjetas, hay que basar la regla en la lista de cuentas que las usan, no en la mera presencia del certificado.
- **Cuentas de servicio que autentican por certificado** por diseño — se conocen y se excluyen.

## Evasiones conocidas

- **Usar el hash NT que devuelve `certipy auth`** en vez del TGT: el certificado da también el hash NT de la cuenta, y con él se hace [[Pass-the-hash]] sin volver a presentar el certificado. Esa vía no genera el `4768` con certificado — la detecta la de pass-the-hash, no esta.
- **Autenticar contra un servicio que no pide TGT por PKINIT** en algunos flujos.
- Un cert para una cuenta **no** en la lista de privilegiadas cae fuera del filtro; por eso la lista blanca de cuentas con tarjeta es mejor que la lista negra de nombres.

## Cómo se prueba

Disparador: cualquier rama de ADCS en laboratorio, hasta `certipy auth` con el `.pfx` de una cuenta privilegiada.

Forma `evento`, un disparo la valida — el `4768` con certificado se genera siempre que se use PKINIT, sin requisito de auditoría especial más allá del registro de Kerberos.
