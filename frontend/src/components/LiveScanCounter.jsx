import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function LiveScanCounter() {
  const [count, setCount] = useState(0);
  const targetCount = 2983; // The exact number of mutations we scanned on the GPU

  useEffect(() => {
    let current = 0;
    const interval = setInterval(() => {
      current += 113; // Count up in chunks
      if (current >= targetCount) {
        current = targetCount;
        clearInterval(interval);
      }
      setCount(current);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-glass/40 rounded-xl border border-neonCyan/30 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-neonCyan to-transparent opacity-50"></div>
      
      <p className="text-[10px] text-neonCyan font-bold tracking-[0.2em] uppercase mb-2">Exhaustive Candidates Scanned</p>
      
      <motion.div 
        key={count}
        initial={{ opacity: 0.5, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-5xl font-black font-mono text-white drop-shadow-[0_0_15px_rgba(0,242,254,0.5)]"
      >
        {count.toLocaleString()}
      </motion.div>
    </div>
  );
}