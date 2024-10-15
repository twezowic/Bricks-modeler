import Part from './Part';
import React, { useState, useEffect } from 'react';
import { ip } from "../utils"

export default function Explorer({ setColorModel }) {
  const [color, setColor] = useState("#ff0000");

  const handleColorChange = (e) => {
    const newColor = e.target.value;
    setColorModel(newColor);
    setColor(newColor);
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
    <li key={part.name} className='mr-[10px]'>
      <Part
        imageUrl={part.imageUrl}
        name={part.name}
        draggable
        onDragStart={(event) => handleDragStart(event, part.name)}
      />
    </li>
  ));

  const handleFilterChange = (event) => {
    setFilterValue(event.target.value);
  };

  const handleDragStart = (event, part) => {
    const partData = JSON.stringify(part);
    event.dataTransfer.setData('model', partData);
  };
  

  return (
    <div className='w-full h-full overflow-x-auto bg-white'>
      <ul className='flex p-0 list-none py-[5px]'>
        {partElements}
      </ul>
      <div className='flex items-center'>
      <input type="color" value={color} onChange={handleColorChange} />
      <input type="text" value={filterValue} onChange={handleFilterChange} />
      </div>
    </div> 
  );
}
