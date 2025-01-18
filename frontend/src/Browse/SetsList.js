import React, { useEffect, useState } from 'react';
import { ip } from '../utils';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Input } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { jsPDF } from 'jspdf';
import { useAuth0 } from '@auth0/auth0-react';

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

    const [comments, setComments] = useState([]);
    const [comment, setComment] = useState("");
    const { user, isAuthenticated } = useAuth0();

    useEffect(() => {
        fetchComments();
    }, [selectedId])

    const fetchComments = async () => {
        try {
            if (selectedId){
                const response = await fetch(`${ip}/comment/${selectedId}`);
                if (response.ok) {
                  const data = await response.json();
                  setComments(data);
                } else {
                  console.error("Failed to fetch comments");
                }
            }
        } catch (error) {
          console.error("Error fetching comments:", error);
        }
      };
    
      const addComment = async () => {
        const newReview = {
          set_id: selectedId,
          comment,
          user_id: user.nickname,
        };
    
        try {
          const response = await fetch(`${ip}/comment`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(newReview),
          });
    
          if (response.ok) {
            fetchComments();
            setComment("");
          } else {
            console.error("Failed to add comment");
          }
        } catch (error) {
          console.error("Error adding comment:", error);
        }
      };


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
                        <div className='flex flex-col w-[1000px] h-full justify-between'>
                            <div className='flex flex-col max-h-[400px] h-full overflow-y-scroll p-4 gap-2'>
                                {comments.map((user_comment, index) => (
                                    <div key={index} className={`rounded-md p-1 ${user_comment.user_id === user.nickname ? "self-end bg-green-300" : 'self-start bg-cyan-600'}`}>
                                        <p><strong>{user_comment.user_id}</strong></p>
                                        <p>{user_comment.comment}</p>
                                    </div>
                                ))}
                            </div>
                            {isAuthenticated ?
                                <div className='flex flex-row border rounded-md p-2 w-full justify-between'>
                                <Input
                                    value={comment}
                                    onChange={(e) => setComment(e.target.value)}
                                    placeholder="Write here..."
                                    className='w-full'
                                    />
                                    <Button onClick={addComment}>Send</Button>
                                </div> :
                                <></>
                            }
                        </div>
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