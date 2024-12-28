import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import Model from './Model';
import Ground from './Ground';
import Controls from './Controls';
import { GizmoHelper, GizmoViewport } from '@react-three/drei';
import { proxy, useSnapshot } from 'valtio';
import { ip } from "../utils"
import { v4 as uuidv4 } from 'uuid';
import { useAuth0 } from '@auth0/auth0-react';
import Renderer from './Renderer';

const state = proxy({ mode: 0, selected: [] });

export default function Modeler({ color }) {
  const [models, setModels] = useState([]);
  const prevModelsRef = useRef(models);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const glRef = useRef(null);

  const [currentlyMoving, setCurrentlyMoving] = useState(false);
  const [correctSteps, setCorrectSteps] = useState(false);

  const [points, setPoints] = useState([]);
  const [tooglePoints, setTooglePoints] = useState(false);

  const snap = useSnapshot(state);
  const [groups, setGroups] = useState([]);

  const location = useLocation();

  const { user, isAuthenticated } = useAuth0();

  // Logika wczytywania z loadera
  useEffect(() => {
    const loadHistory = async () => {
      if (location.state?.models) {
        setModels(location.state.models);
        await getConnection(location.state.models)
      } else {
        setModels([]);
      }
    };
    loadHistory();
  }, []);

//   useEffect(() => {
//     const asyncCalculate = async () => {
//       const result = await checkInstruction();
//       setCorrectSteps(result);
//     };
//     asyncCalculate();
// }, [models]);
  

  useEffect(() => {
    prevModelsRef.current = models;
  }, [models]);

  // Shortkeys
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Enter') {
        saveScene();
      } else if (event.key === '\\') {
        // loadScene();
        // saveInstructionSteps()
      } else if (event.key === 'Delete') {
        const newModels = models.filter(model => !state.selected.includes(model.name));
        setModels(newModels);
        state.selected = [];
      } 
      else if (event.key === "k") {
        // checkInstruction();
        generateSteps()
      }
      else if (event.key === 'Shift') {
        setTooglePoints(!tooglePoints);
        if (!tooglePoints){
          getConnection123();
        }
      }

    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  });

  async function generateSteps(){
    try {
        const response = await fetch(`${ip}/instruction/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'models': models, 'user_id': '1', 'name': '1' })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log(data)
        return data;

    } catch (error) {
        console.error('Error fetching data:', error);
    }
  }

  const handleDrop = async (event) => {
    event.preventDefault();
    const data = event.dataTransfer.getData('model');
    
    // if (!data) {
    //   return;
    // }
    
    try {
      const part = JSON.parse(data);
      console.log(part)
      addNewModel(color, part);
    } catch (error) {
      console.error(error);
    }
  };

  const saveInstructionSteps = async () => {
    try {
      const response = await fetch(`${ip}/prepare_instruction`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ 'models': models })
      });

      if (!response.ok) {
          throw new Error('Network response was not ok');
      }

  } catch (error) {
      console.error('Error fetching data:', error);
  }
  }

  const checkInstruction = async () => {
    const set_id = 0;
    const step = 1;
    try {
        const response = await fetch(`${ip}/instruction/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'set_id': set_id, 'step': step, 'models': models })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log(data)
        return data;

    } catch (error) {
        console.error('Error fetching data:', error);
    }
};
  
  
  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const getConnection = async (currentModels=models) => {
    try {
        const response = await fetch(`${ip}/connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'models': currentModels })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        setGroups(data);

    } catch (error) {
        console.error('Error fetching data:', error);
    }
};


  function setBeginPosition(model, vector) {
    const result = [];
    for (let i = 0; i < model.length; i++) {
      result.push(model[i] - vector[i]);
    }
    return result;
  }

  const getBeginPosition = async (model) => {
    const response = await fetch(`${ip}/model/${model}`);
    const data = await response.json();
    return data['accessors'][0]['min'];
  };

  const addNewModel = async (color, model) => {
    const start_translation = await getBeginPosition(model);
    const newModel = {
      name: `model-${uuidv4()}`,
      gltfPath: model,
      position: setBeginPosition(getEmptySpace(), start_translation),
      rotation: [0, 0, 0],
      color: color
    };
    const newModels = [...models, newModel];
    setModels(newModels);
    
    await getConnection(newModels);
  };  

  const getEmptySpace = () => {
    if (models.length === 0) {
      return [0, 0, 0];
    }

    let minX = models[0].position[0];
    let minY = models[0].position[1];

    for (let i = 1; i < models.length; i++) {
      const posX = models[i].position[0];
      const posY = models[i].position[1];

      if (posX < minX) {
        minX = posX;
      }
      if (posY < minY) {
        minY = posY;
      }
    }
    return [minX - 100, minY - 100, 0];
  };

  const saveScene = async () => {
    const thumbnail = await generateThumbnail();
    // const sceneData = JSON.stringify({ models, thumbnail });
    // var a = document.createElement('a');
    // var blob = new Blob([sceneData], { 'type': 'application/json' });
    // a.href = window.URL.createObjectURL(blob);
    // a.download = 'scene.json';
    // a.click();

    try {
      const name = "a";
      const response = await fetch(`${ip}/tracks`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ 'name': name, 'track': models, 'thumbnail': thumbnail, 'user_id': user.sub })
      });

      if (!response.ok) {
          throw new Error('Failed to add track');
      }

      alert('Track added successfully.');
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add track.');
    }
  };

  const generateThumbnail = () => {
    return new Promise((resolve) => {
      const gl = glRef.current;
      const scene = sceneRef.current;
      const camera = cameraRef.current;
      gl.render(scene, camera);
      const dataURL = gl.domElement.toDataURL('image/png');
      resolve(dataURL);
    });
  };

  // const loadScene = () => {
  //   const input = document.createElement('input');
  //   input.type = 'file';
  //   input.accept = '.json';
  //   input.onchange = e => {
  //     const file = e.target.files[0];
  //     const reader = new FileReader();
  //     reader.onload = () => {
  //       const loadedModels = JSON.parse(reader.result)["models"];
  //       setModels(loadedModels);
  //     };
  //     reader.readAsText(file);
  //   };
  //   input.click();
  // };

  const getConnection123 = async () => {
    try {
        const response = await fetch(`${ip}/connection123`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'models': models })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        console.log(data);

        const newPoints = data.map(item => ({
            point: item.point,
            color: item.color
        }));
        setPoints(newPoints);

    } catch (error) {
        console.error('Error fetching data:', error);
    }
};


  const Points = ({ data }) => {
    return (
      <>
        {data.map((point, index) => (
          <Point key={index} position={point.point} color={point.color}/>
        ))}
      </>
    );
  };

  const Point = ({ position, color }) => {
    return (
      <mesh position={position}>
        <sphereGeometry args={[5, 10, 10]} />
        <meshStandardMaterial color={color} />
      </mesh>
    );
  };

  return (
    <div
    className="float-right w-full h-[80vh] gap-10"
    onDrop={handleDrop}
    onDragOver={handleDragOver}
  >
      {/* <div className={`absolute top-20 right-12 items-center justify-between px-2 flex gap-2 border-2 border-black`}>
        <div className={`w-8 h-8 rounded-full ${correctSteps ? "bg-green-400" : "bg-red-600"}`}/>
        <img
          src={'/instruction_temp.png'}
          alt={`instruction_temp`}
          className='w-[200px] h-auto border-l-2 border-black'
        />
      </div> */}
      <Canvas camera={{ position: [0, 10, 10], fov: 50 }} onCreated={({ gl, scene, camera }) => {
        glRef.current = gl;
        sceneRef.current = scene;
        cameraRef.current = camera;
      }}>
        <directionalLight position={[10, 10, 10]} intensity={1} castShadow />
        <Suspense fallback={null}>
          <group position={[0, 0.5, 0]} scale={0.05} rotation={[-Math.PI / 2, 0, 0]}>
            {models.map((model, index) => (
              <Model
                key={index}
                name={model.name}
                gltfPath={model.gltfPath}
                position={model.position}
                rotation={model.rotation}
                state={state}
                color={model.color}
                groups={groups}
                currentlyMoving={currentlyMoving}
              />
            ))}
            {tooglePoints &&
              <Points data={points} />
            }
          </group>
          <Ground />
        </Suspense>
        <Controls 
          state={state} 
          getConnection={getConnection} 
          setCurrentlyMoving={setCurrentlyMoving} 
          models={models}
          setModels={setModels}
        />
        <GizmoHelper alignment="bottom-right" margin={[80, 80]}>
          <GizmoViewport axisColors={['#9d4b4b', '#2f7f4f', '#3b5b9d']} labelColor="white" />
        </GizmoHelper>
        {/* <RenderToPNG/> */}
      </Canvas>
      <div>

      <Renderer glRef={glRef} sceneRef={sceneRef} cameraRef={cameraRef} getSteps={generateSteps}/>
      </div>
    </div>
  );
}