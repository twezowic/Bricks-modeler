import React from 'react';

export default function Part({ imageUrl, name, onClick, isSelected }) {
  return (
    <img
      src={imageUrl}
      alt={name}
      onClick={onClick}
      className={isSelected ? 'selected' : ''}
    />
  );
}