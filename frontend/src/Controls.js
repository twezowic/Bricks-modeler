import React, { useEffect, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { useSnapshot } from 'valtio';
import { TransformControls } from '@react-three/drei';
import { OrbitControls } from '@react-three/drei';

const modes = ['translate', 'rotate'];
const step = 10;
const vertical = 8;
const rotationStep = Math.PI / 2;

export default function Controls({ state }) {
  const snap = useSnapshot(state);
  const { scene, camera, gl } = useThree();
  const transformControls = useRef();
  const initialTransforms = useRef({}); 

  function roundPosition(object) {
    if (transformControls.current.mode === 'translate') {
      if (object.rotation.x === Math.PI / 2 || object.rotation.x === -Math.PI / 2) {
        object.position.x = Math.round(object.position.x / step) * step;
        object.position.y = Math.round(object.position.y / vertical) * vertical;
        object.position.z = Math.round(object.position.z / step) * step;
      } else if (object.rotation.y === Math.PI / 2 || object.rotation.y === -Math.PI / 2) {
        object.position.x = Math.round(object.position.x / vertical) * vertical;
        object.position.y = Math.round(object.position.y / step) * step;
        object.position.z = Math.round(object.position.z / step) * step;
      } else {
        object.position.x = Math.round(object.position.x / step) * step;
        object.position.y = Math.round(object.position.y / step) * step;
        object.position.z = Math.round(object.position.z / vertical) * vertical;
      }
    } else if (transformControls.current.mode === 'rotate') {
      object.rotation.x = Math.round(object.rotation.x / rotationStep) * rotationStep;
      object.rotation.y = Math.round(object.rotation.y / rotationStep) * rotationStep;
      object.rotation.z = Math.round(object.rotation.z / rotationStep) * rotationStep;
    }
  }

  useEffect(() => {
    const controls = transformControls.current;

    if (controls) {
      const onChange = () => {
        const mainObject = controls.object;

        const deltaX = mainObject.position.x - initialTransforms.current[mainObject.name].position.x;
        const deltaY = mainObject.position.y - initialTransforms.current[mainObject.name].position.y;
        const deltaZ = mainObject.position.z - initialTransforms.current[mainObject.name].position.z;

        const deltaRotX = mainObject.rotation.x - initialTransforms.current[mainObject.name].rotation.x;
        const deltaRotY = mainObject.rotation.y - initialTransforms.current[mainObject.name].rotation.y;
        const deltaRotZ = mainObject.rotation.z - initialTransforms.current[mainObject.name].rotation.z;

        roundPosition(mainObject);

        snap.selected.forEach((name) => {
          const object = scene.getObjectByName(name);

          if (object && object.name !== mainObject.name) {
            object.position.x = initialTransforms.current[name].position.x + deltaX;
            object.position.y = initialTransforms.current[name].position.y + deltaY;
            object.position.z = initialTransforms.current[name].position.z + deltaZ;

            object.rotation.x = initialTransforms.current[name].rotation.x + deltaRotX;
            object.rotation.y = initialTransforms.current[name].rotation.y + deltaRotY;
            object.rotation.z = initialTransforms.current[name].rotation.z + deltaRotZ;

            roundPosition(object);
          }
        });
      };

      controls.addEventListener('objectChange', onChange);

      return () => {
        controls.removeEventListener('objectChange', onChange);
      };
    }
  }, [snap.selected, snap.mode, scene]);

  useEffect(() => {
    snap.selected.forEach((name) => {
      const object = scene.getObjectByName(name);
      if (object) {
        initialTransforms.current[name] = {
          position: {
            x: object.position.x,
            y: object.position.y,
            z: object.position.z,
          },
          rotation: {
            x: object.rotation.x,
            y: object.rotation.y,
            z: object.rotation.z,
          },
        };
      }
    });
  }, [snap.selected, scene]);

  return (
    <>
      {snap.selected.length > 0 && (
        <TransformControls
          ref={transformControls}
          object={scene.getObjectByName(snap.selected[0])}
          mode={modes[snap.mode]}
          camera={camera}
          gl={gl.domElement}
        />
      )}
      <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
    </>
  );
}
