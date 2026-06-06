import { motion } from 'framer-motion';
import { HomeButton } from '../components/HomeButton.tsx';
import { RedTeamSidebar } from '../components/RedTeamSidebar.tsx';
import { AnimatedBackground } from '../components/AnimatedBackground.tsx';
import { AttackSimulation } from '../components/AttackSimulation.tsx';
import { useTactic } from '../context/TacticContext.tsx';
import { useAttack } from '../context/AttackContext.tsx';
import { FaExclamationTriangle } from 'react-icons/fa';
import { RedTeamLogViewer } from '../components/RedTeamLogViewer.tsx'; 

export const RedTeam = () => {
  const { selectedTechnique } = useTactic();
  const { isAttackRunning } = useAttack();

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-hidden relative">
      <AnimatedBackground />
      <HomeButton />

      <div className="relative z-10 flex h-screen">
        <RedTeamSidebar />

        <div className="flex-1 p-8 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-red-400 mb-2 tracking-wider">
                RED TEAM DASHBOARD
              </h1>
              <p className="text-red-300/60 text-sm tracking-wide">
                Offensive Security Operations
              </p>
            </div>
            
            <motion.div 
              className="mb-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <h3 className="text-2xl font-semibold text-red-300 mb-4 flex items-center gap-2">
                <FaExclamationTriangle className="text-red-500" />
                Attack Simulation
                {isAttackRunning && <span className="text-sm font-mono text-red-500 bg-red-900/30 p-1 rounded">ACTIVE</span>}
              </h3>
              <AttackSimulation />
              <p className="text-xs text-gray-500 mt-2 text-right">Simulation of attack flow and nodes.</p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <motion.div
                className="bg-gray-900/50 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm"
                whileHover={{ borderColor: 'rgba(239, 68, 68, 0.5)' }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <FaExclamationTriangle className="text-red-400" size={24} />
                  <h3 className="text-xl font-semibold text-red-400">Mission Status</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Tactics:</span>
                    <span className="text-red-300 font-mono">14</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Techniques:</span>
                    <span className="text-red-300 font-mono">42</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Active Selection:</span>
                    <span className="text-red-300 font-mono">
                      {selectedTechnique ? '1' : '0'}
                    </span>
                  </div>
                </div>
              </motion.div>

              <motion.div
                className="bg-gray-900/50 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm"
                whileHover={{ borderColor: 'rgba(239, 68, 68, 0.5)' }}
              >
                <h3 className="text-xl font-semibold text-red-400 mb-4">Selected Technique</h3>
                {selectedTechnique ? (
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <p className="text-red-300 font-mono text-sm">{selectedTechnique}</p>
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm italic">
                    Select a technique from the sidebar to view details
                  </p>
                )}
              </motion.div>
            </div>

            <motion.div
              className="bg-gray-900/50 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <h3 className="text-xl font-semibold text-red-400 mb-4">Operational Notes</h3>
              <div className="space-y-3 text-sm text-gray-400">
                <p>
                  • Select techniques from the sidebar to analyze attack vectors
                </p>
                <p>
                  • Selected techniques will automatically filter Blue Team defensive measures
                </p>
                <p>
                  • Use this dashboard to plan offensive security assessments
                </p>
                <p>
                  • All activities should be conducted within authorized scope
                </p>
              </div>
            </motion.div>

            <motion.div
              className="mt-6 mb-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <RedTeamLogViewer />
            </motion.div>

          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default RedTeam;