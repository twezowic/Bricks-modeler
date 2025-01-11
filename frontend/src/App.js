import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Route, Routes } from 'react-router-dom';
import AppRoutes from './AppRoutes';


function App() {
  const location = useLocation();

  useEffect(() => {
    const handleRouteChange = () => {
      const previousUrl = sessionStorage.getItem('currentUrl');
      if (previousUrl !== '/') {
        sessionStorage.removeItem('models');
      }
      sessionStorage.setItem('currentUrl', window.location.pathname);
    };
    handleRouteChange();
    return () => {
      sessionStorage.setItem('currentUrl', window.location.pathname);
    };
  }, [location]);

  return (
    <Routes>
      {AppRoutes.map((route, index) => {
        const { element, ...rest } = route;
        return <Route key={index} {...rest} element={element} />;
      })}
    </Routes>
  )
}

export default App;
