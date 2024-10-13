import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { Auth0Provider } from '@auth0/auth0-react';
import { BrowserRouter } from 'react-router-dom';
import Header from './header';


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <Auth0Provider
        domain="dev-kz5z1frqrsaajuhg.us.auth0.com"
        clientId="Rc0H8Cc08nf70BY1u5DRHl7DXgztyQdL"
        authorizationParams={{
        redirect_uri: 'http://localhost:3000/profile'
        }}
    >
    <BrowserRouter>
        <Header/>
        <App />
    </BrowserRouter>
    </Auth0Provider>
);

