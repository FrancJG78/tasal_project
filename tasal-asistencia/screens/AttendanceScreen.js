import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  Alert, 
  StyleSheet, 
  ActivityIndicator 
} from 'react-native';
import { RNCamera } from 'react-native-camera'; // Asegúrate de tener instalado react-native-camera
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import axios from 'axios';

export default function AttendanceScreen({ navigation, route }) {
  // Se recibe el proyecto seleccionado desde la pantalla anterior
  const { project } = route.params;

  const [isProcessing, setIsProcessing] = useState(false);
  const [isOnline, setIsOnline] = useState(false);

  // Detectar conectividad
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(state.isConnected);
    });
    return () => unsubscribe();
  }, []);

  // Función para manejar la lectura del QR
  const handleBarCodeRead = async ({ data }) => {
    if (isProcessing) return;
    setIsProcessing(true);

    // Se muestra un diálogo para confirmar la acción
    Alert.alert(
      'QR Escaneado',
      `Datos: ${data}`,
      [
        {
          text: 'Registrar',
          onPress: () => registerAttendance(data),
        },
        {
          text: 'Cancelar',
          onPress: () => setIsProcessing(false),
          style: 'cancel',
        }
      ],
      { cancelable: false }
    );
  };

  // Función para registrar la asistencia
  const registerAttendance = async (data) => {
    // Se espera que el QR contenga la URL con el id, se extrae con una expresión regular
    const regex = /\/registrar-qr\/(\d+)\//;
    const match = data.match(regex);
    let workerId = null;
    if (match && match[1]) {
      workerId = match[1];
    } else {
      Alert.alert("Error", "QR no válido");
      setIsProcessing(false);
      return;
    }

    // Se prepara el objeto de asistencia
    const attendanceData = {
      trabajador: workerId,
      proyecto: project.id,
      fecha: new Date().toISOString().split("T")[0],
      presente: true
    };

    try {
      if (isOnline) {
        // Si hay conexión, se intenta enviar la asistencia al servidor
        const response = await axios.post(
          'http://YOUR_SERVER_DOMAIN/api/registrar-asistencia/',
          attendanceData
        );
        if (response.status === 200) {
          Alert.alert("Éxito", "Asistencia registrada en línea");
        } else {
          throw new Error("Error en el servidor");
        }
      } else {
        throw new Error("Sin conexión");
      }
    } catch (error) {
      // Si ocurre error o no hay conexión, guardar el registro en AsyncStorage para sincronizar después
      try {
        let unsynced = await AsyncStorage.getItem('unsynced_attendance');
        let unsyncedArray = unsynced ? JSON.parse(unsynced) : [];
        unsyncedArray.push(attendanceData);
        await AsyncStorage.setItem('unsynced_attendance', JSON.stringify(unsyncedArray));
        Alert.alert(
          "Modo Offline", 
          "Asistencia registrada localmente y se sincronizará cuando se recupere la conexión."
        );
      } catch (storageError) {
        Alert.alert("Error", "No se pudo guardar la asistencia offline.");
      }
    }

    setIsProcessing(false);
  };

  // Función para forzar la sincronización de asistencias pendientes
  const syncAttendance = async () => {
    try {
      let unsynced = await AsyncStorage.getItem('unsynced_attendance');
      let unsyncedArray = unsynced ? JSON.parse(unsynced) : [];
      if (unsyncedArray.length === 0) {
        Alert.alert("Sincronización", "No hay registros pendientes.");
        return;
      }

      // Intenta enviar cada registro pendiente
      for (let i = 0; i < unsyncedArray.length; i++) {
        try {
          const response = await axios.post(
            'http://YOUR_SERVER_DOMAIN/api/registrar-asistencia/',
            unsyncedArray[i]
          );
          if (response.status === 200) {
            // Elimina el registro sincronizado
            unsyncedArray.splice(i, 1);
            i--;
          }
        } catch (error) {
          // Si algún registro falla, continúa con los demás
        }
      }

      await AsyncStorage.setItem('unsynced_attendance', JSON.stringify(unsyncedArray));
      Alert.alert("Sincronización", "Sincronización completada.");
    } catch (err) {
      Alert.alert("Error", "No se pudo sincronizar la asistencia.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Registro de Asistencia</Text>
      <Text style={styles.subtitle}>Proyecto: {project.nombre}</Text>
      
      <View style={styles.scannerContainer}>
        {isProcessing ? (
          <View style={styles.processing}>
            <ActivityIndicator size="large" color="#0000ff" />
            <Text>Procesando...</Text>
          </View>
        ) : (
          <RNCamera
            style={styles.preview}
            onBarCodeRead={handleBarCodeRead}
            captureAudio={false}
          />
        )}
      </View>

      <TouchableOpacity style={styles.syncButton} onPress={syncAttendance}>
        <Text style={styles.syncText}>Sincronizar Asistencias</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20
  },
  scannerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  preview: {
    width: '100%',
    height: '100%'
  },
  processing: {
    justifyContent: 'center',
    alignItems: 'center'
  },
  syncButton: {
    marginVertical: 20,
    padding: 10,
    backgroundColor: '#007bff',
    borderRadius: 5,
    alignItems: 'center'
  },
  syncText: {
    color: '#fff',
    fontSize: 16
  }
});
