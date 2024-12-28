import * as THREE from 'three'
import { jsPDF } from 'jspdf';
import { ip } from '../utils';

export default function Renderer({ glRef, sceneRef, cameraRef, getSteps }) {
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
    gl.setClearColor('#74b1ef', 1); // Czarny kolor tła
  
    // Tymczasowy rozmiar renderera
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

    const data = await getSteps();

    const set_id = data.set_id

    console.log(set_id)
  
    const modelsSteps = data.steps.map(step => step.models.map(model => model.model_id));
  
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

    // const pdf = new jsPDF('landscape');

    // images.reverse().forEach((image, index) => {
    //   if (index > 1) pdf.addPage();
    //   pdf.addImage(image, 'PNG', 60, 30, 180, 160);
    // });

    // pdf.save('zapisana_instrucja.pdf')

    await saveInstruction(images.splice(1).reverse(), set_id);
  };
  
  return (
    <button onClick={generateInstruction} className='px-100'>Klik</button>
  );
}
