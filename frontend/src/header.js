import { Link } from "react-router-dom";
import LoginButton from "./Account/login";
import LogoutButton from "./Account/logout";
import { useAuth0 } from "@auth0/auth0-react";
import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

const Header = () => {
    const { isAuthenticated } = useAuth0();

    return (
      <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar className="flex flex-row gap-10">
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            BrickBuilder
          </Typography>
            <div className="flex flex-row justify-between w-full">
             <div className="space-x-4">
             {/* <Link to="/">Home</Link> */}
             <Link to="/">Builder</Link>
             <Link to="/sets">Browse</Link>
             {isAuthenticated && 
              <>
                 <Link to="/loader">Your sets</Link>
                 <Link to="/profile">Profile</Link>
              </>
             }
             </div>
           {isAuthenticated ? (
             <LogoutButton/>
          ) : (
            <LoginButton/>
          )
        }
            </div>
        </Toolbar>
      </AppBar>
    </Box>
    );
  };
  
  export default Header;
  