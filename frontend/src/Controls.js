import React, { useEffect, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { useSnapshot } from 'valtio';
import { TransformControls } from '@react-three/drei';
import { OrbitControls } from '@react-three/drei';

const modes = ['translate', 'rotate'];
const step = 10;
const vertical = 2.5;
const rotationStep = Math.PI / 2;

export default function Controls({ state }) {
  const snap = useSnapshot(state);
  const { scene, camera, gl } = useThree();
  const transformControls = useRef();

  useEffect(() => {
    const controls = transformControls.current;

    if (controls) {
      const onChange = () => {
        const object = controls.object;
        if (controls.mode === 'translate') {
          object.position.x = Math.round(object.position.x / step) * step;
          object.position.y = Math.round(object.position.y / step) * step;
          object.position.z = Math.round(object.position.z / vertical) * vertical;
        }
        else if (controls.mode === 'rotate') {
          object.rotation.x = Math.round(object.rotation.x / rotationStep) * rotationStep;
          object.rotation.y = Math.round(object.rotation.y / rotationStep) * rotationStep;
          object.rotation.z = Math.round(object.rotation.z / rotationStep) * rotationStep;
        }
      };

      controls.addEventListener('objectChange', onChange);


      return () => {
        controls.removeEventListener('objectChange', onChange);
      };
    }
  }, [snap.current, step]);

  return (
    <>
      {snap.current && (
        <TransformControls
          ref={transformControls}
          object={scene.getObjectByName(snap.current)}
          mode={modes[snap.mode]}
          camera={camera}
          gl={gl.domElement}
        />
      )}
      <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
    </>
  );
}
