import React, { useState, useRef } from 'react';
import { useSnapshot } from 'valtio';
import { useGLTF, useCursor } from '@react-three/drei';
import * as THREE from "three";
import { useFrame } from '@react-three/fiber';

const modes = ['translate', 'rotate'];

export default function Model({ name, gltfPath, state, color = 'white', onPositionChange, ...props }) {
  const snap = useSnapshot(state);
  const [hovered, setHovered] = useState(false);
  const { nodes } = useGLTF(gltfPath);
  const ref = useRef();
  const prevPosition = useRef([0, 0, 0]);
  const prevRotation = useRef([0, 0, 0]);

  useCursor(hovered);
  useGLTF.preload(gltfPath);

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

  const pivotPoint = new THREE.Vector3(0, 0, 0);

  function getName(str) {
    const segments = str.split('/');
    return segments[segments.length - 1];
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
      geometry={nodes[getName(gltfPath)].geometry}
      material={new THREE.MeshPhongMaterial()}
      // color, emissive, specular = ambient, difuse, specular
      material-color={color}
      material-specular={'#7c71a2'}
      dispose={null}
      {...props}
      >
      <group position={pivotPoint}>
        {props.children}
      </group>
    </mesh>
  );
}
