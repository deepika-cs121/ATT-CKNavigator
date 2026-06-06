import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
// This import is now correct and points to the local frontend file
import { AttackScenario, AttackStep, scenarios, getDefaultScenario } from '../data/attackScenarios';
import toast from 'react-hot-toast';
import { io, Socket } from 'socket.io-client';

// This is the frontend-only log type.
// The backend will send us logs that match this structure.
export interface Log {
  id: number;
  timestamp: string; // SQLite sends timestamps as strings
  techniqueId: string;
  tactic: string;
  message: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  type: 'RED_TEAM' | 'BLUE_TEAM';
}

interface AttackContextType {
  isAttackRunning: boolean;
  startAttack: (technique: string, tactic: string) => void;
  currentScenario: AttackScenario | null; 
  currentStep: AttackStep | null;
  allLogs: Log[]; // Provide all logs to any component
}

const AttackContext = createContext<AttackContextType | undefined>(undefined);

// Connect to the backend server
const socket: Socket = io("http://localhost:3001");

export const AttackProvider = ({ children }: { children: ReactNode }) => {
  const [isAttackRunning, setIsAttackRunning] = useState(false);
  const [currentScenario, setCurrentScenario] = useState<AttackScenario | null>(null);
  const [currentStep, setCurrentStep] = useState<AttackStep | null>(null);
  const [allLogs, setAllLogs] = useState<Log[]>([]);
  
  useEffect(() => {
    // Fetch all historical logs from the API on page load
    fetch("http://localhost:3001/logs")
      .then(res => res.json())
      .then((data: Log[]) => {
        setAllLogs(data);
      })
      .catch(err => console.error("Failed to load logs:", err));

    // Set up all WebSocket listeners
    socket.on('connect', () => {
      console.log('Connected to backend socket server');
    });

    socket.on('attack_started', () => {
      setIsAttackRunning(true);
    });
    
    socket.on('step_update', (step: AttackStep) => {
      setCurrentStep(step);
    });
    
    // Listen for new logs pushed by the server
    socket.on('new_log', (newLog: Log) => {
      setAllLogs(prevLogs => [newLog, ...prevLogs]);
    });

    socket.on('attack_complete', (data: { message: string }) => {
      setIsAttackRunning(false);
      setCurrentStep(null);
      toast.success(data.message);
    });
    
    socket.on('attack_error', (data: { message: string }) => {
      toast.error(data.message);
    });

    // Clean up listeners on unmount
    return () => {
      socket.off('connect');
      socket.off('attack_started');
      socket.off('step_update');
      socket.off('new_log');
      socket.off('attack_complete');
      socket.off('attack_error');
    };
  }, []);

  // This function just sends a message to the backend
  const startAttack = (technique: string, tactic: string) => {
    if (!isAttackRunning) {
      setCurrentStep(null);
      
      // Find the scenario locally to set the nodes *immediately*
      const scenario = scenarios[tactic] || getDefaultScenario(tactic);
      setCurrentScenario(scenario); 
      
      // Tell the backend to start the attack
      socket.emit('start_attack', { technique, tactic });
    }
  };

  return (
    <AttackContext.Provider value={{ isAttackRunning, startAttack, currentScenario, currentStep, allLogs }}>
      {children}
    </AttackContext.Provider>
  );
};

export const useAttack = () => {
  const context = useContext(AttackContext);
  if (!context) {
    throw new Error('useAttack must be used within AttackProvider');
  }
  return context;
};