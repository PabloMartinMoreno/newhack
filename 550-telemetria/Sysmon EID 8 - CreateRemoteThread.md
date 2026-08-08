---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 8"
por-defecto: false
coste: bajo
aliases:
  - hilo remoto
  - CreateRemoteThread
tags:
  - plataforma/windows
---

# Sysmon EID 8 - CreateRemoteThread

## Qué lo genera

Un proceso que crea un hilo de ejecución **dentro de otro proceso**.

Es de los artefactos de más alta fidelidad de Windows, y por una razón simple: en operación normal **casi nadie hace esto**. Los que sí lo hacen son pocos y conocidos — depuradores, antivirus, algunas herramientas de accesibilidad y de monitoreo. Todo lo demás que aparezca acá merece una mirada.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `SourceImage` | Quién inyecta | El proceso atacante |
| `TargetImage` | Dónde inyecta | El proceso víctima |
| `StartAddress` | Dirección de inicio del hilo | Una dirección sin módulo asociado es memoria sin respaldo en disco |
| `StartModule` | Módulo, si lo hay | **Vacío es la señal** |
| `StartFunction` | Función, si se resolvió | `LoadLibraryA` es la inyección clásica de DLL |
| `SourceUser` / `TargetUser` | Contextos | Cruzar límites de usuario es más raro todavía |

`StartModule` vacío con `StartAddress` apuntando a memoria privada es la firma de código ejecutando sin archivo en disco. Es lo que la mayoría de las herramientas de inyección producen.

## Coste de recolección

Bajo. Es un evento raro por naturaleza, así que se puede registrar sin filtrar y el volumen sigue siendo manejable. Excelente relación entre coste y valor.

## Cómo se activa

Sección correspondiente en la configuración de Sysmon. Conviene registrarlo **sin exclusiones agresivas**: dado lo raro que es, filtrar de más pierde mucho y ahorra poco.

## Limitaciones

- **Solo cubre una de muchas formas de inyectar.** Es la limitación importante y hay que tenerla presente: existen bastantes técnicas que consiguen ejecución en otro proceso **sin** crear un hilo remoto — colas de procedimientos asíncronos, secuestro de un hilo existente, escritura de memoria seguida de redirección del contexto, y las variantes que crean el proceso ya vaciado.
- **Los legítimos existen y hay que conocerlos.** Sin la lista del entorno, cada depurador abierto es una alerta.
- **No dice qué se ejecutó**, solo que se creó el hilo. Hay que correlacionar con [[Sysmon EID 7 - ImageLoad]] y con la creación del proceso.
- **Requiere que ambos procesos estén siendo observados.**

Detectar lo que esta fuente no ve exige mirar el acceso al proceso —[[Sysmon EID 10 - ProcessAccess]]— y la carga de módulos, que es más ruidosa. Es un buen ejemplo de que **una fuente sola no cubre una técnica**: cubre una implementación de la técnica.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
