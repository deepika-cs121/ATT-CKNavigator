import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaHome } from 'react-icons/fa';

export const HomeButton = () => {
  const navigate = useNavigate();

  return (
    <motion.button
      onClick={() => navigate('/')}
      className="fixed top-6 right-6 z-50 px-4 py-2 bg-gray-900 border border-green-500/50 rounded-lg text-green-400 hover:bg-green-500/10 hover:border-green-400 transition-all duration-300 flex items-center gap-2 shadow-lg shadow-green-500/20"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <FaHome size={18} />
      <span className="text-sm font-semibold">HOME</span>
    </motion.button>
  );
};

export default HomeButton;