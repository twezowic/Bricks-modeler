import Part from './Part';
import React, { useState, useEffect } from 'react';
import { ip } from "../utils"
import { useSearchParams } from 'react-router-dom';

export default function Explorer({ setColorModel, selectedStep }) {
  const [searchParams] = useSearchParams();
  const set_id = Object.fromEntries([...searchParams]).set_id ?? undefined

  const [color, setColor] = useState("#ff0000");

  const handleColorChange = (e) => {
    const newColor = e.target.value;
    setColorModel(newColor);
    setColor(newColor);
  };

  const [parts, setParts] = useState([]);

  const [filterValue, setFilterValue] = useState('brick 2 x 4');
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [size, setSize] = useState([0, 0, 0]);

  const categories = [
    'All',
    'Bars, Ladders and Fences',
    'Baseplates',
    'Bricks',
    'Bricks Curved',
    'Bricks Round and Cones',
    'Bricks Sloped',
    'Bricks Special',
    'Panels',
    'Plates',
    'Plates Angled',
    'Plates Round Curved and Dishes',
    'Plates Special',
    'Tiles',
    'Tiles Round and Curved',
    'Tiles Special',
    'Windows and Doors'
  ]

  useEffect(() => {
    const fetchParts = async () => {
      try {
        const params = new URLSearchParams();

        if (filterValue) {
          params.append('filter', filterValue);
        }

        if (selectedCategory !== "All") {
          params.append('category', selectedCategory);
        }

        params.append('size', size.join(','))

        const url = `${ip}/parts?${params.toString()}`;

        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setParts(data);
      } catch (error) {
        console.error('Error fetching parts:', error);
      }
    };
    const fetchInstructionParts = async () => {
      try {
        const response = await fetch(`${ip}/instruction/models/${set_id}/${selectedStep}`, {
            method: 'GET',
        });
        const data = await response.json();
        setParts(data);
    } catch (error) {
        console.error('Error fetching instructions:', error);
    }
    }
    if (set_id) {
        fetchInstructionParts()
    } else {
      fetchParts();
    }
  }, [filterValue, selectedCategory, size, selectedStep]);

  const partElements = parts.map((part, index) => (
    <li key={part.model} className='mr-[10px]'>
      <Part
        imageUrl={part.thumbnail ?? ""}
        name={part.model}
        draggable
        onDragStart={(event) => handleDragStart(event, part.model, part.color)}
        color={part.color}
        count={part.count}
      />
    </li>
  ));

  const handleFilterChange = (event) => {
    setFilterValue(event.target.value);
  };

  const handleDragStart = (event, part, partColor) => {
    const partData = JSON.stringify(part);
    event.dataTransfer.setData('model', partData);

    if (partColor){
      const partColorData = JSON.stringify(partColor);
      event.dataTransfer.setData('color', partColorData);
    }
  };

  const handleChangeSize = (index, value) => {
    const newSize = [...size];
    newSize[index] = Number(value);
    setSize(newSize);
  };

  return (
    <div className='w-full h-[13vh] overflow-x-auto bg-white flex flex-col'>
      <ul className='flex p-0 list-none'>
        {partElements}
      </ul>
      {!set_id &&
         <div className='flex items-center gap-2'>
         <input type="color" value={color} onChange={handleColorChange} />
         <input type="text" value={filterValue} onChange={handleFilterChange} />
         <select
           value={selectedCategory}
           onChange={(e) => setSelectedCategory(e.target.value)}
           className=""
         >
           {categories.map((category) => (
             <option key={category} value={category}>
               {category}
             </option>
           ))}
         </select>
         <div className='flex flex-row border-1 max-h-[30px]'>
           <input
             type="number"
             value={size[0]}
             min={0}
             max={48}
             onChange={(e) => handleChangeSize(0, e.target.value)}
             className="m-2 p-1 border"
           />
           <input
             type="number"
             value={size[1]}
             min={0}
             max={56}
             onChange={(e) => handleChangeSize(1, e.target.value)}
             className="m-2 p-1 border"
           />
           <input
             type="number"
             value={size[2]}
             min={0}
             max={39}
             onChange={(e) => handleChangeSize(2, e.target.value)}
             className="m-2 p-1 border"
           />
         </div>
         </div>
      }
    </div> 
  );
}
