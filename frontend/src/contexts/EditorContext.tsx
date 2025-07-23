import React from 'react';
import { EditorElement, Scene } from '../types/editor';

interface EditorContextValue {
  scene: Scene | null;
  selectedElement: EditorElement | null;
  history: {
    canUndo: boolean;
    canRedo: boolean;
  };
  tools: {
    activeTool: string;
  };
  zoom: {
    scale: number;
  };
  readOnly: boolean;
}

export const EditorContext = React.createContext<EditorContextValue>({
  scene: null,
  selectedElement: null,
  history: {
    canUndo: false,
    canRedo: false,
  },
  tools: {
    activeTool: 'select',
  },
  zoom: {
    scale: 1,
  },
  readOnly: false,
});

interface EditorProviderProps {
  children: React.ReactNode;
  value: EditorContextValue;
}

export const EditorProvider: React.FC<EditorProviderProps> = ({
  children,
  value,
}) => {
  return (
    <EditorContext.Provider value={value}>{children}</EditorContext.Provider>
  );
};

export const useEditorContext = () => {
  const context = React.useContext(EditorContext);
  if (!context) {
    throw new Error('useEditorContext must be used within an EditorProvider');
  }
  return context;
};
