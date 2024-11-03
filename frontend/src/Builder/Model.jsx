import React, { useState, useRef } from 'react';
import { useSnapshot } from 'valtio';
import { useGLTF, useCursor } from '@react-three/drei';
import * as THREE from "three";
import { useFrame } from '@react-three/fiber';
import { ip } from '../utils';

const modes = ['translate', 'rotate'];

export default function Model({ name, gltfPath, state, color = 'white', onPositionChange, groups, currentlyMoving, ...props }) {
  const snap = useSnapshot(state);
  const [hovered, setHovered] = useState(false);
  const { nodes } = useGLTF(`${ip}/model/${gltfPath}`);
  const ref = useRef();
  const prevPosition = useRef([0, 0, 0]);
  const prevRotation = useRef([0, 0, 0]);

  useCursor(hovered);
  useGLTF.preload(`${ip}/model/${gltfPath}`);

  useFrame(() => {
    if (ref.current) {
      const { position, rotation } = ref.current;
      const currentPosition = [position.x, position.y, position.z];
      const currentRotation = [rotation.x, rotation.y, rotation.z];

      if (!metadataEqual(currentPosition, prevPosition.current) || !metadataEqual(currentRotation, prevRotation.current)) {
        onPositionChange(currentPosition, currentRotation);
        prevPosition.current = currentPosition;
        prevRotation.current = currentRotation;
      }
    }
  });



  function metadataEqual(meta1, meta2) {
    return meta1[0] === meta2[0] && meta1[1] === meta2[1] && meta1[2] === meta2[2];
  }


  function findHeight(modelName) {
    for (const group of groups) {
        const height = group.find(([name]) => name === modelName);
        if (height) return height[1];
      }
  }

  function getModelsHigherThan(group, minHeight) {
    var result = [];
    for (const [model, height] of group) {
      if (height > minHeight) {
        result.push(model)
      }
    }
    return result;
  }

  function handleClick(e) {
    e.stopPropagation();
    console.log("model", currentlyMoving)
    if (!currentlyMoving) {
      for (const group of groups) {
        const groupModels = group.map((model)=>(model[0]))
        if (groupModels.includes(name)){
          if (snap.selected.length !== 1 && snap.selected.includes(name)) { 
            const selectedHeight = findHeight(name);
            state.selected = [name].concat(getModelsHigherThan(group, selectedHeight));
          }
          else {
            state.selected = groupModels;
          }
          break;
        }
      }
    }
  }

  return (
    <mesh
      ref={ref}
      onClick={handleClick}
      onPointerMissed={(e) => e.type === 'click' && (state.selected = [])}
      onContextMenu={(e) => snap.selected.includes(name) && (e.stopPropagation(), (state.mode = (snap.mode + 1) % modes.length))}
      onPointerOver={(e) => (e.stopPropagation(), setHovered(true))}
      onPointerOut={(e) => setHovered(false)}
      name={name}
      geometry={nodes[gltfPath].geometry}
      material={new THREE.MeshPhongMaterial()}
      material-color={color}
      material-specular={'#7c71a2'}
      dispose={null}
      {...props}
      >
    </mesh>
  );
}