import { Link } from "react-router-dom";
import LoginButton from "./Account/login";
import LogoutButton from "./Account/logout";
import { useAuth0 } from "@auth0/auth0-react";

const Header = () => {
    const { isAuthenticated } = useAuth0();

    return (
      <header className="bg-[#6f6f6f] text-yellow-300">
        <nav className="p-4 flex justify-between items-center">
            <div className="flex flex-row justify-between w-full">
            <div className="space-x-4">
            {/* <Link to="/">Home</Link> */}
            <Link to="/loader">Browser</Link>
            <Link to="/">Builder</Link>
            <Link to="/profile">Profile</Link>
          </div>
          <div className="flex flex-row space-x-4 text-black">
          {isAuthenticated ? (
             <LogoutButton/>
          ) : (
            <LoginButton/>
          )
        }
          </div>
            </div>
        </nav>
      </header>
    );
  };
  
  export default Header;
  