import React from 'react';

export default function Part({ imageUrl, name, draggable, onDragStart }) {
  return (
    <img
      src={imageUrl}
      alt={name}
      draggable={draggable} // Dodaj atrybut draggable
      onDragStart={onDragStart} // Dodaj obsługę przeciągania
    />
  );
}
