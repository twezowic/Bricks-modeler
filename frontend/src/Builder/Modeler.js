import React, { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import Model from './Model';
import Ground from './Ground';
import Controls from './Controls';
import { GizmoHelper, GizmoViewport } from '@react-three/drei';
import { proxy } from 'valtio';
import { ip } from "../utils"
import { v4 as uuidv4 } from 'uuid';
import { useAuth0 } from '@auth0/auth0-react';
import Renderer from './Renderer';
import { useSearchParams } from 'react-router-dom';
import Instruction from './Instruction';
import SaveDialog from './saveDialog';

const state = proxy({ mode: 0, selected: [] });

export default function Modeler({ color, selectedStep, setSelectedStep }) {
  const [searchParams] = useSearchParams();
  const set_id = Object.fromEntries([...searchParams]).set_id

  const [instructions, setInstructions] = useState([]);

  const fetchInstruction = async (setId) => {
      try {
          const response = await fetch(`${ip}/instruction/${setId}`, {
              method: 'GET',
          });
          const data = await response.json();
          setInstructions(data);
          // setSelectedStep(0);
      } catch (error) {
          console.error('Error fetching instructions:', error);
      }
  };

  useEffect(() => {
    const setUpReconstruction = async () => {
      if (set_id){
        await fetchInstruction(set_id)
      }
    };
    setUpReconstruction();
  }, []);

  const [models, setModels] = useState([]);
  const prevModelsRef = useRef(models);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const glRef = useRef(null);

  const [currentlyMoving, setCurrentlyMoving] = useState(false);
  const [correctSteps, setCorrectSteps] = useState(false);

  // Tylko prezentacja miejsce łączeń
  const [points, setPoints] = useState([]);
  const [tooglePoints, setTooglePoints] = useState(false);
  //

  const [groups, setGroups] = useState([]);
  const [seperateBy, setSeperateBy] = useState(undefined);

  useEffect(()=> {
    const selectSeperated = async () => {
      if (seperateBy) {
        const data = await getConnection()
        state.selected = data.find(group => group.includes(seperateBy));
        setSeperateBy(undefined)
      }
    }
    selectSeperated()
  }, [seperateBy])

  const { user, isAuthenticated } = useAuth0();

  // Logika wczytywania z loadera
  useEffect(() => {
    const loadHistory = async () => {
      let savedModels = sessionStorage.getItem('models');
      const modelsFromLoader = localStorage.getItem('models');
      const stepFromLoader = parseInt(localStorage.getItem('step'));
      setSelectedStep(stepFromLoader ? stepFromLoader : 0)

      if (modelsFromLoader){
        savedModels = modelsFromLoader;
        sessionStorage.setItem('models', JSON.stringify(models));
        localStorage.removeItem('models');
      }
      const modelsJSON = JSON.parse(savedModels)
      if (modelsJSON) {
        setModels(modelsJSON);
        await getConnection(modelsJSON)
      } else {
        setModels([]);
      }
    };
    loadHistory();
  }, []);


  useEffect(() => {
    const saveProgress = () => {
      sessionStorage.setItem('models', JSON.stringify(models));
    };

    const interval = setInterval(saveProgress, 15 * 1000); // 15 sekund

    return () => clearInterval(interval);
  }, [models]);

  useEffect(() => {
    const asyncCalculate = async () => {
      if (set_id){
        const result = await checkInstruction();
        setCorrectSteps(result);
      }
    };
    asyncCalculate();
}, [models, selectedStep]);
  

  useEffect(() => {
    prevModelsRef.current = models;
  }, [models]);

  // Shortkeys
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Delete') {
        const newModels = models.filter(model => !state.selected.includes(model.name));
        setModels(newModels);
        state.selected = [];
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

  async function generateSteps(name){
    try {
        const response = await fetch(`${ip}/instruction/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'models': models, 'user_id': user.sub, 'name': name})
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
    const partData = event.dataTransfer.getData('model');
    const colorData = event.dataTransfer.getData('color');
    
    // if (!data) {
    //   return;
    // }
    
    try {
      const part = JSON.parse(partData);
      if (colorData){
        const colorPart = JSON.parse(colorData);
        addNewModel(colorPart, part);
      }
      else {
        addNewModel(color, part);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const checkInstruction = async () => {
    try {
        const response = await fetch(`${ip}/instruction/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'set_id': set_id, 'step': selectedStep, 'models': models })
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
        const requestBody = { 'models': currentModels }
        if (seperateBy){
          requestBody['seperate_by'] = seperateBy
        }
        const response = await fetch(`${ip}/connection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        setGroups(data);
        return data;

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

  const saveScene = async (name) => {
    const thumbnail = await generateThumbnail();
    // const sceneData = JSON.stringify({ models, thumbnail });
    // var a = document.createElement('a');
    // var blob = new Blob([sceneData], { 'type': 'application/json' });
    // a.href = window.URL.createObjectURL(blob);
    // a.download = 'scene.json';
    // a.click();
    try {
      const requestBody = {
        name: name,
        track: models,
        thumbnail: thumbnail,
        user_id: user.sub,
      };
    
      if (set_id) {
        requestBody.set_id = set_id;
        requestBody.step = selectedStep;
      }
    
      const response = await fetch(`${ip}/tracks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
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

  const track_id = Object.fromEntries([...searchParams]).track_id

  const updateTrack = async () => {
    const thumbnail = await generateThumbnail();
    try {
      const requestBody = {
        track: models,
        thumbnail: thumbnail
      };
    
      if (set_id) {
        requestBody.step = selectedStep;
      }

      const response = await fetch(`${ip}/tracks/${track_id}`, {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
          throw new Error('Failed to update track');
      }

      alert('Track updated successfully.');
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update track.');
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
    className="float-right w-full h-[80vh] gap-10 relative"
    onDrop={handleDrop}
    onDragOver={handleDragOver}
  >
      {set_id && 
        <Instruction 
        images={instructions.map(step=>step.instruction)} 
        correctSteps={correctSteps} 
        currentStep={selectedStep} 
        setCurrentStep={setSelectedStep}
        />
      }
      <Canvas camera={{ position: [0, 10, 10], fov: 50 }} onCreated={({ gl, scene, camera }) => {
        glRef.current = gl;
        sceneRef.current = scene;
        cameraRef.current = camera;
      }}>
        <directionalLight position={[10, 10, 10]} intensity={1} castShadow />
        <Suspense fallback={null}>
          <group position={[0, 0, 0]} scale={0.05} rotation={[-Math.PI / 2, 0, 0]}>
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
                seperateBy={seperateBy}
                setSeperateBy={setSeperateBy}
                getConnection={getConnection}
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
          seperateBy={seperateBy}
        />
        <GizmoHelper alignment="bottom-right" margin={[80, 80]}>
          <GizmoViewport axisColors={['#9d4b4b', '#2f7f4f', '#3b5b9d']} labelColor="white" />
        </GizmoHelper>
      </Canvas>
      {isAuthenticated && 
        <div className='flex flex-row absolute bottom-1 left-1 z-10 gap-1'>
          <SaveDialog saveTrack={saveScene} updateTrack={updateTrack} trackId={track_id}/>
          {!set_id &&
             <Renderer glRef={glRef} sceneRef={sceneRef} cameraRef={cameraRef} getSteps={generateSteps}/>
          } 
        </div>
      }
    </div>
  );
}