import React, { useEffect, useState } from 'react';
import { ip } from '../utils';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Input } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { jsPDF } from 'jspdf';
import { useAuth0 } from '@auth0/auth0-react';
import Comments from './Comments';

export default function SetsDisplay() {
    const [sets, setSets] = useState([]);
    const [pageIndex, setPageIndex] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [selectedId, setSelectedId] = useState(undefined)
    const [instructions, setInstructions] = useState([]);
    const [currentStep, setCurrentStep] = useState(0);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const navigate = useNavigate();

    const fetchSets = async () => {
        try {
            const response = await fetch(`${ip}/sets/${pageIndex}`, {
                method: 'GET',
            });
            const data = await response.json();
            setSets(data.data);
            setTotalPages(data.total_pages);
        } catch (error) {
            console.error('Error fetching sets:', error);
        }
    };

    const fetchInstruction = async (setId) => {
        try {
            const response = await fetch(`${ip}/instruction/${setId}`, {
                method: 'GET',
            });
            const data = await response.json();
            setInstructions(data);
            setCurrentStep(0);
        } catch (error) {
            console.error('Error fetching instructions:', error);
        }
    };

    const openDialog = (setId) => {
        fetchInstruction(setId);
        setSelectedId(setId)
        setIsDialogOpen(true);
    };

    const closeDialog = () => {
        setSelectedId(undefined)
        setIsDialogOpen(false);
    };

    const handleNext = () => {
        if (currentStep < instructions.length - 1) {
            setCurrentStep((prev) => prev + 1);
        }
    };

    const handlePrevious = () => {
        if (currentStep > 0) {
            setCurrentStep((prev) => prev - 1);
        }
    };

    const saveToPDF = () => {
        const pdf = new jsPDF('landscape');

        const images = instructions.map(i=>i.instruction)

        images.forEach((image, index) => {
            if (index != 0){
                pdf.addPage();
            }
            pdf.addImage(image, 'PNG', 60, 30, 180, 160);
        });

        pdf.save('instruction.pdf')
    }

    useEffect(() => {
        fetchSets();
    }, [pageIndex]);

    return (
        <div className='flex flex-col justify-center px-[200px] gap-10 text-white text-[24px]'>
            <div className='grid grid-cols-4 gap-10'>
                {sets && sets.map((set) => (
                    <div key={set._id}>
                        <h3>{set.name}</h3>
                        {set.thumbnail && (
                            <img
                                src={set.thumbnail}
                                alt={set.name}
                                width={600}
                                height={600}
                                onClick={() => openDialog(set._id)}
                                className="cursor-pointer"
                            />
                        )}
                    </div>
                ))}
            </div>
            <div className='flex flex-row justify-between text-white'>
                <button
                    onClick={() => setPageIndex(pageIndex - 1)}
                    disabled={pageIndex === 0}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
                >
                    Previous
                </button>
                <button
                    onClick={() => setPageIndex(pageIndex + 1)}
                    disabled={pageIndex === totalPages - 1}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
                >
                    Next
                </button>
            </div>

            <Dialog open={isDialogOpen} onClose={closeDialog} fullWidth maxWidth="lg">
                <DialogTitle>Instruction</DialogTitle>
                <DialogContent className='flex flex-row gap-10'>
                    <div className='flex flex-row gap-6'>
                        {instructions.length > 0 ? (
                            <div>
                                <img
                                    src={instructions[currentStep].instruction}
                                    alt={`Step ${currentStep + 1}`}
                                    className="w-full h-auto"
                                />
                                <p className="mt-4 text-center">Step {currentStep + 1}</p>
                            </div>
                        ) : (
                            <p>Loading instructions...</p>
                        )}
                        <Comments selectedId={selectedId}/>
                    </div>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handlePrevious} disabled={currentStep === 0}>
                        Previous
                    </Button>
                    <Button onClick={handleNext} disabled={currentStep === instructions.length - 1}>
                        Next
                    </Button>
                    <Button onClick={closeDialog}>Close</Button>
                    <Button
                        component="a"
                        onClick={()=>(navigate(`/?set_id=${selectedId}`))}
                    >
                        Build
                    </Button>
                    <Button onClick={saveToPDF}>
                        Save to PDF
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}