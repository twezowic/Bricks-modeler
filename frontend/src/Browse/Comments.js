import { useAuth0 } from '@auth0/auth0-react';
import React, { useEffect, useState } from 'react';
import { ip } from '../utils';
import { Button, Input } from '@mui/material';

export default function Comments({selectedId}) {

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
        <div className='flex flex-col w-full h-full justify-between'>
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
    )
}