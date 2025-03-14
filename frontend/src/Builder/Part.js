import React from 'react';

export default function Part({ imageUrl, name, draggable, onDragStart, color, count }) {
  return (
    <div className="flex flex-row gap-2 h-[90px] p-2 justify-center">
      <img
        src={`data:image/png;base64,${imageUrl}`}
        alt={`Model-${name}`}
        draggable={draggable}
        onDragStart={onDragStart}
        className="max-w-[100px] h-[90px]"
      />
      {count && color && (
        <div className="flex flex-col gap-2 w-full h-full">
          <span>
            x {count}
          </span>
          <div
            className="h-10 w-10 rounded-full border border-black"
            style={{ backgroundColor: color }}
          ></div>
        </div>
      )}
    </div>
  );
}
