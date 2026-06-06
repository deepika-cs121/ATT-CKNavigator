import { motion, AnimatePresence } from 'framer-motion';
import { useAttack } from '../context/AttackContext.tsx';
import React, { useMemo } from 'react';
import { 
  FaShieldAlt, 
  FaBolt, 
  FaServer, 
  FaWifi, 
  FaEnvelope, 
  FaDatabase 
} from 'react-icons/fa';
import { LuBrickWall } from 'react-icons/lu';
import { HackerIcon } from './HackerIcon';

// Helper to get the right icon
const getNodeIcon = (type: string) => {
  if (type.includes('Workstation') || type.includes('Target')) return <FaServer size={32} className="text-white" />;
  if (type.includes('Attacker') || type.includes('Red')) return <FaBolt size={32} className="text-white" />;
  if (type.includes('Blue') || type.includes('Defense')) return <FaShieldAlt size={32} className="text-white" />;
  if (type.includes('Gateway')) return <FaWifi size={32} className="text-white" />;
  if (type.includes('WAF') || type.includes('Firewall')) return <LuBrickWall size={32} className="text-white" />;
  if (type.includes('Email')) return <FaEnvelope size={32} className="text-white" />;
  if (type.includes('Database') || type.includes('DB')) return <FaDatabase size={32} className="text-white" />;
  return <FaServer size={32} className="text-white" />;
};

// Helper to get node colors
const getNodeColor = (type: 'red' | 'blue' | 'neutral') => {
  switch (type) {
    case 'red':
      return 'bg-red-600/50 border-red-400 shadow-red-500/30';
    case 'blue':
      return 'bg-blue-600/50 border-blue-400 shadow-blue-500/30';
    case 'neutral':
      return 'bg-gray-600/50 border-gray-400 shadow-gray-500/30';
  }
};

export const AttackSimulation = () => {
  const { currentScenario, currentStep, isAttackRunning } = useAttack();

  const nodePositions = useMemo(() => {
    if (!currentScenario) return new Map<string, { x: number; y: number }>();
    
    const positions = new Map<string, { x: number; y: number }>();
    const count = currentScenario.nodes.length;
    const height = 300; 
    const width = 800; 
    const radius = Math.min(width / 3, height / 2.5);
    const centerX = width / 2.5;
    const centerY = height / 2;

    currentScenario.nodes.forEach((node, i) => {
      const angle = (i / count) * 2 * Math.PI - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      positions.set(node.id, { x, y });
    });
    return positions;
  }, [currentScenario]);

  if (!isAttackRunning || !currentScenario) {
    return (
      <div className="relative w-full h-96 border border-red-500/30 rounded-xl bg-gray-900/50 p-6 flex items-center justify-center">
        <p className="text-gray-600 text-lg">Select a technique and click "Execute Attack" to begin simulation.</p>
      </div>
    );
  }

  const { nodes } = currentScenario;
  const fromPos = currentStep ? nodePositions.get(currentStep.visual.from) : null;
  const toPos = currentStep ? nodePositions.get(currentStep.visual.to) : null;

  return (
    <div className="relative w-full h-96 border border-red-500/30 rounded-xl bg-gray-900/50 p-6 overflow-hidden">
      
      <AnimatePresence>
        {isAttackRunning && <HackerIcon />}
      </AnimatePresence>

      {/* Render Nodes */}
      {nodes.map((node) => {
        const pos = nodePositions.get(node.id);
        if (!pos) return null;
        
        const isActive = currentStep && (currentStep.visual.from === node.id || currentStep.visual.to === node.id);

        return (
          <motion.div
            key={node.id}
            className="absolute flex flex-col items-center z-10"
            initial={{ x: pos.x, y: pos.y }}
            animate={{ x: pos.x, y: pos.y }}
          >
            <motion.div
              className={`p-4 rounded-full border-4 shadow-xl ${getNodeColor(node.type)}`}
              animate={{ scale: isActive ? 1.1 : 1 }}
              transition={{ duration: 0.3 }}
            >
              {getNodeIcon(node.name)}
            </motion.div>
            <p className={`mt-2 text-sm font-bold ${
              node.type === 'red' ? 'text-red-400' : node.type === 'blue' ? 'text-blue-400' : 'text-gray-400'
            }`}>
              {node.name}
            </p>
          </motion.div>
        );
      })}

      {/* Render Animated Packet */}
      <svg className="absolute w-full h-full left-0 top-0 pointer-events-none z-20">
        <AnimatePresence>
          {isAttackRunning && currentStep && fromPos && toPos && (
            <motion.path
              key={currentStep.step} // Re-triggers animation on step change
              d={`M ${fromPos.x + 32} ${fromPos.y + 32} L ${toPos.x + 32} ${toPos.y + 32}`}
              stroke="none"
              fill="none"
            >
              <motion.circle
                cx="0"
                cy="0"
                r={8} // Fixed the 'r' attribute error
                fill="#ef4444"
                initial={{ pathOffset: 0, opacity: 1 }}
                animate={{ pathOffset: 1, opacity: 1 }}
                transition={{ duration: 2, ease: "linear" }}
              />
            </motion.path>
          )}
        </AnimatePresence>
      </svg>
      
      {/* Display Current Action */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep?.step || 'idle'}
          className="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 bg-red-900/50 border border-red-500/50 text-red-300 px-4 py-2 rounded-lg text-sm font-mono"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          {currentStep?.visual.action || 'Initializing...'}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default AttackSimulation;