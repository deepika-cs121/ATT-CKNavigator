import { motion, AnimatePresence } from 'framer-motion';
import { HomeButton } from '../components/HomeButton.tsx';
import { AnimatedBackground } from '../components/AnimatedBackground.tsx';
import { SeverityChart } from '../components/SeverityChart.tsx';
import { useAttack, Log } from '../context/AttackContext.tsx';
import { FaShieldAlt, FaServer } from 'react-icons/fa';
import { RedTeamLogViewer } from '../components/RedTeamLogViewer.tsx';

export const BlueTeam = () => {
  const { isAttackRunning, allLogs } = useAttack();

  // Filter all logs to get just Blue Team logs
  const logsToDisplay: Log[] = allLogs.filter(log => log.type === 'BLUE_TEAM');

  const formatLogSeverity = (severity: Log['severity']) => {
    switch (severity) {
      case 'Critical': return 'text-red-400 bg-red-900/30'; // Kept red for critical, but lighter
      case 'High': return 'text-orange-400 bg-orange-900/30'; // Kept orange for high
      case 'Medium': return 'text-yellow-400 bg-yellow-900/30'; // Kept yellow for medium
      case 'Low': return 'text-sky-400 bg-sky-900/30'; // Changed to blue for low
      default: return 'text-gray-400 bg-gray-700/30';
    }
  };

  // Helper to format timestamp string
  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return 'N/A';
    // Timestamps from SQLite are full ISO strings, convert to local time
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-hidden relative">
      <AnimatedBackground />
      <HomeButton />

      <div className="relative z-10 p-8 pt-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-blue-400 mb-2 tracking-wider">
              BLUE TEAM DASHBOARD
            </h1>
            <p className="text-blue-300/60 text-sm tracking-wide">
              Cyber Defense and Monitoring
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <motion.div
              className="bg-gray-900/50 border border-blue-500/30 rounded-xl p-6 backdrop-blur-sm lg:col-span-1"
              whileHover={{ borderColor: 'rgba(96, 165, 250, 0.5)' }} 
            >
              <div className="flex items-center gap-3 mb-4">
                <FaShieldAlt className="text-blue-400" size={24} />
                <h3 className="text-xl font-semibold text-blue-400">Live Attack Status</h3>
              </div>
              <div className="space-y-2 text-sm">
                <p className={`text-2xl font-mono font-bold ${isAttackRunning ? 'text-red-500 animate-pulse' : 'text-blue-400'}`}>
                  {isAttackRunning ? '🚨 ACTIVE THREAT' : '✅ ALL CLEAR'}
                </p>
                <p className="text-gray-400">
                  Last Log Time: <span className="font-mono text-blue-300">{formatTimestamp(logsToDisplay[0]?.timestamp)}</span>
                </p>
                <p className="text-gray-400">
                  Total Logs: <span className="font-mono text-blue-300">{logsToDisplay.length}</span>
                </p>
              </div>
            </motion.div>

            <motion.div
              className="bg-gray-900/50 border border-blue-500/30 rounded-xl p-6 backdrop-blur-sm lg:col-span-2"
              whileHover={{ borderColor: 'rgba(96, 165, 250, 0.5)' }} 
            >
              <h3 className="text-xl font-semibold text-blue-400 mb-4">Live Log Severity Distribution</h3>
              <SeverityChart findings={logsToDisplay} />
            </motion.div>

          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* --- BLUE TEAM LOGS (LEFT) --- */}
            <motion.div
              className="bg-gray-900/50 border border-blue-500/30 rounded-xl p-6 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-blue-400 flex items-center gap-2">
                  <FaServer />
                  Blue Team: Security Event Logs ({logsToDisplay.length})
                </h3>
              </div>

              <div className="h-96 overflow-y-auto scrollbar-custom-blue border border-gray-700 rounded-lg p-2 bg-gray-950/70">
                <AnimatePresence initial={false}>
                  {logsToDisplay.length === 0 ? (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-gray-500 text-center py-10 italic"
                    >
                      {isAttackRunning ? "Monitoring for defensive alerts..." : "No attack logs visible. Run a technique from the Red Team dashboard."}
                    </motion.p>
                  ) : (
                    <table className="min-w-full text-sm text-left text-gray-400">
                      <thead className="text-xs text-blue-300 uppercase bg-gray-800/80 sticky top-0">
                        <tr>
                          <th scope="col" className="px-6 py-3">Timestamp</th>
                          <th scope="col" className="px-6 py-3">Severity</th>
                          <th scope="col" className="px-6 py-3">Tactic</th>
                          <th scope="col" className="px-6 py-3">Technique ID</th>
                          <th scope="col" className="px-6 py-3">Message</th>
                        </tr>
                      </thead>
                      <tbody>
                        <AnimatePresence>
                          {logsToDisplay.map((log) => (
                            <motion.tr
                              key={log.id}
                              layout
                              initial={{ opacity: 0, y: -20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, x: 20 }}
                              transition={{ duration: 0.3 }}
                              className="border-b border-gray-700 hover:bg-gray-800/50"
                            >
                              <td className="px-6 py-4 font-mono text-xs">{formatTimestamp(log.timestamp)}</td>
                              <td className="px-6 py-4">
                                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${formatLogSeverity(log.severity)}`}>
                                  {log.severity.toUpperCase()}
                                </span>
                              </td>
                              <td className="px-6 py-4">{log.tactic}</td>
                              <td className="px-6 py-4 font-mono text-xs text-blue-300">{log.techniqueId}</td>
                              <td className="px-6 py-4 font-light">{log.message}</td>
                            </motion.tr>
                          ))}
                        </AnimatePresence>
                      </tbody>
                    </table>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>

            {/* --- RED TEAM LOGS (RIGHT) --- */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <RedTeamLogViewer />
            </motion.div>

          </div>

        </motion.div>
      </div>

      <style>{
        `.scrollbar-custom-blue::-webkit-scrollbar {
          width: 8px;
        }
        .scrollbar-custom-blue::-webkit-scrollbar-track {
          background: rgba(31, 41, 55, 0.5); /* Gray-800 with transparency */
        }
        .scrollbar-custom-blue::-webkit-scrollbar-thumb {
          background: rgba(96, 165, 250, 0.3); /* blue-400 with transparency */
          border-radius: 4px;
        }
        .scrollbar-custom-blue::-webkit-scrollbar-thumb:hover {
          background: rgba(96, 165, 250, 0.5); /* blue-400 with more transparency on hover */
        }`
      }</style>
    </div>
  );
};

export default BlueTeam;