import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ip } from './utils';
import './Loader.css';

function Loader() {
  const [thumbnails, setThumbnails] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadThumbnails = async () => {
      const response = await fetch(`${ip}/tracks`);
      const data = await response.json();
      setThumbnails(data);
    };

    loadThumbnails();
  }, []);


  const getTrack = async (model_id) => {
    const response = await fetch(`${ip}/tracks/${model_id}`);
    const data = await response.json();
    return data['track'];
  }

  const handleThumbnailClick = async (model_id) => {
    const trackData = await getTrack(model_id);
    navigate('/', {state: { models: trackData }});
  };

  const handleAddNewModel = () => {
    navigate('/');
  };

  return (
    <div className="thumbnail-viewer">
      {thumbnails.map((thumb, index) => (
        <img
          key={index}
          src={thumb.thumbnail}
          alt={thumb.name}
          onClick={() => handleThumbnailClick(thumb._id)}
          className="thumbnail-item"
        />
      ))}
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
