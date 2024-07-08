import Modeler from './Modeler';
import Explorer from './Explorer';

import React, { useState } from 'react';

function Main() {
    const [selectedColor, setSelectedColor] = useState("#ff0000");
    const [selectedModel, setSelectedModel] = useState("2926")

    return (
      <>
        <Modeler color={selectedColor} model={selectedModel}/>
        <Explorer setColorModel={setSelectedColor} setModel={setSelectedModel}/>
      </>
    )
  }

  export default Main;
