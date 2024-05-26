import './App.css';
import React from 'react';
import Part from './Part';
import { useState } from 'react';

export default function Explorer(){
    const [color, setColor] = useState("#ff0000");

    return (
    <div className='panel'>
        <ul className='image-list'>
          <li><Part imageUrl={'https://cdn.rebrickable.com/media/parts/elements/292602.jpg'} name={2926}/></li>
          <li><Part imageUrl={'https://cdn.rebrickable.com/media/parts/elements/329923.jpg'} name={3299}/></li>
          <li><Part imageUrl={'https://cdn.rebrickable.com/media/parts/elements/346002.jpg'} name={3460}/></li>
          <input type="color" value={color} onChange={(e) => setColor(e.target.value)}></input>
        </ul>
    </div>
    )
}