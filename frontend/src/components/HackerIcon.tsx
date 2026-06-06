import { FaLaptopCode } from 'react-icons/fa';
import { motion, Variants } from 'framer-motion';

const typingAnimation: Variants = {
  hidden: { width: '0' },
  visible: {
    width: 'auto',
    transition: {
      duration: 1.5,
      ease: 'linear', 
      repeat: Infinity,
    },
  },
};

const cursorAnimation: Variants = {
  blink: {
    opacity: [0, 1, 1, 0],
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

export const HackerIcon = () => {
  return (
    <div className="absolute bottom-4 left-4 z-30 p-3 bg-gray-950/80 border border-red-500/30 rounded-lg flex items-center gap-3">
      <FaLaptopCode className="text-red-400" size={24} />
      <div className="flex items-center font-mono text-sm text-green-400">
        <span className="text-gray-400 mr-1">$</span>
        <motion.span
          style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}
          variants={typingAnimation}
          initial="hidden"
          animate="visible"
        >
          run_exploit.sh
        </motion.span>
        <motion.div
          className="w-0.5 h-4 bg-green-400"
          variants={cursorAnimation}
          animate="blink"
        />
      </div>
    </div>
  );
};

export default HackerIcon;