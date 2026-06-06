import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaChevronDown, FaChevronRight, FaBolt } from 'react-icons/fa';
import { useTactic } from '../context/TacticContext.tsx';
import { useAttack } from '../context/AttackContext.tsx';
import { tactics } from '../data/attackData.ts'; 

export const RedTeamSidebar = () => {
  const [expandedTactic, setExpandedTactic] = useState<string | null>(null);
  const { selectedTechnique, setSelectedTechnique } = useTactic();
  const { startAttack, isAttackRunning } = useAttack();
  
  const [selectedTacticName, setSelectedTacticName] = useState<string | null>(null);

  const toggleTactic = (tacticName: string) => {
    setExpandedTactic(expandedTactic === tacticName ? null : tacticName);
  };

  const handleSelectTechnique = (techniqueId: string, tacticName: string) => {
    if (selectedTechnique === techniqueId) {
      setSelectedTechnique(null);
      setSelectedTacticName(null);
    } else {
      setSelectedTechnique(techniqueId);
      setSelectedTacticName(tacticName);
    }
  };

  const handleExecuteAttack = () => {
    if (selectedTechnique && selectedTacticName && !isAttackRunning) {
      startAttack(selectedTechnique, selectedTacticName);
    }
  };

  return (
    <div className="w-80 bg-gray-900/80 backdrop-blur-sm border-r border-red-500/30 h-screen overflow-y-auto scrollbar-custom flex flex-col">
      <div className="p-6 border-b border-red-500/30 bg-red-900/20 sticky top-0 z-20">
        <h2 className="text-2xl font-bold text-red-400 tracking-wider">MITRE ATT&CK</h2>
        <p className="text-xs text-red-300/60 mt-1 tracking-wide">TACTICS & TECHNIQUES</p>
      </div>

      <div className="p-4 space-y-2 flex-1">
        {tactics.map((tactic, idx) => (
          <motion.div
            key={tactic.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="border border-red-500/20 rounded-lg overflow-hidden bg-gray-950/50"
          >
            <button
              onClick={() => toggleTactic(tactic.name)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-red-500/10 transition-colors duration-200 group"
            >
              <span className="text-sm font-semibold text-red-400 group-hover:text-red-300">
                {tactic.name}
              </span>
              {expandedTactic === tactic.name ? (
                <FaChevronDown size={18} className="text-red-400" />
              ) : (
                <FaChevronRight size={18} className="text-red-400" />
              )}
            </button>

            <AnimatePresence>
              {expandedTactic === tactic.name && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-2 pb-2 space-y-1">
                    {tactic.techniques.map((technique) => {
                      const techniqueId = `${technique.id}: ${technique.name}`;
                      const isSelected = selectedTechnique === techniqueId;

                      return (
                        <motion.button
                          key={technique.id}
                          onClick={() => handleSelectTechnique(techniqueId, tactic.name)}
                          className={`w-full text-left px-3 py-2 rounded text-xs transition-all duration-200 ${
                            isSelected
                              ? 'bg-red-500/30 text-red-200 border border-red-400/50 shadow-lg shadow-red-500/20'
                              : 'bg-gray-900/50 text-red-300/70 hover:bg-red-500/10 hover:text-red-300 border border-red-500/10'
                          }`}
                          whileHover={{ scale: 1.02, x: 2 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className="font-mono font-semibold">{technique.id}</div>
                          <div className="text-xs opacity-80 mt-0.5">{technique.name}</div>
                        </motion.button>
                      );
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

      <motion.div 
        className="p-4 border-t border-red-500/30 bg-red-900/10 sticky bottom-0 z-20"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.button
          onClick={handleExecuteAttack}
          disabled={!selectedTechnique || !selectedTacticName || isAttackRunning}
          className={`w-full py-3 rounded-lg flex items-center justify-center gap-2 font-bold transition-all duration-300 ${
            !selectedTechnique || !selectedTacticName || isAttackRunning
              ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
              : 'bg-red-600 text-white shadow-xl shadow-red-600/30 hover:bg-red-700'
          }`}
          whileHover={selectedTechnique && !isAttackRunning ? { scale: 1.02 } : {}}
          whileTap={selectedTechnique && !isAttackRunning ? { scale: 0.98 } : {}}
        >
          {isAttackRunning ? (
            'ATTACK IN PROGRESS...'
          ) : (
            <>
              <FaBolt size={20} />
              EXECUTE ATTACK
            </>
          )}
        </motion.button>
        <p className="text-xs text-red-300/50 mt-2 text-center">
            {isAttackRunning ? 'Monitoring logs...' : 'Select a technique to enable attack.'}
        </p>
      </motion.div>

      <style>{
        `.scrollbar-custom::-webkit-scrollbar {
          width: 8px;
        }
        .scrollbar-custom::-webkit-scrollbar-track {
          background: rgba(31, 41, 55, 0.5);
        }
        .scrollbar-custom::-webkit-scrollbar-thumb {
          background: rgba(239, 68, 68, 0.3);
          border-radius: 4px;
        }
        .scrollbar-custom::-webkit-scrollbar-thumb:hover {
          background: rgba(239, 68, 68, 0.5);
        }`
      }</style>
    </div>
  );
};

export default RedTeamSidebar;