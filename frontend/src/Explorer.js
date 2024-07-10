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
  const [filterValue, setFilterValue] = useState('');


  useEffect(() => {
    const fetchParts = async () => {
      try {
        const response = await fetch(`${ip}/parts?filter=${filterValue}`);
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
  }, [filterValue]);

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

  const handleFilterChange = (event) => {
    setFilterValue(event.target.value);
  };

  return (
    <div className='panel'>
      <ul className='image-list'>
        {partElements}
      </ul>
      <input type="color" value={color} onChange={handleColorChange} />
      <input type="text" value={filterValue} onChange={handleFilterChange} placeholder="Filter parts by name" />
    </div>
  );
}
