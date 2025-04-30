// offline.js
const db = new Dexie("TASAL_Asistencia");
db.version(1).stores({
    asistencias: "++id, project_id, fecha, trabajador_id, presente"
});

// Función para guardar un registro offline
function guardarAsistenciaOffline(asistencia) {
    db.asistencias.add(asistencia).then(() => {
        console.log("Registro guardado offline");
    });
}
// offline.js (continuación)

// Función para sincronizar los registros offline con el servidor
async function sincronizarAsistencias() {
    try {
        // Obtener todos los registros almacenados en IndexedDB
        const registros = await db.asistencias.toArray();
        if (registros.length === 0) {
            console.log("No hay registros pendientes de sincronización.");
            return;
        }
        console.log("Registros pendientes:", registros);

        // Preparar el payload para el servidor.
        // Asumiremos que todos los registros pertenecen al mismo proyecto y fecha para simplificar;
        // en una aplicación real podrías agrupar por proyecto y fecha o enviar uno por uno.
        // Aquí enviamos un arreglo con todos los registros.
        const payload = {
            asistencias: registros.map(reg => ({
                trabajador: reg.trabajador_id,
                presente: reg.presente
            })),
            // Puedes agregar 'project' y 'date' si todos son iguales, o enviarlos individualmente
            // Por ejemplo, si todos pertenecen al mismo proyecto y fecha:
            project: registros[0].project_id,
            date: registros[0].fecha
        };

        // Enviar el payload al endpoint de la API
        const response = await fetch('/api/registrar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Si usas autenticación, agrega el token o credenciales necesarias
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            // Si la sincronización es exitosa, eliminar los registros sincronizados
            await db.asistencias.clear();
            console.log("Sincronización completada y registros eliminados de la DB local.");
        } else {
            console.error("Error en la sincronización, status:", response.status);
        }
    } catch (error) {
        console.error("Error durante la sincronización:", error);
    }
}
// Detecta cuando el navegador vuelve a estar en línea y sincroniza los datos.
window.addEventListener('online', () => {
    console.log("Conexión recuperada. Intentando sincronizar...");
    sincronizarAsistencias();
});
if (navigator.onLine) {
    sincronizarAsistencias();
}
