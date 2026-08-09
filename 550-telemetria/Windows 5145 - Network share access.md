---
tipo: telemetria
plataforma: [windows]
producto: Windows Security
identificador: "5145"
por-defecto: false
coste: alto
aliases:
  - acceso a recurso compartido
  - 5145
tags:
  - plataforma/windows
---

# Windows 5145 - Network share access

## Qué lo genera

Acceso a un objeto dentro de un recurso compartido de red, con el detalle de **qué objeto** y con qué permisos.

Existe una versión resumida que solo dice que alguien accedió al recurso; ésta es la detallada, y la diferencia importa: sin el nombre del objeto, la mitad de lo que sigue no se puede detectar.

## Campos relevantes

| Campo | Para qué sirve |
|---|---|
| `SubjectUserName` | Quién |
| `IpAddress` | Desde dónde |
| `ShareName` | Qué recurso |
| `RelativeTargetName` | **Qué objeto dentro del recurso** |
| `AccessMask` | Qué permisos pidió |

## Qué se ve acá

**Los recursos administrativos ocultos.** Windows comparte por defecto las unidades y un recurso de comunicación entre procesos. Un usuario normal no los usa nunca; las herramientas de ejecución remota, todo el tiempo. El acceso a uno de esos desde una estación de trabajo cualquiera es de los indicadores más simples de movimiento lateral.

**Las canalizaciones con nombre.** El campo del objeto revela cuál se abrió, y varias corresponden a servicios concretos: la de control de servicios es la que usan las herramientas que crean un servicio remoto para ejecutar código, la de tareas programadas la que crea tareas remotas. Ver una de esas, desde un origen inusual, es ejecución remota en curso.

**Las políticas del dominio.** El recurso donde viven las directivas de grupo es de lectura pública para cualquier usuario del dominio, y ahí históricamente quedaron credenciales en archivos de configuración. Un usuario recorriendo esas rutas es reconocimiento.

## Coste de recolección

Alto. Los recursos compartidos de archivos generan enormes cantidades de eventos en operación normal, sobre todo en servidores de archivos.

Se domina limitando la auditoría a los recursos que importan —los administrativos y los del dominio— en vez de a todos.

## Cómo se activa

Auditoría detallada de recursos compartidos por directiva. **No viene por defecto** y suele estar apagada precisamente por volumen.

## Limitaciones

- **Volumen alto** en servidores de archivos.
- **No dice qué se hizo con el objeto**, solo que se accedió y con qué permisos pedidos.
- **La versión resumida no alcanza.** Si está habilitada la de recurso y no la detallada, falta el nombre del objeto y con él casi toda la señal.
- **El uso administrativo legítimo se ve igual.** Los equipos de soporte usan estos mismos recursos, y sin conocer su patrón habitual todo es alerta.

## Quién lo emite / quién lo consume

Rojo: [[Pass-the-hash]]
Azul: [[Autenticación NTLM donde el dominio usa Kerberos]]
