import React from 'react';
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
    <div className="absolute top-20 right-12 flex items-center justify-between gap-2 border-2 border-black z-10 bg-white">
        <div className="flex flex-col">
            <img
            src={images[currentStep]}
            alt={`carousel-image-${currentStep}`}
            className="w-[400px] h-auto"
            />
            <div className="flex flex-row justify-between items-center px-4">
            <div className={`w-8 h-8 rounded-full ${correctSteps ? "bg-green-400" : "bg-red-600"}`} />
            <span className="text-[16px] px-4 py-2">
                {currentStep + 1} / {images.length}
            </span>
            </div>
        </div>
        <button
            className="absolute top-1/2 left-2 transform -translate-y-1/2 z-10 bg-white/70 hover:bg-white/90 rounded-full p-2"
            onClick={prevImage}
        >
            <ArrowBack />
        </button>
        <button
            className="absolute top-1/2 right-2 transform -translate-y-1/2 z-10 bg-white/70 hover:bg-white/90 rounded-full p-2"
            onClick={nextImage}
        >
            <ArrowForward />
        </button>
    </div>
    );
};

export default Instruction;
