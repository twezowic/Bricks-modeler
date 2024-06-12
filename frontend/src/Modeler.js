import './App.css';
import React, { useEffect, useState, useRef  } from 'react';
import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import Model from './Model';
import Ground from './Ground';
import Controls from './Controls';
import { GizmoHelper, GizmoViewport } from '@react-three/drei';
import { proxy } from 'valtio';

const state = proxy({ current: null, mode: 0 });

export default function Modeler({color, model}) {
  const [models, setModels] = useState([
  ]);
  const prevModelsRef = useRef(models);


  useEffect(() => {
    prevModelsRef.current = models;
  }, [models]);

  // Shortkeys
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === ' ') {
        addNewModel(color, model);
      }
      else if (event.key === 'Enter'){
        saveScene();
      }
      else if (event.key === "Backspace"){
        loadScene();
      }
      else if (event.key === "Delete"){
        const newModels = models.filter(model => model.name !== state.current);
        setModels(newModels);
        state.current = null;
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  });

  function setBeginPosition(model, vector) {
    const result = [];
    for (let i = 0; i < model.length; i++) {
      result.push(model[i] - vector[i]);
    }
    return result;
  }

  const getBeginPosition = async (model) => {
    const response = await fetch('/' + model + '.gltf');
    const data = await response.json();
    return data['accessors'][0]['min'];
  };

  const addNewModel = async (color, model) => {
    const start_translation = await getBeginPosition(model);
    const newModel = {
      name: `model-${models.length + 1}`,
      gltfPath: model,
      position: setBeginPosition([0, 0, 0], start_translation),
      rotation: [0, 0, 0],
      color: color
    };
    setModels((prevModels) => [...prevModels, newModel]);
  };

  const updateModelPosition = (name, newPosition, newRotation) => {
    const newModels = models.map((model) =>
      model.name === name ? { ...model, position: newPosition, rotation: newRotation } : model
    );
    setModels(newModels);
  };

  const saveScene = () => {
    const sceneData = JSON.stringify(models);
    console.log(sceneData)
    var a = document.createElement('a');
    var blob = new Blob([sceneData], {'type':'application/json'});
    a.href = window.URL.createObjectURL(blob);
    a.download = 'scene.json';
    a.click();
  };


  const loadScene = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        const loadedModels = JSON.parse(reader.result);
        setModels(loadedModels);
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <div className='canvas'>
      <Canvas camera={{ position: [0, 10, 10], fov: 50 }}>
        <pointLight position={[0, 10, 0]} intensity={100} />
        {/* <hemisphereLight color="#ffffff" groundColor="#b9b9b9" position={[-7, 25, 13]} intensity={0.85} /> */}
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
                onPositionChange={(newPosition, newRotation) => updateModelPosition(model.name, newPosition, newRotation)}
              />
            ))}
          </group>
          <Ground />
        </Suspense>
        <Controls state={state}/>
        <GizmoHelper alignment="bottom-right" margin={[80, 80]}>
          <GizmoViewport axisColors={['#9d4b4b', '#2f7f4f', '#3b5b9d']} labelColor="white" />
        </GizmoHelper>
      </Canvas>
    </div>
  );
}
