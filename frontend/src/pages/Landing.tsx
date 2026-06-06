import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { FaShieldAlt, FaBullseye } from 'react-icons/fa';
import { AnimatedBackground } from '../components/AnimatedBackground.tsx';

export const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-hidden relative">
      <AnimatedBackground />

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <motion.h1
            className="text-7xl md:text-8xl font-black mb-4 tracking-wider"
            style={{
              fontFamily: 'monospace',
              textShadow: '0 0 20px rgba(34, 197, 94, 0.8), 0 0 40px rgba(34, 197, 94, 0.4)',
              color: '#22c55e',
            }}
            animate={{
              textShadow: [
                '0 0 20px rgba(34, 197, 94, 0.8), 0 0 40px rgba(34, 197, 94, 0.4)',
                '0 0 30px rgba(34, 197, 94, 1), 0 0 60px rgba(34, 197, 94, 0.6)',
                '0 0 20px rgba(34, 197, 94, 0.8), 0 0 40px rgba(34, 197, 94, 0.4)',
              ],
            }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          >
            ATT&CK NAVIGATOR
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl text-green-400/80 font-light tracking-widest"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            Advanced Threat Tactics & Combat Knowledge Navigator
          </motion.p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="flex items-center gap-3 mb-16 px-6 py-3 bg-gray-900/50 border border-green-500/30 rounded-full backdrop-blur-sm"
        >
          <motion.div
            className="w-3 h-3 bg-green-400 rounded-full"
            animate={{
              scale: [1, 1.3, 1],
              opacity: [1, 0.5, 1],
              boxShadow: [
                '0 0 5px rgba(34, 197, 94, 0.8)',
                '0 0 15px rgba(34, 197, 94, 1)',
                '0 0 5px rgba(34, 197, 94, 0.8)',
              ],
            }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <span className="text-green-400 font-mono text-sm tracking-wider">SYSTEM ONLINE</span>
        </motion.div>

        <div className="flex flex-col md:flex-row gap-8 items-center">
          <motion.button
            onClick={() => navigate('/red-team')} 
            className="group relative px-12 py-6 bg-gradient-to-br from-red-900/40 to-red-950/20 border-2 border-red-500/50 rounded-xl overflow-hidden hover:border-red-400 transition-all duration-300 min-w-[280px]"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(239, 68, 68, 0.5)' }}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-red-500/0 via-red-500/20 to-red-500/0"
              animate={{ x: ['-100%', '200%'] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            />
            <div className="relative flex items-center justify-center gap-3">
              <FaBullseye className="text-red-400" size={28} />
              <div className="text-left">
                <div className="text-2xl font-bold text-red-400 tracking-wider">RED TEAM</div>
                <div className="text-xs text-red-300/70 tracking-wide">OFFENSIVE OPS</div>
              </div>
            </div>
          </motion.button>

          <motion.button
            onClick={() => navigate('/blue-team')}
            className="group relative px-12 py-6 bg-gradient-to-br from-blue-900/40 to-blue-950/20 border-2 border-blue-500/50 rounded-xl overflow-hidden hover:border-blue-400 transition-all duration-300 min-w-[280px]"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(59, 130, 246, 0.5)' }}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/20 to-blue-500/0"
              animate={{ x: ['-100%', '200%'] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear', delay: 1 }}
            />
            <div className="relative flex items-center justify-center gap-3">
              <FaShieldAlt className="text-blue-400" size={28} />
              <div className="text-left">
                <div className="text-2xl font-bold text-blue-400 tracking-wider">BLUE TEAM</div>
                <div className="text-xs text-blue-300/70 tracking-wide">DEFENSIVE OPS</div>
              </div>
            </div>
          </motion.button>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-16 text-center text-gray-500 text-sm font-mono"
        >
          <p>PURPLE TEAM LAB ENVIRONMENT</p>
        </motion.div>
      </div>
    </div>
  );
};

export default Landing;