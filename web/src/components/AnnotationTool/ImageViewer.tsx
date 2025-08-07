import React, { useRef, useEffect, useState } from "react";
import { VITE_BASE_API } from "../../api/annotationService";

export interface ImageMetadata {
  naturalWidth: number;
  naturalHeight: number;
  renderedX: number;
  renderedY: number;
  renderedWidth: number;
  renderedHeight: number;
  containerWidth: number;
  containerHeight: number;
}

interface ImageViewerProps {
  imagePath: string;
  onImageLoad?: (metadata: ImageMetadata) => void;
}

const ImageViewer: React.FC<ImageViewerProps> = ({
  imagePath,
  onImageLoad,
}) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [imageMetadata, setImageMetadata] = useState<ImageMetadata | null>(
    null
  );

  const calculateImageMetadata = () => {
    if (!imgRef.current || !containerRef.current) return;

    const img = imgRef.current;
    const container = containerRef.current;

    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const naturalWidth = img.naturalWidth;
    const naturalHeight = img.naturalHeight;

    // Calculate the rendered size maintaining aspect ratio (objectFit: contain)
    const containerAspect = containerWidth / containerHeight;
    const imageAspect = naturalWidth / naturalHeight;

    let renderedWidth: number;
    let renderedHeight: number;
    let renderedX: number;
    let renderedY: number;

    if (imageAspect > containerAspect) {
      // Image is wider - fit to width
      renderedWidth = containerWidth;
      renderedHeight = containerWidth / imageAspect;
      renderedX = 0;
      renderedY = (containerHeight - renderedHeight) / 2;
    } else {
      // Image is taller - fit to height
      renderedHeight = containerHeight;
      renderedWidth = containerHeight * imageAspect;
      renderedX = (containerWidth - renderedWidth) / 2;
      renderedY = 0;
    }

    const metadata: ImageMetadata = {
      naturalWidth,
      naturalHeight,
      renderedX,
      renderedY,
      renderedWidth,
      renderedHeight,
      containerWidth,
      containerHeight,
    };

    setImageMetadata(metadata);
    onImageLoad?.(metadata);
  };

  useEffect(() => {
    calculateImageMetadata();
  }, [imagePath]);

  const handleImageLoad = () => {
    calculateImageMetadata();
  };

  const handleResize = () => {
    calculateImageMetadata();
  };

  useEffect(() => {
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: "600px",
        height: "400px",
        border: "1px solid #ccc",
        marginBottom: "10px",
        overflow: "hidden",
        position: "relative",
      }}
    >
      <img
        ref={imgRef}
        src={`${VITE_BASE_API}/images${imagePath}`}
        alt="Construction site"
        style={{ width: "100%", height: "100%", objectFit: "contain" }}
        onLoad={handleImageLoad}
      />
      {/* Visual indicator for image boundaries */}
      {imageMetadata && (
        <div
          style={{
            position: "absolute",
            left: imageMetadata.renderedX,
            top: imageMetadata.renderedY,
            width: imageMetadata.renderedWidth,
            height: imageMetadata.renderedHeight,
            border: "1px dashed rgba(0, 255, 0, 0.5)",
            pointerEvents: "none",
            zIndex: 5,
          }}
        />
      )}
    </div>
  );
};

export default ImageViewer;
