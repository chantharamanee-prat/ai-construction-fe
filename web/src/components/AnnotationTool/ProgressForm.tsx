import React from 'react';

interface ProgressFormProps {
  progress: number;
  onChange: (progress: number) => void;
}

const ProgressForm: React.FC<ProgressFormProps> = ({ progress, onChange }) => {
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Math.min(100, Math.max(0, Number(e.target.value)));
    onChange(value);
  };

  return (
    <div style={{ marginTop: '10px' }}>
      <label htmlFor="progress">Progress (%): </label>
      <input
        id="progress"
        type="number"
        min={0}
        max={100}
        value={progress}
        onChange={handleInputChange}
      />
    </div>
  );
};

export default ProgressForm;
