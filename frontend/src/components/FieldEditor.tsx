import React from 'react';
import { ExtractedField } from '../types';

interface Props {
  fields: ExtractedField[];
  onUpdate: (fields: ExtractedField[]) => void;
}

const FieldEditor: React.FC<Props> = ({ fields, onUpdate }) => {
  const handleChange = (index: number, newValue: string) => {
    const updated = [...fields];
    updated[index].value = newValue;
    onUpdate(updated);
  };

  return (
    <div>
      <h3>📝 Editable Extracted Fields</h3>
      {fields.filter(f => f.value?.trim()).map((field, idx) => (
        <div key={idx} style={{ marginBottom: 8 }}>
          <label>{field.field_name}</label>
          <input
            type="text"
            value={field.value ?? ''}
            onChange={(e) => handleChange(idx, e.target.value)}
            style={{ marginLeft: 10 }}
          />
        </div>
      ))}
    </div>
  );
};

export default FieldEditor;
