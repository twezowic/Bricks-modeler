import './App.css';
import React from 'react';
import { Suspense } from 'react';
import { Canvas } from '@react-three/fiber'
import Model from './Model';
import Ground from './Ground';
import Controls from './Controls';
import { GizmoHelper, GizmoViewport, Gltf } from '@react-three/drei'
import { proxy } from 'valtio';

const state = proxy({ current: null, mode: 0 });

export default function Modeler(){
    return (
    <div className='canvas'>
        <Canvas camera={{ position: [0, 10, 10], fov: 50 }}>
            <pointLight position={[0, 10, 0]} intensity={100} />
            {/* <hemisphereLight color="#ffffff" groundColor="#b9b9b9" position={[-7, 25, 13]} intensity={0.85} /> */}
            <Suspense fallback={null}>
            <group position={[0,0.5,0]} scale={0.05} rotation={[-Math.PI / 2, 0, 0]}>
                <Model name="first" gltfPath="3299" position={[0,-30,0]} state={state}/>
                <Model name="second" gltfPath="3460" position={[0,30,0]} state={state}/>
                <Model name="third" gltfPath="3460" position={[0,-60,0]} state={state}/>
                <Gltf src="/2926.gltf"/>
            </group>
            <Ground />
            </Suspense>
            <Controls state={state}/>

            <GizmoHelper alignment="bottom-right" margin={[80, 80]}>
                <GizmoViewport axisColors={['#9d4b4b', '#2f7f4f', '#3b5b9d']} labelColor="white" />
            </GizmoHelper>
      </Canvas>
    </div>
    )
}