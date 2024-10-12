import Modeler from './Modeler';
import Explorer from './Explorer';

import React, { useState } from 'react';
import Profile from './Account/profile';
import { useAuth0 } from '@auth0/auth0-react';

function Main() {
    const [selectedColor, setSelectedColor] = useState("#ff0000");
    const [selectedModel, setSelectedModel] = useState("2926")

    return (
      <>
        <Modeler color={selectedColor} model={selectedModel}/>
        <Explorer setColorModel={setSelectedColor} setModel={setSelectedModel}/>
        <Profile/>
      </>
    )
  }

  export default Main;
