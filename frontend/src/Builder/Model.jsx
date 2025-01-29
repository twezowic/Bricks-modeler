import React, { useState, useRef } from 'react';
import { useSnapshot } from 'valtio';
import { useGLTF, useCursor } from '@react-three/drei';
import * as THREE from "three";
import { ip } from '../utils';

const modes = ['translate', 'rotate'];

export default function Model({ name, gltfPath, state, color = 'white', groups, currentlyMoving, seperateBy,setSeperateBy, ...props }) {
  const snap = useSnapshot(state);
  const [hovered, setHovered] = useState(false);
  const { nodes } = useGLTF(`${ip}/model/${gltfPath}`);
  const ref = useRef();

  useCursor(hovered);
  useGLTF.preload(`${ip}/model/${gltfPath}`);

  function handleClick(e) {
    e.stopPropagation();
    if (!currentlyMoving) {
      for (const group of groups) {
        if (group.includes(name)){
          if (snap.selected.length !== 1 && snap.selected.includes(name) && !seperateBy) { 
            setSeperateBy(name);
          }
          else {
            state.selected = group;
            setSeperateBy(undefined);
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