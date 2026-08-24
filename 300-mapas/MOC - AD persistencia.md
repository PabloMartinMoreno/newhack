---
tipo: moc
dominio: ad
aliases:
  - MOC AD persistencia
tags:
  - dominio/ad
---

# MOC - AD persistencia

> [!abstract] Fase de la kill chain de AD
> Volver a entrar después de que roten las credenciales. Hub: [[MOC - Active Directory]]. Cheatsheet: [[AD persistencia - matriz de referencia]]. Clases: [[T1558.001 - Golden Ticket]] · [[T1134.005 - SID-History Injection]].

Persistir en AD es tener un secreto que no caduca con una rotación de contraseñas. Se elige por **qué secreto controlo** y por **cuánto sobrevive**.

## Árbol de decisión

```
¿Qué tengo, y cuánta supervivencia quiero?
├─ El hash de krbtgt (por DCSync)
│  ├─ forjar cualquier identidad  → [[Golden ticket]]   ← muere al rotar krbtgt DOS veces
│  └─ forjar el ticket de UN servicio  → silver ticket (matriz)
├─ Escritura sobre una cuenta
│  └─ inyectar un SID administrativo en su SIDHistory  → [[Persistencia por SID History]]   ← no aparece en las membresías
└─ Acceso a la PKI
   └─ un certificado de larga vida  → [[MOC - ADCS]]   ← el que sobrevive al cambio de contraseña
```

La escala de supervivencia: **golden** cae cuando el equipo azul rota `krbtgt` dos veces; **SID History** sobrevive a la rotación pero se ve auditando el atributo; **certificado** es el más duro, vale años y sobrevive a la respuesta a incidentes que rota credenciales.

## Orden de aprendizaje

1. [[Golden ticket]] — forjar identidad con el secreto de firma del dominio
2. [[Persistencia por SID History]] — pertenencia silenciosa que no está en las membresías

## Cara roja

- [[Golden ticket]] · [[Persistencia por SID History]] · (certificado → [[MOC - ADCS]])
- Comandos: [[AD persistencia - matriz de referencia]] — golden, silver, diamond, ADCS de `ESC1` a `ESC8`, ACL, y por qué `krbtgt` se rota dos veces.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[Golden ticket]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | [[Ticket de servicio sin ticket inicial previo]] |
| [[Persistencia por SID History]] | [[Windows 4765 - SID History added\|4765]] | [[SID History agregado a una cuenta]] |

El golden se ve como un ticket de servicio **sin ticket inicial previo**; el SID History, como la **escritura del atributo** con un SID administrativo — casi ninguna cuenta legítima lo tiene fuera de una migración.

## Huecos conocidos

- [x] Golden y SID History (persistencia), ambos con detección
- [x] El certificado de larga vida como persistencia vive en [[MOC - ADCS]]
- [ ] Silver y diamond ticket viven en la matriz, sin nota de criterio propia
- [ ] La cara **escalada** del SID History (SID en el PAC de un ticket forjado) está en [[MOC - AD confianzas]], no acá
