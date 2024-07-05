import './App.css';
import Modeler from './Modeler';
import Explorer from './Explorer';
import React, { useState } from 'react';


function App() {
  const [selectedColor, setSelectedColor] = useState("#ff0000");
  const [selectedModel, setSelectedModel] = useState("2926")

  return (
    <>
      <Modeler color={selectedColor} model={selectedModel}/>
      <Explorer setColorModel={setSelectedColor} setModel={setSelectedModel}/>
    </>
  )
}

export default App;
