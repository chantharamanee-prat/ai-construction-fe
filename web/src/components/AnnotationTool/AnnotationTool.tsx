import React, { useEffect, useState } from 'react';
import { fetchImages, saveAnnotation, type Annotation } from '../../api/annotationService';
import ImageViewer from './ImageViewer';
import DrawingCanvas from './DrawingCanvas';
import ProgressForm from './ProgressForm';

const AnnotationTool: React.FC = () => {
  const [images, setImages] = useState<string[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [annotation, setAnnotation] = useState<Annotation | null>(null);

  useEffect(() => {
    async function loadImages() {
      try {
        const imgs = await fetchImages();
        setImages(imgs);
        if (imgs.length > 0) {
          setCurrentImageIndex(0);
          setAnnotation({
            imageName: imgs[0],
            progress: 0,
            boxes: [],
          });
        } else {
          alert('No images found');
        }
      } catch (error) {
        alert('Failed to load images: ' + (error instanceof Error ? error.message : String(error)));
      }
    }
    loadImages();
  }, []);

  const handleBoxChange = (boxes: Annotation['boxes']) => {
    if (annotation) {
      setAnnotation({ ...annotation, boxes });
    }
  };

  const handleProgressChange = (progress: number) => {
    if (annotation) {
      setAnnotation({ ...annotation, progress });
    }
  };

  const handleSave = async () => {
    if (annotation) {
      try {
        await saveAnnotation(annotation);
        alert('Annotation saved successfully');
      } catch (error) {
        alert('Failed to save annotation: ' + (error instanceof Error ? error.message : String(error)));
      }
    }
  };

  const handleNextImage = () => {
    if (currentImageIndex < images.length - 1) {
      const nextIndex = currentImageIndex + 1;
      setCurrentImageIndex(nextIndex);
      setAnnotation({
        imageName: images[nextIndex],
        progress: 0,
        boxes: [],
      });
    }
  };

  if (images.length === 0) {
    return <div>Loading images...</div>;
  }

  return (
    <div>
      <h2>Annotation Tool</h2>
      <div>
        <ImageViewer imagePath={images[currentImageIndex]} />
        <DrawingCanvas boxes={annotation?.boxes || []} onChange={handleBoxChange} />
        <ProgressForm progress={annotation?.progress || 0} onChange={handleProgressChange} />
      </div>
      <button onClick={handleSave}>Save Annotation</button>
      <button onClick={handleNextImage} disabled={currentImageIndex >= images.length - 1}>
        Next Image
      </button>
    </div>
  );
};

export default AnnotationTool;
