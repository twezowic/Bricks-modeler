import React, {Link, useEffect, useState} from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from 'react-router-dom';
import Comments from "../Browse/Comments";
import { ip } from "../utils";

const Profile = () => {
  const { user, isAuthenticated, isLoading } = useAuth0();
  const navigate = useNavigate();
  const [selectedId, setSelectedId] = useState(null)
  const [sets, setSets] = useState([]);

  const fetchSets = async () => {
      try {
          const response = await fetch(`${ip}/sets?user_id=${user.sub}`, {
              method: 'GET',
          });
          const data = await response.json();
          setSets(data);
      } catch (error) {
          console.error('Error fetching sets:', error);
      }
  };

  useEffect(()=>{
    if (!isLoading){
      fetchSets()
    }
  }, [isLoading])

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
    <div className="flex flex-row gap-10 p-5">
    <div className="flex-grow grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {sets && sets.map((set) => (
        <div 
          key={set._id} 
          className={`p-4 border rounded-lg
                      ${selectedId === set._id ? 'border-red-800' : 'border-gray-300'}`}
        >
          <div className="text-white">{set.name}</div>
          {set.thumbnail && (
            <img
              src={set.thumbnail}
              alt={set.name}
              width={200}
              height={200}
              onClick={() => 
                selectedId === set._id ? setSelectedId(null) : setSelectedId(set._id)
              }
              className="cursor-pointer rounded-lg object-cover"
            />
          )}
        </div>
      ))}
    </div>
  <div className="w-1/3 p-4 bg-gray-100 rounded-lg">
    {selectedId ? (
      <Comments selectedId={selectedId} />
    ) : (
      <p className="text-gray-500 text-center">Select set to see comments.</p>
    )}
  </div>
</div>

    </>
  );
};

export default Profile;