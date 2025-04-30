import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LoginScreen from './screens/LoginScreen';
import HomeScreen from './screens/HomeScreen';
import ProjectSelectionScreen from './screens/ProjectSelectionScreen';
import QRScanScreen from './screens/QRScanScreen';
import SyncScreen from './screens/SyncScreen';
import { AuthProvider } from './context/AuthContext';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Login">
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Home" component={HomeScreen} />
          <Stack.Screen name="Proyectos" component={ProjectSelectionScreen} />
          <Stack.Screen name="Escanear QR" component={QRScanScreen} />
          <Stack.Screen name="Sincronizar" component={SyncScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </AuthProvider>
  );
}
