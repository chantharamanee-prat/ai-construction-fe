import React from 'react';

interface ImageViewerProps {
  imagePath: string;
}

const ImageViewer: React.FC<ImageViewerProps> = ({ imagePath }) => {
  return (
    <div style={{ border: '1px solid #ccc', marginBottom: '10px' }}>
      <img
        src={`/datasets/construction_raw_images/${imagePath}`}
        alt="Construction site"
        style={{ maxWidth: '100%', maxHeight: '400px' }}
      />
    </div>
  );
};

export default ImageViewer;
