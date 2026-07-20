# Manual del Sistema de Estacionamiento Medido

Este manual ficticio describe el uso de la plataforma web de Estacionamiento Medido. La información se utiliza exclusivamente para probar el sistema RAG del MVP.

## 1. Introducción al sistema

El sistema de Estacionamiento Medido permite administrar zonas con estacionamiento regulado, registrar vehículos, controlar el cumplimiento de las tarifas y consultar reportes operativos. Los usuarios acceden desde un navegador web y las opciones disponibles dependen de su rol.

El menú principal contiene las áreas Operación, Administración, Tarifas, Infracciones y Reportes. Los cambios importantes quedan registrados en una bitácora con usuario, fecha y hora.

## 2. Inicio de sesión

Para ingresar a la plataforma, abra la dirección web provista por el municipio e introduzca su correo electrónico y contraseña. Luego seleccione **Ingresar**. Si el usuario tiene más de un rol, el sistema solicitará elegir el perfil de trabajo antes de mostrar el menú principal.

Después de cinco intentos fallidos de acceso, la cuenta queda bloqueada durante quince minutos. Los administradores pueden revisar el estado de una cuenta desde Administración → Usuarios.

## 3. Recuperación de contraseña

Si olvidó su contraseña, en la pantalla de acceso seleccione **¿Olvidaste tu contraseña?**. Escriba el correo electrónico registrado y presione **Enviar instrucciones**. El sistema enviará un enlace temporal para definir una nueva clave.

El enlace de recuperación vence después de treinta minutos y solo puede utilizarse una vez. Si el correo no llega, revise la carpeta de correo no deseado. Un administrador puede actualizar el correo del usuario desde Administración → Usuarios → Editar.

## 4. Gestión de usuarios

La gestión general de cuentas se realiza desde **Administración → Usuarios**. Desde allí un administrador puede buscar usuarios, crear cuentas, editar datos, bloquear accesos y asignar roles.

Cada cuenta debe tener nombre, apellido, DNI, correo electrónico, rol y estado. El correo debe ser único. Los roles disponibles son Administrador, Supervisor, Inspector y Consulta. Un usuario con estado inactivo no puede iniciar sesión.

## 5. Creación de inspectores

Para crear un nuevo inspector, siga esta ruta:

**Administración → Usuarios → Inspectores → Nuevo Inspector**

Complete los siguientes campos obligatorios:

- Nombre
- Apellido
- DNI
- Correo electrónico
- Zona asignada

Seleccione **Guardar Inspector**. El sistema valida que el DNI y el correo no estén registrados previamente y envía un correo de bienvenida con instrucciones de acceso.

Una persona encargada de controlar autos estacionados debe estar registrada con el rol **Inspector** y tener al menos una zona asignada. Para cambiar la zona, abra Administración → Usuarios → Inspectores, seleccione el inspector y elija **Editar asignación**. Los cambios de asignación se aplican al próximo ingreso del inspector.

## 6. Gestión de zonas de estacionamiento

Para crear una nueva zona, ingrese a **Operación → Zonas → Nueva Zona**. Complete el nombre, código, dirección de referencia, días de operación, horario inicial, horario final y estado.

El código de zona debe ser único. Una zona nueva queda en estado Borrador hasta que un supervisor la active. Una zona activa puede asociarse a inspectores y vehículos autorizados.

Para editar una zona existente, seleccione Operación → Zonas, busque por código y presione **Editar**. No se puede eliminar una zona que tenga infracciones registradas; en ese caso debe cambiarse a estado Inactiva.

## 7. Configuración de tarifas

Las tarifas se administran desde **Tarifas → Configuración → Nueva tarifa**. Seleccione la zona, indique el precio por hora, la fecha de inicio de vigencia y los días en los que aplica. Presione **Guardar tarifa** y luego **Publicar** para que el cambio quede activo.

Para cambiar el precio por hora, abra Tarifas → Configuración, seleccione la tarifa vigente, presione **Editar**, modifique el campo **Precio por hora** y cree una nueva vigencia. El sistema conserva el historial y no modifica operaciones cobradas anteriormente.

Solo un usuario Administrador o Supervisor puede publicar tarifas. Las tarifas futuras pueden programarse con hasta noventa días de anticipación.

## 8. Gestión de vehículos

El registro de vehículos se encuentra en **Operación → Vehículos**. Para agregar un vehículo seleccione **Nuevo vehículo** e introduzca patente, marca, modelo, color y tipo de autorización.

La patente debe tener formato válido y no puede estar duplicada. Un vehículo puede quedar asociado a una cuenta de usuario o a una autorización especial de zona. Para modificar sus datos, busque la patente y seleccione **Editar**.

## 9. Infracciones

Un inspector puede registrar una infracción desde **Operación → Infracciones → Nueva infracción**. Debe seleccionar zona, indicar patente, elegir el tipo de infracción, escribir una observación y adjuntar una fotografía opcional.

Antes de guardar, verifique la ubicación y la hora. El sistema asigna un número único y deja la infracción en estado Pendiente. Un supervisor puede revisarla y cambiarla a Confirmada, Observada o Anulada.

Las infracciones confirmadas aparecen en los reportes del día siguiente. Para consultar una infracción existente utilice su número, patente o zona.

## 10. Reportes

Los reportes están disponibles en **Reportes**. Se pueden consultar infracciones por fecha, zona, inspector y estado; recaudación por período y zona; ocupación estimada; y actividad de usuarios.

Para generar un reporte seleccione el tipo, configure los filtros y presione **Generar**. El resultado puede exportarse en formato CSV. Los reportes de recaudación muestran únicamente operaciones registradas por el sistema.

## 11. Preguntas frecuentes

**¿Qué hago si un inspector no ve su zona?** Verifique que la cuenta esté activa, que tenga rol Inspector y que la asignación de zona esté publicada. El inspector debe cerrar sesión y volver a ingresar.

**¿Puedo borrar una infracción?** No. Una infracción guardada debe ser revisada por un supervisor y, si corresponde, anulada. La bitácora conserva el motivo.

**¿Puedo cambiar una tarifa ya aplicada?** No se modifica una vigencia pasada. Cree una nueva tarifa con una fecha de inicio posterior y publíquela.

## 12. Soporte técnico

Ante errores de acceso, reúna correo del usuario, fecha y hora del problema, navegador utilizado y una captura del mensaje. No envíe contraseñas ni tokens por correo.

El soporte técnico se solicita desde **Ayuda → Nuevo ticket**. Seleccione la categoría, describa el problema, adjunte evidencia y presione **Enviar**. Para incidentes críticos indique también la zona afectada y el número de operación, si existe.

Este manual no contiene instrucciones para configurar Mercado Pago, otras pasarelas de pago ni integraciones externas.
