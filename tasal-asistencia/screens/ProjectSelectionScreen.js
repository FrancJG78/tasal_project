import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  FlatList, 
  TouchableOpacity, 
  ActivityIndicator, 
  StyleSheet, 
  Alert 
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

export default function ProjectSelectionScreen({ navigation }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  // Función para obtener los proyectos del servidor o de la copia local
  const fetchProjects = async () => {
    try {
      // Reemplaza la URL con la de tu API en la nube
      const response = await axios.get('http://YOUR_SERVER_DOMAIN/api/projects/');
      setProjects(response.data);

      // Guarda los proyectos en AsyncStorage para usarlos offline
      await AsyncStorage.setItem('projects', JSON.stringify(response.data));
    } catch (error) {
      Alert.alert('Error', 'No se pudieron cargar los proyectos en línea, cargando copia local.');
      // Si falla, intenta cargar desde almacenamiento local
      const storedProjects = await AsyncStorage.getItem('projects');
      if (storedProjects !== null) {
        setProjects(JSON.parse(storedProjects));
      } else {
        Alert.alert('Error', 'No hay proyectos almacenados localmente.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // Función que se ejecuta al seleccionar un proyecto
  const selectProject = (project) => {
    // Se navega a la pantalla de asistencia pasando el proyecto seleccionado
    navigation.navigate('Attendance', { project });
  };

  // Renderizado de cada elemento en la lista
  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.itemContainer}
      onPress={() => selectProject(item)}
    >
      <Text style={styles.itemText}>{item.nombre}</Text>
    </TouchableOpacity>
  );

  // Mientras se cargan los proyectos
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text>Cargando proyectos...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Selecciona el Proyecto</Text>
      <FlatList
        data={projects}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        contentContainerStyle={styles.listContainer}
      />
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
    marginBottom: 20,
    textAlign: 'center'
  },
  listContainer: {
    paddingBottom: 20
  },
  itemContainer: {
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 5,
    marginBottom: 10
  },
  itemText: {
    fontSize: 18
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  }
});
