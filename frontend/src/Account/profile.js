import React, {Link} from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const { user, isAuthenticated, isLoading } = useAuth0();
  const navigate = useNavigate();

  if (isLoading) {
    return <div>Loading ...</div>;
  }
  return (
    <>
    {isAuthenticated && (
      <div>
        <img src={user.picture} alt={user.name} />
        <p>{user.email}</p>
        <p>{user.sub}</p>           {/* user id do bazy w mongo*/}
      </div>
    )}
    <button onClick={()=>navigate('/')}/>
    </>
  );
};

export default Profile;