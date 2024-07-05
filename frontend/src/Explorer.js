import './App.css';
import Part from './Part';
import React, { useState, useEffect } from 'react';
import { ip } from "./utils"

export default function Explorer({ setModel, setColorModel }) {
  const [color, setColor] = useState("#ff0000");
  const [selectedModel, setSelectedModel] = useState(0);

  const handleColorChange = (e) => {
    const newColor = e.target.value;
    setColorModel(newColor);
    setColor(newColor);
  };

  const handleSelectModel = (modelName, listNum) => {
    console.log('Selected model:', modelName);
    setModel(modelName);
    setSelectedModel(listNum);
  };

  const [parts, setParts] = useState([]);

  useEffect(() => {
    const fetchParts = async () => {
      try {
        const response = await fetch(`${ip}/thumbnails`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setParts(data);
      } catch (error) {
        console.error('Error fetching parts:', error);
      }
    };
    fetchParts();
  }, []);

  // const parts = [
  //   { imageUrl: 'https://cdn.rebrickable.com/media/parts/elements/292602.jpg', name: 2926 },
  //   { imageUrl: 'https://cdn.rebrickable.com/media/parts/elements/329923.jpg', name: 3299 },
  //   { imageUrl: 'https://cdn.rebrickable.com/media/parts/elements/346002.jpg', name: 3460 }
  // ];

  
  const partElements = parts.map((part, index) => (
    <li key={part.name}>
      <Part
        imageUrl={part.imageUrl}
        name={part.name}
        onClick={() => handleSelectModel(part.name, index)}
        isSelected={selectedModel === index}
      />
    </li>
  ));

  return (
    <div className='panel'>
      <ul className='image-list'>
        {partElements}
      </ul>
      <input type="color" value={color} onChange={handleColorChange} />
      <input></input>
    </div>
  );
}
