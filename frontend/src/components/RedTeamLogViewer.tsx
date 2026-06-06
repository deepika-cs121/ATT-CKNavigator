import { motion, AnimatePresence } from 'framer-motion';
import { useAttack, Log } from '../context/AttackContext.tsx'; 
import { FaServer } from 'react-icons/fa';

// Helper to format timestamp string
const formatTimestamp = (timestamp: string | null) => {
  if (!timestamp) return 'N/A';
  // Timestamps from SQLite are full ISO strings, convert to local time
  return new Date(timestamp).toLocaleTimeString();
};

// Helper to format severity
const formatLogSeverity = (severity: Log['severity']) => {
  switch (severity) {
    case 'Critical': return 'text-red-500';
    case 'High': return 'text-orange-500';
    case 'Medium': return 'text-yellow-500';
    case 'Low': return 'text-green-500';
    default: return 'text-gray-500';
  }
};

export const RedTeamLogViewer = () => {
  const { allLogs } = useAttack();

  // Filter all logs to get just Red Team logs
  const redLogs: Log[] = allLogs.filter(log => log.type === 'RED_TEAM');

  return (
    <motion.div
      className="bg-gray-900/50 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm"
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-red-400 flex items-center gap-2">
          <FaServer />
          Red Team Operational Logs ({redLogs.length})
        </h3>
      </div>
      
      <div className="h-96 overflow-y-auto scrollbar-custom border border-gray-700 rounded-lg p-2 bg-gray-950/70">
        <AnimatePresence initial={false}>
          {redLogs.length === 0 ? (
              <motion.p 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                className="text-gray-500 text-center py-10 italic"
              >
                No operational logs. Run an attack to generate logs.
              </motion.p>
          ) : (
              <table className="min-w-full text-sm text-left text-gray-400">
                <thead className="text-xs text-red-300 uppercase bg-gray-800/80 sticky top-0">
                  <tr>
                    <th scope="col" className="px-6 py-3">Timestamp</th>
                    <th scope="col" className="px-6 py-3">Severity</th>
                    <th scope="col" className="px-6 py-3">Tactic</th>
                    <th scope="col" className="px-6 py-3">Message</th>
                  </tr>
                </thead>
                <tbody>
                  <AnimatePresence>
                    {redLogs.map((log) => (
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
                          <span className={`font-semibold ${formatLogSeverity(log.severity)}`}>
                            {log.severity.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4">{log.tactic}</td>
                        <td className="px-6 py-4 font-light">{log.message}</td>
                      </motion.tr>
                    ))}
                  </AnimatePresence>
                </tbody>
              </table>
          )}
        </AnimatePresence>
      </div>

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
    </motion.div>
  );
};

export default RedTeamLogViewer;