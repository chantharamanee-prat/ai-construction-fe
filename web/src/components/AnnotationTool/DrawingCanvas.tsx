import React, { useRef, useState, useEffect } from "react";
import { Stage, Layer, Rect, Text } from "react-konva";
import type { ImageMetadata } from "./ImageViewer";
import { CLASS_NAMES, CLASS_COLORS, type ClassId } from "./ClassSelector";

interface YoloBox {
  classId: number;
  xCenter: number; // Normalized 0-1
  yCenter: number; // Normalized 0-1
  width: number; // Normalized 0-1
  height: number; // Normalized 0-1
}

interface DrawingCanvasProps {
  boxes: YoloBox[];
  onChange: (boxes: YoloBox[]) => void;
  imageMetadata?: ImageMetadata;
  selectedClass: ClassId;
}

interface CanvasBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

const DrawingCanvas: React.FC<DrawingCanvasProps> = ({
  boxes,
  onChange,
  imageMetadata,
  selectedClass,
}) => {
  const [newBox, setNewBox] = useState<CanvasBox | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(
    null
  );
  const [hoveredBox, setHoveredBox] = useState<number | null>(null);
  const stageRef = useRef<any>(null);

  // Convert normalized YOLO coordinates to canvas coordinates
  const yoloToCanvas = (yoloBox: YoloBox): CanvasBox => {
    if (!imageMetadata) {
      return { x: 0, y: 0, width: 0, height: 0 };
    }

    const { renderedX, renderedY, renderedWidth, renderedHeight } =
      imageMetadata;

    // Convert from normalized center coordinates to canvas coordinates
    const canvasWidth = yoloBox.width * renderedWidth;
    const canvasHeight = yoloBox.height * renderedHeight;
    const canvasX =
      renderedX + yoloBox.xCenter * renderedWidth - canvasWidth / 2;
    const canvasY =
      renderedY + yoloBox.yCenter * renderedHeight - canvasHeight / 2;

    return {
      x: canvasX,
      y: canvasY,
      width: canvasWidth,
      height: canvasHeight,
    };
  };

  // Convert canvas coordinates to normalized YOLO coordinates
  const canvasToYolo = (canvasBox: CanvasBox): YoloBox | null => {
    if (!imageMetadata) return null;

    const {
      renderedX,
      renderedY,
      renderedWidth,
      renderedHeight,
      naturalWidth,
      naturalHeight,
    } = imageMetadata;

    // Ensure the box is within the image boundaries
    const imageLeft = renderedX;
    const imageTop = renderedY;
    const imageRight = renderedX + renderedWidth;
    const imageBottom = renderedY + renderedHeight;

    // Clamp box to image boundaries
    const clampedX = Math.max(imageLeft, Math.min(imageRight, canvasBox.x));
    const clampedY = Math.max(imageTop, Math.min(imageBottom, canvasBox.y));
    const clampedRight = Math.max(
      imageLeft,
      Math.min(imageRight, canvasBox.x + canvasBox.width)
    );
    const clampedBottom = Math.max(
      imageTop,
      Math.min(imageBottom, canvasBox.y + canvasBox.height)
    );

    const clampedWidth = clampedRight - clampedX;
    const clampedHeight = clampedBottom - clampedY;

    // Skip if box is too small or outside image
    if (clampedWidth < 5 || clampedHeight < 5) return null;

    // Convert to image-relative coordinates
    const imageRelativeX = clampedX - renderedX;
    const imageRelativeY = clampedY - renderedY;

    // Normalize to 0-1 range based on rendered image size
    const normalizedX = imageRelativeX / renderedWidth;
    const normalizedY = imageRelativeY / renderedHeight;
    const normalizedWidth = clampedWidth / renderedWidth;
    const normalizedHeight = clampedHeight / renderedHeight;

    // Convert to center coordinates
    const xCenter = normalizedX + normalizedWidth / 2;
    const yCenter = normalizedY + normalizedHeight / 2;

    return {
      classId: selectedClass, // Use selected class
      xCenter,
      yCenter,
      width: normalizedWidth,
      height: normalizedHeight,
    };
  };

  // Check if point is within image boundaries
  const isPointInImage = (x: number, y: number): boolean => {
    if (!imageMetadata) return false;
    const { renderedX, renderedY, renderedWidth, renderedHeight } =
      imageMetadata;
    return (
      x >= renderedX &&
      x <= renderedX + renderedWidth &&
      y >= renderedY &&
      y <= renderedY + renderedHeight
    );
  };

  const handleMouseDown = (e: any) => {
    if (isDrawing || !imageMetadata) return;

    const stage = stageRef.current;
    const point = stage.getPointerPosition();

    // Only start drawing if within image boundaries
    if (!isPointInImage(point.x, point.y)) return;

    setStartPoint({ x: point.x, y: point.y });
    setNewBox({
      x: point.x,
      y: point.y,
      width: 0,
      height: 0,
    });
    setIsDrawing(true);
  };

  const handleMouseMove = (e: any) => {
    if (!isDrawing || !newBox || !startPoint || !imageMetadata) return;

    const stage = stageRef.current;
    const point = stage.getPointerPosition();

    // Calculate box dimensions
    const width = point.x - startPoint.x;
    const height = point.y - startPoint.y;

    // Update box with proper top-left coordinates
    setNewBox({
      x: width >= 0 ? startPoint.x : point.x,
      y: height >= 0 ? startPoint.y : point.y,
      width: Math.abs(width),
      height: Math.abs(height),
    });
  };

  const handleMouseUp = () => {
    if (!isDrawing || !newBox || !imageMetadata) return;

    setIsDrawing(false);

    // Convert to YOLO format and validate
    const yoloBox = canvasToYolo(newBox);
    if (yoloBox) {
      onChange([...boxes, yoloBox]);
    }

    setNewBox(null);
    setStartPoint(null);
  };

  const handleBoxDoubleClick = (index: number) => {
    // Remove box on double click
    const newBoxes = boxes.filter((_, i) => i !== index);
    onChange(newBoxes);
  };

  const formatCoordinate = (value: number): string => {
    return value.toFixed(3);
  };

  return (
    <Stage
      width={600}
      height={400}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      ref={stageRef}
      style={{ display: "block", cursor: isDrawing ? "crosshair" : "default" }}
    >
      <Layer>
        {/* Render existing boxes */}
        {boxes.map((box, i) => {
          const canvasBox = yoloToCanvas(box);
          const classColor = CLASS_COLORS[box.classId as ClassId] || "#ff0000";
          const className = CLASS_NAMES[box.classId as ClassId] || "unknown";
          return (
            <React.Fragment key={i}>
              <Rect
                x={canvasBox.x}
                y={canvasBox.y}
                width={canvasBox.width}
                height={canvasBox.height}
                stroke={hoveredBox === i ? "#000000" : classColor}
                strokeWidth={hoveredBox === i ? 3 : 2}
                fill="transparent"
                onMouseEnter={() => setHoveredBox(i)}
                onMouseLeave={() => setHoveredBox(null)}
                onDblClick={() => handleBoxDoubleClick(i)}
              />
              {/* Show class label */}
              <Text
                x={canvasBox.x}
                y={canvasBox.y - 15}
                text={`${box.classId}: ${className}`}
                fontSize={11}
                fill={classColor}
                fontStyle="bold"
              />
              {/* Show coordinates on hover */}
              {hoveredBox === i && (
                <Text
                  x={canvasBox.x}
                  y={canvasBox.y - 35}
                  text={`Center: (${formatCoordinate(
                    box.xCenter
                  )}, ${formatCoordinate(
                    box.yCenter
                  )}) | Size: ${formatCoordinate(
                    box.width
                  )} × ${formatCoordinate(box.height)}`}
                  fontSize={10}
                  fill="#000"
                  background="#fff"
                />
              )}
            </React.Fragment>
          );
        })}

        {/* Render new box being drawn */}
        {newBox && (
          <Rect
            x={newBox.x}
            y={newBox.y}
            width={newBox.width}
            height={newBox.height}
            stroke="#0066ff"
            strokeWidth={2}
            fill="rgba(0, 102, 255, 0.1)"
            dash={[5, 5]}
          />
        )}

        {/* Instructions text */}
        <Text
          x={10}
          y={10}
          text="Draw boxes within the green dashed boundary. Double-click to delete."
          fontSize={12}
          fill="#666"
        />
      </Layer>
    </Stage>
  );
};

export default DrawingCanvas;
