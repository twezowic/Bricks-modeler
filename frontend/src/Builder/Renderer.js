import * as THREE from 'three'
import { ip } from '../utils';
import { Button } from '@mui/material';
import { useState } from 'react';
import * as React from 'react';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

export default function Renderer({ glRef, sceneRef, cameraRef, getSteps }) {
  const [name, setName] = useState("");
  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setName('');
  };

  const handleSave = () => {
    generateInstruction(name);
    handleClose();
  };

  async function saveInstruction(instruction, set_id){
    try {
        const response = await fetch(`${ip}/instruction/generate`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'instruction': instruction, 'set_id': set_id })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log(data)
        return data;

    } catch (error) {
        console.error('Error fetching data:', error);
    }
  }

  const generateImage = (scene) => {
    if (!glRef.current || !scene || !cameraRef.current) return;
  
    const gl = glRef.current;
    const originalCamera = cameraRef.current;
  
    const width = 1920;
    const height = 1080;
  
    const camera = originalCamera.clone();
  
    const boundingBox = new THREE.Box3().setFromObject(scene);
    const center = boundingBox.getCenter(new THREE.Vector3());
    const size = boundingBox.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
  
    const fov = camera.fov * (Math.PI / 180);
    const distance = maxDim / (2 * Math.tan(fov / 2));
    camera.position.set(center.x, center.y + distance, center.z + distance);
    camera.lookAt(center);
    camera.updateProjectionMatrix();
  
    const prevClearColor = gl.getClearColor(new THREE.Color());
    const prevAlpha = gl.getClearAlpha();
  
    // kolor tła
    gl.setClearColor('#74b1ef', 1);
  
    const prevSize = gl.getSize(new THREE.Vector2());
    gl.setSize(width, height);
  
    gl.render(scene, camera);
  
    const dataURL = gl.domElement.toDataURL('image/png');
  
    gl.setSize(prevSize.x, prevSize.y);
    gl.setClearColor(prevClearColor, prevAlpha);
  
    return dataURL
  };

  const generateInstruction = async () => { 
    const images = [];

    const data = await getSteps(name);

    console.log(data)

    const set_id = data.set_id

    console.log(set_id)
  
    const modelsSteps = data.steps.map(step => step.models.map(model => model.model_id)).reverse();

    const sceneCopy = sceneRef.current.clone(true);


    // TODO do zastanowienia się
    // const ground = sceneCopy.children.find(
    //   (child) => child.type === "Mesh"
    // )

    // sceneCopy.remove(ground)

    const groupElement = sceneCopy.children.find(
      (child) => child.type === "Group"
    );
    const groupElements = groupElement.children;

    const firstImage = await generateImage(sceneCopy);
    images.push(firstImage);
  
    for (const models of modelsSteps) {
      const modelsToRemove = groupElements.filter(model => models.includes(model.name));
  
      modelsToRemove.forEach(modelToRemove => {
        groupElement.remove(modelToRemove);
      });
  
      const imageData = await generateImage(sceneCopy);
      images.push(imageData);
    }
    await saveInstruction(images.reverse().splice(1), set_id);
  };
  
  return (
    <React.Fragment>
    <button className='px-2 py-2 rounded-[8px] bg-white' onClick={handleClickOpen}>
      Generate Instruction
    </button>
    <Dialog
      open={open}
      onClose={handleClose}
    >
      <DialogTitle>Generate instruction</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Enter a name for your set.
        </DialogContentText>
            <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Track Name"
            type="text"
            fullWidth
            variant="standard"
            value={name}
            onChange={(e) => setName(e.target.value)}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} variant={'info'}>Cancel</Button>
        <Button type="button"onClick={handleSave}>Generate Instruction</Button>
      </DialogActions>
    </Dialog>
  </React.Fragment>
  );
}
