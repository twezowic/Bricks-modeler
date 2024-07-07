import './App.css';
import React, { useEffect, useState, useRef } from 'react';
import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import Model from './Model';
import Ground from './Ground';
import Controls from './Controls';
import { GizmoHelper, GizmoViewport } from '@react-three/drei';
import { proxy } from 'valtio';
import { ip } from "./utils"

const state = proxy({ current: null, mode: 0 });

export default function Modeler({ color, model }) {
  const [models, setModels] = useState([]);
  const prevModelsRef = useRef(models);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const glRef = useRef(null);
  const [counter, setCounter] = useState(0);

  useEffect(() => {
    prevModelsRef.current = models;
  }, [models]);

  // Shortkeys
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === ' ') {
        addNewModel(color, model);
      } else if (event.key === 'Enter') {
        saveScene();
      } else if (event.key === 'Backspace') {
        loadScene();
      } else if (event.key === 'Delete') {
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
    const response = await fetch(`${ip}/model/${model}`);
    const data = await response.json();
    return data['accessors'][0]['min'];
  };

  const addNewModel = async (color, model) => {
    const start_translation = await getBeginPosition(model);
    const newModel = {
      name: `model-${counter}`,
      gltfPath: model,
      position: setBeginPosition([0, 0, 0], start_translation),
      rotation: [0, 0, 0],
      color: color
    };
    setCounter(counter + 1);
    setModels((prevModels) => [...prevModels, newModel]);
  };

  const updateModelPosition = (name, newPosition, newRotation) => {
    const newModels = models.map((model) =>
      model.name === name ? { ...model, position: newPosition, rotation: newRotation } : model
    );
    setModels(newModels);
  };

  const saveScene = async () => {
    const thumbnail = await generateThumbnail();
    const sceneData = JSON.stringify({ models, thumbnail });
    console.log(sceneData);
    var a = document.createElement('a');
    var blob = new Blob([sceneData], { 'type': 'application/json' });
    a.href = window.URL.createObjectURL(blob);
    a.download = 'scene.json';
    a.click();

    try {
      const name = "a";
      const response = await fetch(`${ip}/tracks`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ 'name': name, 'track': models, 'thumbnail': thumbnail })
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

  const loadScene = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        const loadedModels = JSON.parse(reader.result)["models"];
        setModels(loadedModels);
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <div className='canvas'>
      <Canvas camera={{ position: [0, 10, 10], fov: 50 }} onCreated={({ gl, scene, camera }) => {
        glRef.current = gl;
        sceneRef.current = scene;
        cameraRef.current = camera;
      }}>
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
        <Controls state={state} />
        <GizmoHelper alignment="bottom-right" margin={[80, 80]}>
          <GizmoViewport axisColors={['#9d4b4b', '#2f7f4f', '#3b5b9d']} labelColor="white" />
        </GizmoHelper>
      </Canvas>
    </div>
  );
}
