import React from 'react';
import { IconButton } from '@mui/material';
import { ArrowForward, ArrowBack } from '@mui/icons-material';

const Instruction = ({ images, correctSteps, currentStep, setCurrentStep }) => {
    const nextImage = () => {
        if (currentStep < images.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const prevImage = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    return (
            <div className='absolute top-20 right-12 items-center justify-between flex gap-2 border-2 border-black z-10 bg-white'>
                <div className='flex flex-col'>
                <img
                    src={images[currentStep]}
                    alt={`carousel-image-${currentStep}`}
                    className='w-[400px] h-auto'
                />
                <div className='flex flex-row justify-between items-center px-4'>
                    <div className={`w-8 h-8  rounded-full ${correctSteps ? "bg-green-400" : "bg-red-600"}`}/>
                    <span className='text-[16px] px-4 py-2'>
                        {currentStep + 1} / {images.length}
                     </span>
                </div>
                </div> 
            <IconButton
                sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '10px',
                    transform: 'translateY(-50%)',
                    zIndex: 1,
                    backgroundColor: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    },
                }}
                onClick={prevImage}
            >
                <ArrowBack />
            </IconButton>
            <IconButton
                sx={{
                    position: 'absolute',
                    top: '50%',
                    right: '10px',
                    transform: 'translateY(-50%)',
                    zIndex: 1,
                    backgroundColor: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    },
                }}
                onClick={nextImage}
            >
                <ArrowForward />
            </IconButton>
            </div>
    );
};

export default Instruction;
