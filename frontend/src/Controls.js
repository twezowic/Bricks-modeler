import React from 'react';
import { useThree } from '@react-three/fiber';
import { useSnapshot } from 'valtio'
import { TransformControls } from '@react-three/drei';
import { OrbitControls } from '@react-three/drei';

const modes = ['translate', 'rotate', 'scale'];

export default function Controls({ state }) {
  const snap = useSnapshot(state);
  const scene = useThree((state) => state.scene);

  return (
    <>
      {snap.current && <TransformControls object={scene.getObjectByName(snap.current)} mode={modes[snap.mode]} />}
      <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
    </>
  );
}
