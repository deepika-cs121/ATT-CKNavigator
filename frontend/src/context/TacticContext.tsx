import { createContext, useContext, useState, ReactNode } from 'react';

interface TacticContextType {
  selectedTechnique: string | null;
  setSelectedTechnique: (technique: string | null) => void;
}

const TacticContext = createContext<TacticContextType | undefined>(undefined);

export const TacticProvider = ({ children }: { children: ReactNode }) => {
  const [selectedTechnique, setSelectedTechnique] = useState<string | null>(null);

  return (
    <TacticContext.Provider value={{ selectedTechnique, setSelectedTechnique }}>
      {children}
    </TacticContext.Provider>
  );
};

export const useTactic = () => {
  const context = useContext(TacticContext);
  if (!context) {
    throw new Error('useTactic must be used within TacticProvider');
  }
  return context;
};