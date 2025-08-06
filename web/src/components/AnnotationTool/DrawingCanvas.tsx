import React, { useRef, useState, useEffect } from 'react';
import { Stage, Layer, Rect } from 'react-konva';

interface Box {
  classId: number;
  xCenter: number;
  yCenter: number;
  width: number;
  height: number;
}

interface DrawingCanvasProps {
  boxes: Box[];
  onChange: (boxes: Box[]) => void;
}

const DrawingCanvas: React.FC<DrawingCanvasProps> = ({ boxes, onChange }) => {
  const [newBox, setNewBox] = useState<Box | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const stageRef = useRef<any>(null);

  const handleMouseDown = (e: any) => {
    if (isDrawing) return;
    const stage = stageRef.current;
    const point = stage.getPointerPosition();
    setNewBox({
      classId: 0,
      xCenter: point.x,
      yCenter: point.y,
      width: 0,
      height: 0,
    });
    setIsDrawing(true);
  };

  const handleMouseMove = (e: any) => {
    if (!isDrawing || !newBox) return;
    const stage = stageRef.current;
    const point = stage.getPointerPosition();
    const width = point.x - newBox.xCenter;
    const height = point.y - newBox.yCenter;
    setNewBox({
      ...newBox,
      width,
      height,
    });
  };

  const handleMouseUp = () => {
    if (!isDrawing || !newBox) return;
    setIsDrawing(false);
    if (Math.abs(newBox.width) > 5 && Math.abs(newBox.height) > 5) {
      onChange([...boxes, newBox]);
    }
    setNewBox(null);
  };

  return (
    <div style={{ border: '1px solid #ccc', marginBottom: '10px' }}>
      <Stage
        width={600}
        height={400}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        ref={stageRef}
      >
        <Layer>
          {boxes.map((box, i) => (
            <Rect
              key={i}
              x={box.xCenter}
              y={box.yCenter}
              width={box.width}
              height={box.height}
              stroke="red"
            />
          ))}
          {newBox && (
            <Rect
              x={newBox.xCenter}
              y={newBox.yCenter}
              width={newBox.width}
              height={newBox.height}
              stroke="blue"
            />
          )}
        </Layer>
      </Stage>
    </div>
  );
};

export default DrawingCanvas;
