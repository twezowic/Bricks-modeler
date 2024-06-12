import React, { useState, useRef } from 'react';
import { useSnapshot } from 'valtio';
import { useGLTF, useCursor } from '@react-three/drei';
import * as THREE from "three";
import { useFrame } from '@react-three/fiber';

const modes = ['translate', 'rotate'];

export default function Model({ name, gltfPath, state, color = 'white', onPositionChange, ...props }) {
  const snap = useSnapshot(state);
  const [hovered, setHovered] = useState(false);
  const { nodes } = useGLTF(gltfPath + '.gltf');
  const ref = useRef();
  const prevPosition = useRef([0, 0, 0]);
  const prevRotation = useRef([0, 0, 0]);

  useCursor(hovered);
  useGLTF.preload(gltfPath + '.gltf');

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

  function metadataEqual(pos1, pos2) {
    return pos1[0] === pos2[0] && pos1[1] === pos2[1] && pos1[2] === pos2[2];
  }

  return (
    <mesh
      ref={ref}
      onClick={(e) => (e.stopPropagation(), (state.current = name))}
      onPointerMissed={(e) => e.type === 'click' && (state.current = null)}
      onContextMenu={(e) => snap.current === name && (e.stopPropagation(), (state.mode = (snap.mode + 1) % modes.length))}
      onPointerOver={(e) => (e.stopPropagation(), setHovered(true))}
      onPointerOut={(e) => setHovered(false)}
      name={name}
      geometry={nodes[gltfPath].geometry}
      material={new THREE.MeshPhongMaterial()}
      // color, emissive, specular = ambient, difuse, specular
      material-color={color}
      material-specular={'#7c71a2'}
      dispose={null}
      {...props}
    />
  );
}
