import Modeler from './Modeler';
import Explorer from './Explorer';

import React, { useState } from 'react';

function Main() {
    const [selectedColor, setSelectedColor] = useState("#ff0000");
    const [selectedModel, setSelectedModel] = useState("2926")

    const [selectedStep, setSelectedStep] = useState(0)

    return (
      <>
        <Modeler color={selectedColor} model={selectedModel} selectedStep={selectedStep} setSelectedStep={setSelectedStep}/>
        <Explorer setColorModel={setSelectedColor} setModel={setSelectedModel} selectedStep={selectedStep}/>
      </>
    )
  }

  export default Main;
