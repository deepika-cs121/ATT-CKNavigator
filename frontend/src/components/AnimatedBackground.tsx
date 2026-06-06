import { motion } from 'framer-motion';

export const AnimatedBackground = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-gray-950" />

      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(34, 197, 94, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(34, 197, 94, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          animation: 'gridMove 20s linear infinite'
        }} />
      </div>

      {[...Array(5)].map((_, i) => (
        <motion.div
          key={`hex-${i}`}
          className="absolute"
          style={{
            left: `${5 + (i * 18)}%`,
            top: `${10 + (i % 3) * 25}%`,
            width: `${40 + (i % 4) * 15}px`,
            height: `${40 + (i % 4) * 15}px`,
            border: '2px solid rgba(34, 197, 94, 0.3)',
            clipPath: 'polygon(30% 0%, 70% 0%, 100% 50%, 70% 100%, 30% 100%, 0% 50%)',
          }}
          animate={{
            y: [0, -20, 0],
            opacity: [0.3, 0.6, 0.3],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 4 + i * 0.3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {[...Array(7)].map((_, i) => (
        <motion.div
          key={`shape-${i}`}
          className="absolute rounded-full"
          style={{
            left: `${5 + (i * 15)}%`,
            top: `${5 + (i % 4) * 20}%`,
            width: `${25 + (i % 5) * 15}px`,
            height: `${25 + (i % 5) * 15}px`,
            background: `radial-gradient(circle, rgba(34, 197, 94, 0.4), transparent)`,
          }}
          animate={{
            y: [0, -30, 0],
            x: [0, 20, 0],
            scale: [1, 1.2, 1],
            opacity: [0.4, 0.7, 0.4],
          }}
          transition={{
            duration: 5 + i * 0.3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {[...Array(4)].map((_, i) => (
        <motion.div
          key={`square-${i}`}
          className="absolute"
          style={{
            left: `${8 + (i * 22)}%`,
            top: `${15 + (i % 2) * 30}%`,
            width: `${30 + (i % 3) * 10}px`,
            height: `${30 + (i % 3) * 10}px`,
            border: '1px solid rgba(34, 197, 94, 0.25)',
            transform: 'rotate(45deg)',
          }}
          animate={{
            rotate: [45, 65, 45],
            y: [0, 15, 0],
            opacity: [0.25, 0.5, 0.25],
          }}
          transition={{
            duration: 6 + i * 0.4,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      {[...Array(3)].map((_, i) => (
        <motion.div
          key={`triangle-${i}`}
          className="absolute"
          style={{
            left: `${12 + (i * 30)}%`,
            top: `${8 + (i % 2) * 40}%`,
            width: 0,
            height: 0,
            borderLeft: `${20 + (i % 3) * 10}px solid transparent`,
            borderRight: `${20 + (i % 3) * 10}px solid transparent`,
            borderBottom: `${35 + (i % 3) * 15}px solid rgba(34, 197, 94, 0.2)`,
          }}
          animate={{
            y: [0, -25, 0],
            opacity: [0.2, 0.45, 0.2],
            rotate: [0, 10, 0],
          }}
          transition={{
            duration: 5.5 + i * 0.35,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
      
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={`glass-${i}`}
          className="absolute rounded-lg backdrop-blur-sm"
          style={{
            left: `${6 + (i * 16)}%`,
            top: `${12 + (i % 3) * 30}%`,
            width: `${40 + (i % 4) * 20}px`,
            height: `${40 + (i % 4) * 20}px`,
            background: 'rgba(34, 197, 94, 0.05)',
            border: '1px solid rgba(34, 197, 94, 0.2)',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
          }}
          animate={{
            y: [0, -18, 0],
            x: [0, 10, 0],
            opacity: [0.3, 0.6, 0.3],
            rotate: [0, 5, 0],
          }}
          transition={{
            duration: 6 + i * 0.35,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(34, 197, 94, 0)" />
            <stop offset="50%" stopColor="rgba(34, 197, 94, 0.4)" />
            <stop offset="100%" stopColor="rgba(34, 197, 94, 0)" />
          </linearGradient>
        </defs>

        {[...Array(8)].map((_, i) => {
          const x1 = (i * 13) % 100;
          const y1 = (i * 21) % 100;
          const x2 = ((i * 13) + 15 + (i % 20)) % 100;
          const y2 = ((i * 21) + 12 + (i % 15)) % 100;

          return (
            <motion.line
              key={`conn-line-${i}`}
              x1={`${x1}%`}
              y1={`${y1}%`}
              x2={`${x2}%`}
              y2={`${y2}%`}
              stroke="url(#lineGradient)"
              strokeWidth="1"
              opacity="0.3"
              animate={{
                opacity: [0.2, 0.5, 0.2],
                pathLength: [0, 1, 0],
              }}
              transition={{
                duration: 4 + i * 0.2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          );
        })}

        {[...Array(10)].map((_, i) => {
          const cx = (5 + i * 10) % 100;
          const cy = (8 + i * 9) % 100;

          return (
            <motion.circle
              key={`node-${i}`}
              cx={`${cx}%`}
              cy={`${cy}%`}
              r="3"
              fill="rgba(34, 197, 94, 0.6)"
              stroke="rgba(34, 197, 94, 0.8)"
              strokeWidth="1"
              animate={{
                r: [3, 5, 3],
                opacity: [0.4, 0.8, 0.4],
              }}
              transition={{
                duration: 3 + i * 0.15,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          );
        })}
      </svg>

      {[...Array(4)].map((_, i) => (
        <motion.div
          key={`line-${i}`}
          className="absolute h-px bg-gradient-to-r from-transparent via-green-500 to-transparent"
          style={{
            left: 0,
            right: 0,
            top: `${25 * i}%`,
            opacity: 0.2,
          }}
          animate={{
            scaleX: [0, 1, 0],
            opacity: [0, 0.4, 0],
          }}
          transition={{
            duration: 3,
            delay: i * 0.7,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}

      <style>{`
        @keyframes gridMove {
          0% { transform: translateY(0); }
          100% { transform: translateY(50px); }
        }
      `}</style>
    </div>
  );
};

export default AnimatedBackground;