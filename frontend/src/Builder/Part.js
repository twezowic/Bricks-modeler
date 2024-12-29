import React, { useState } from 'react';

export default function Part({ imageUrl, name, draggable, onDragStart, color, count }) {
  const [currentCount, setCurrentCount] = useState(count);

  const handleDragEnd = () => {
    if (currentCount > 0) {
      setCurrentCount((prevCount) => prevCount - 1);
    }
  };

  return (
    <div className="flex flex-row gap-2 h-[90px] p-2 justify-center">
      <img
        src={`data:image/png;base64,${imageUrl}`}
        alt={`Model-${name}`}
        draggable={draggable}
        onDragStart={onDragStart}
        onDragEnd={handleDragEnd}
        className="max-w-[100px] h-[90px]"
      />
      {count && color && (
        <div className="flex flex-col gap-2 w-full h-full">
          <span>
            Count: {currentCount} / {count}
          </span>
          <div
            className="h-10 w-10 rounded-full"
            style={{ backgroundColor: color }}
          ></div>
        </div>
      )}
    </div>
  );
}
