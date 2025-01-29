import React, { useEffect, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { useSnapshot } from 'valtio';
import { TransformControls } from '@react-three/drei';
import { OrbitControls } from '@react-three/drei';

const modes = ['translate', 'rotate'];
const step = 10;
const vertical = 8;
const rotationStep = Math.PI / 2;

export default function Controls({ state, getConnection, setCurrentlyMoving, models, setModels }) {
  const snap = useSnapshot(state);
  const { scene, camera, gl } = useThree();
  const transformControls = useRef();
  const initialTransforms = useRef({});

  function roundPosition(object) {
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
    if (transformControls.current.mode === 'rotate') {
      object.rotation.x = Math.round(object.rotation.x / rotationStep) * rotationStep;
      object.rotation.y = Math.round(object.rotation.y / rotationStep) * rotationStep;
      object.rotation.z = Math.round(object.rotation.z / rotationStep) * rotationStep;
    }
  }

  function rotatePoint3D(center, object, radZ) {
    const translatedX = object.x - center.x;
    const translatedY = object.y - center.y;
    const translatedZ = object.z - center.z;

    const finalPointX = translatedX * Math.cos(radZ) - translatedY * Math.sin(radZ);
    const finalPointY = translatedX * Math.sin(radZ) + translatedY * Math.cos(radZ);
    const finalPointZ = translatedZ;

    return {
        x: finalPointX + center.x,
        y: finalPointY + center.y,
        z: finalPointZ + center.z
    };
  }

  useEffect(() => {
    const controls = transformControls.current;

    if (controls) {
      const onChange = () => {
        setCurrentlyMoving(true);
        const mainObject = controls.object;

        const deltaX = mainObject.position.x - initialTransforms.current[mainObject.name].position.x;
        const deltaY = mainObject.position.y - initialTransforms.current[mainObject.name].position.y;
        const deltaZ = mainObject.position.z - initialTransforms.current[mainObject.name].position.z;

        const deltaRotZ = mainObject.rotation.z - initialTransforms.current[mainObject.name].rotation.z;
        
        roundPosition(mainObject);

        snap.selected.forEach((name) => {
          const object = scene.getObjectByName(name);

          if (object && object.name !== mainObject.name) {
            object.position.x = initialTransforms.current[name].position.x + deltaX;
            object.position.y = initialTransforms.current[name].position.y + deltaY;
            object.position.z = initialTransforms.current[name].position.z + deltaZ;
            
            object.rotation.z = initialTransforms.current[name].rotation.z + deltaRotZ;
            const rotated = rotatePoint3D(
              mainObject.position, 
              object.position, 
              Math.round(deltaRotZ / rotationStep) * rotationStep
            )
            object.position.x = rotated.x;
            object.position.y = rotated.y;
            object.position.z = rotated.z;

            roundPosition(object);
          }
        });
      };

      const onFinishMove = async () => {
        const updatedModels = models.map((model) => {
          if (snap.selected.includes(model.name)) {
            const object = scene.getObjectByName(model.name);
  
            if (object) {
              return {
                ...model,
                position: [object.position.x, object.position.y, object.position.z],
                rotation: [object.rotation.x, object.rotation.y, object.rotation.z],
              };
            }
          }
          return model;
        });

        console.log(updatedModels)
  
        setModels(updatedModels);

        try {
          await getConnection(updatedModels);
        } catch (error) {
          console.error("Error fetching groups:", error);
        } finally {
          setCurrentlyMoving(false);
        }
      };

      controls.addEventListener('objectChange', onChange);
      controls.addEventListener('mouseUp', onFinishMove);

      return () => {
        controls.removeEventListener('objectChange', onChange);
        controls.removeEventListener('mouseUp', onFinishMove);
      };
    }
  }, [snap.selected, snap.mode, scene, getConnection]);

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
          showX={modes[snap.mode] === 'translate'}
          showZ={modes[snap.mode] === 'translate'}
        />
      )}
      <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
    </>
  );
}
