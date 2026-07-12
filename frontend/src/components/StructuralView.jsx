import React from 'react';
import { motion } from 'framer-motion';
import { useResistorStore } from '../store/useResistorStore';

export default function StructuralView() {
  const selected = useResistorStore((state) => state.selectedMutation);
  const isCritical = selected?.attribution?.matches_known_resistance;
  const color = isCritical ? '#FF2A85' : '#00F2FE'; // Hot Magenta if critical, Cyan if normal

  return (
    <div className="w-full h-full flex flex-col items-center justify-center relative p-4">
      
      {/* Glowing Target Graphic */}
      <motion.div 
        key={selected?.mutation} // Re-animates when mutation changes
        initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        className="relative flex items-center justify-center w-48 h-48 rounded-full border border-dashed mb-8"
        style={{ borderColor: color, boxShadow: `0 0 40px ${color}33` }}
      >
        <div className="absolute w-full h-[1px]" style={{ backgroundColor: color, opacity: 0.3 }}></div>
        <div className="absolute h-full w-[1px]" style={{ backgroundColor: color, opacity: 0.3 }}></div>
        
        {/* Pulsing Core */}
        <div className="w-4 h-4 rounded-full animate-ping absolute" style={{ backgroundColor: color }}></div>
        <div className="w-4 h-4 rounded-full relative z-10" style={{ backgroundColor: color, boxShadow: `0 0 20px ${color}` }}></div>
      </motion.div>

      {/* Live Data Feed */}
      <div className="w-full max-w-sm bg-obsidian/50 p-4 rounded-xl border border-white/5 flex flex-col items-center text-center">
        <h3 className="text-2xl font-mono font-bold tracking-widest uppercase mb-3 drop-shadow-md" style={{ color: color }}>
          {selected?.mutation || "TARGET"}
        </h3>
        <p className="text-xs text-slate-400 font-mono uppercase tracking-widest mb-2 flex justify-between w-full">
          <span>Context:</span> <span className="text-slate-200">{selected?.attribution?.structural_context}</span>
        </p>
        <p className="text-xs text-slate-400 font-mono uppercase tracking-widest flex justify-between w-full">
          <span>Severity:</span> <span className="text-slate-200">{selected?.attribution?.substitution_severity}</span>
        </p>
      </div>

    </div>
  );
}
