import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ip } from './utils';
import './Loader.css';
import { useAuth0 } from '@auth0/auth0-react';

function Loader() {
  const [thumbnails, setThumbnails] = useState([]);
  const navigate = useNavigate();
  const { user } = useAuth0();

  useEffect(() => {
    const loadThumbnails = async () => {
      const response = await fetch(`${ip}/tracks/user/${encodeURIComponent(user.sub)}`);
      const data = await response.json();
      console.log(data)
      setThumbnails(data);
    };

    loadThumbnails();
  }, []);


  const getTrack = async (model_id) => {
    const response = await fetch(`${ip}/tracks/${model_id}`);
    const data = await response.json();
    return data
  }

  const handleThumbnailClick = async (model_id) => {
    const trackData = await getTrack(model_id);

    const url = trackData.set_id ? `/?track_id=${model_id}&set_id=${trackData.set_id}`: `/?track_id=${model_id}`
    localStorage.setItem('models', JSON.stringify(trackData.track));
    navigate(url);
  };

  const handleAddNewModel = () => {
    navigate('/');
  };

  return (
    <div className="thumbnail-viewer">
      {thumbnails && 
        thumbnails.map((thumb, index) => (
          <img
            key={index}
            src={thumb.thumbnail}
            alt={thumb.name}
            onClick={() => handleThumbnailClick(thumb._id)}
            className="thumbnail-item"
          />
        ))
      }
      <img
        src="./plus.png"
        alt="Add new model"
        onClick={handleAddNewModel}
        className="thumbnail-item"
      />
    </div>
  );
}

export default Loader;
