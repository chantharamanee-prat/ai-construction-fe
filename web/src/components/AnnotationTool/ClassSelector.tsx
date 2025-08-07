import React from "react";

export type ClassId = 0 | 1 | 2 | 3 | 4 | 5;

export const CLASS_NAMES: Record<ClassId, string> = {
  0: "foundation",
  1: "column",
  2: "beam",
  3: "roof",
  4: "wall",
  5: "floor",
};

export const CLASS_COLORS: Record<ClassId, string> = {
  0: "#8B4513", // Brown for foundation
  1: "#FF6B6B", // Red for column
  2: "#4ECDC4", // Teal for beam
  3: "#45B7D1", // Blue for roof
  4: "#96CEB4", // Green for wall
  5: "#FFEAA7", // Yellow for floor
};

interface ClassSelectorProps {
  selectedClass: ClassId;
  onChange: (classId: ClassId) => void;
}

const ClassSelector: React.FC<ClassSelectorProps> = ({
  selectedClass,
  onChange,
}) => {
  return (
    <div style={{ marginBottom: "10px" }}>
      <h4>Select Class:</h4>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {Object.entries(CLASS_NAMES).map(([id, name]) => {
          const classId = parseInt(id) as ClassId;
          const isSelected = selectedClass === classId;
          return (
            <button
              key={classId}
              onClick={() => onChange(classId)}
              style={{
                padding: "8px 12px",
                border: isSelected ? "3px solid #000" : "1px solid #ccc",
                backgroundColor: isSelected ? CLASS_COLORS[classId] : "#fff",
                color: isSelected ? "#fff" : "#000",
                borderRadius: "4px",
                cursor: "pointer",
                fontWeight: isSelected ? "bold" : "normal",
                fontSize: "12px",
              }}
            >
              {classId}: {name}
            </button>
          );
        })}
      </div>
      <p style={{ fontSize: "12px", color: "#666", marginTop: "5px" }}>
        Selected: Class {selectedClass} ({CLASS_NAMES[selectedClass]})
      </p>
    </div>
  );
};

export default ClassSelector;
