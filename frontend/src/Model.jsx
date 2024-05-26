import React, { useState } from 'react';
import { useSnapshot } from 'valtio';
import { useGLTF, useCursor } from '@react-three/drei';
import * as THREE from "three";

const modes = ['translate', 'rotate'];

export default function Model({ name, gltfPath, state, ...props }) {
  const snap = useSnapshot(state);
  const [hovered, setHovered] = useState(false);
  const { nodes } = useGLTF(gltfPath + '.gltf')

  useCursor(hovered);
  useGLTF.preload(gltfPath + '.gltf')
  return (
    <mesh
      onClick={(e) => (e.stopPropagation(), (state.current = name))}
      onPointerMissed={(e) => e.type === 'click' && (state.current = null)}
      onContextMenu={(e) => snap.current === name && (e.stopPropagation(), (state.mode = (snap.mode + 1) % modes.length))}
      onPointerOver={(e) => (e.stopPropagation(), setHovered(true))}
      onPointerOut={(e) => setHovered(false)}
      name={name}
      geometry={nodes[gltfPath].geometry}
      material={new THREE.MeshPhongMaterial()}
      // color, emissive, specular = ambient, difuse, specular
      material-color={snap.current === name ? 'red' : 'white'}
      material-specular={'#7c71a2'}
      dispose={null}
      {...props}
    />
  );
}

