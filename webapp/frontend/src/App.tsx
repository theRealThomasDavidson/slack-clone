import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ApiProvider } from './contexts/ApiContext';
import AppRoutes from './routes';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ApiProvider>
          <AppRoutes />
        </ApiProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;