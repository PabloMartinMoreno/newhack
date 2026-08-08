---
tipo: moc
dominio: windows
aliases:
  - MOC telemetría Windows
  - Fuentes de Windows
tags:
  - plataforma/windows
---

# MOC - Telemetría de Windows

> [!abstract] Nota de referencia paraguas
> Las fuentes de datos del lado azul en Windows: qué ve cada una, qué le cuesta y qué no ve. Los conceptos transversales están en [[MOC - Fundamentos de detección]]; las técnicas rojas que las emiten, en [[MOC - Active Directory]], que está sin desarrollar.

> [!warning] Andamiaje, no contenido cerrado
> Estas catorce notas describen **qué es cada fuente**, no qué técnica la dispara. El campo *Quién lo emite* está en pendiente en casi todas, porque el lado rojo de Windows en este vault todavía es una sola nota.
>
> Es deliberado: son el lugar donde colgar lo que se vaya aprendiendo. A diferencia de las fuentes web, que nacieron de técnicas concretas, estas nacieron primero.

## Qué encender, y en qué orden

No todo cuesta lo mismo ni rinde lo mismo. Por relación valor/coste:

```
1. Ya está encendido — verificá retención y centralización
   [[Windows 4624 - Successful logon]]      accesos exitosos
   [[Windows 4625 - Failed logon]]          fallidos — barato y muy útil
   [[Windows 4768 - Kerberos TGT requested]]
   [[Windows 4769 - Kerberos service ticket requested]]

2. Una directiva y rinde muchísimo
   [[Windows 4688 - Process creation]]      ← CON la línea de comandos, o no sirve
   [[PowerShell 4104 - Script block logging]]

3. Instalar Sysmon — el salto grande
   [[Sysmon EID 1 - ProcessCreate]]         la base de todo
   [[Sysmon EID 8 - CreateRemoteThread]]    barato y de altísima fidelidad
   [[Sysmon EID 10 - ProcessAccess]]        acceso a memoria de otro proceso
   [[Sysmon EID 11 - FileCreate]]           efecto compartido de muchas técnicas
   [[Sysmon EID 13 - RegistryValueSet]]     persistencia
   [[Sysmon EID 22 - DnsQuery]]             DNS con proceso

4. Caras — solo con capacidad de filtrado y de almacenamiento
   [[Sysmon EID 3 - NetworkConnect]]        volumen alto
   [[Sysmon EID 7 - ImageLoad]]             el más caro de todos
   [[Windows 4662 - Directory object operation]]  configuración laboriosa
   [[Windows 5145 - Network share access]]
```

Los dos apuntes del grupo 2 son los que más veces se hacen mal, y en los dos casos el resultado es cobertura aparente: la directiva está, la fuente llega, y **falta justo el campo que tenía toda la señal**.

## Árbol de decisión — quiero detectar esto, ¿qué fuente?

```
¿Qué quiero ver?
├─ Que algo se ejecutó
│  ├─ con argumentos y hashes  → [[Sysmon EID 1 - ProcessCreate]]
│  ├─ sin instalar nada        → [[Windows 4688 - Process creation]]
│  └─ si fue PowerShell        → [[PowerShell 4104 - Script block logging]]
├─ Que alguien se movió a otra máquina
│  ├─ el acceso en el destino  → [[Windows 4624 - Successful logon]] tipo 3 o 10
│  ├─ el ticket en el DC       → [[Windows 4769 - Kerberos service ticket requested]]
│  └─ el recurso que tocó      → [[Windows 5145 - Network share access]]
├─ Que probaron credenciales
│  ├─ contra máquinas          → [[Windows 4625 - Failed logon]] y su SubStatus
│  └─ contra Kerberos          → [[Windows 4768 - Kerberos TGT requested]]
├─ Que tocaron la memoria de otro proceso
│  ├─ abrieron un handle       → [[Sysmon EID 10 - ProcessAccess]]
│  ├─ crearon un hilo          → [[Sysmon EID 8 - CreateRemoteThread]]
│  └─ cargaron un módulo raro  → [[Sysmon EID 7 - ImageLoad]]
├─ Que dejaron algo para volver
│  ├─ un archivo               → [[Sysmon EID 11 - FileCreate]]
│  └─ una clave de registro    → [[Sysmon EID 13 - RegistryValueSet]]
└─ Que sacaron datos o llamaron a casa
   ├─ la conexión              → [[Sysmon EID 3 - NetworkConnect]]
   └─ la resolución de nombre  → [[Sysmon EID 22 - DnsQuery]]
```

## Sysmon o nativo

Es la primera decisión práctica, y no siempre se puede elegir.

| | Nativo | Sysmon |
|---|---|---|
| Instalar algo | no | sí, un servicio |
| Filtrado en origen | no | sí, completo |
| Hashes | no | sí |
| Identificador único de proceso | no | sí |
| Nombre original del binario | no | sí |
| Cobertura de memoria y módulos | no | sí |

La falta de **identificador único de proceso** en el nativo es la más limitante: sin él no se pueden unir los eventos de un mismo proceso entre fuentes, y hay que correlacionar por el identificador numérico, que Windows reutiliza.

Aun así, el nativo con la línea de comandos habilitada cubre muchísimo. La comparación completa está en [[Windows 4688 - Process creation]].

## Orden de lectura

1. [[MOC - Fundamentos de detección]] — los conceptos antes que las fuentes
2. [[Sysmon EID 1 - ProcessCreate]] → [[Windows 4688 - Process creation]] — la misma pregunta con dos fuentes, y qué se pierde
3. [[Windows 4624 - Successful logon]] → [[Windows 4625 - Failed logon]] — los tipos de acceso y los códigos de fallo
4. [[Sysmon EID 10 - ProcessAccess]] → [[Acceso a LSASS desde proceso no firmado]] — el único ciclo rojo↔azul cerrado del vault
5. [[Windows 4768 - Kerberos TGT requested]] → [[Windows 4769 - Kerberos service ticket requested]] — Kerberos y por qué el ataque ocurre fuera de línea
6. El resto, según haga falta

El punto 4 es el que conviene leer entero de una: es el único lugar del vault donde se puede seguir una técnica desde el lado rojo, ver qué artefacto emite, y leer la detección que lo consume. Ese recorrido es el modelo del vault funcionando.

## Cómo se llena esto

Cada fuente tiene su campo *Quién lo emite* en pendiente. Se completa igual que se completó el lado web: escribiendo la técnica roja, observando qué apareció de verdad, y recién ahí escribiendo la detección. El ciclo está en [[Validación de tradecraft en laboratorio]].

**Lo que no hay que hacer es rellenarlo de memoria.** Una nota de telemetría que declara emisores que nadie observó es exactamente la clase de mentira que el campo `probado:` existe para evitar.

## Huecos conocidos

- [x] Las catorce fuentes principales, con campos, coste, activación y limitaciones
- [ ] **El lado rojo entero.** [[MOC - Active Directory]] sigue siendo semilla, así que ninguna de estas fuentes tiene emisores declarados salvo una
- [ ] **Ninguna detección de Windows** más allá de [[Acceso a LSASS desde proceso no firmado]]
- [ ] Fuentes que faltan: creación de servicios, tareas programadas, WMI, borrado del registro de eventos, autenticación NTLM
- [ ] Nada de Linux — `auditd` aparece en [[Proceso hijo del servidor web]] y no tiene notas propias
