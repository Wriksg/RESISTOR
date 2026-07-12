import React from 'react';
import { motion } from 'framer-motion';
import { useResistorStore } from '../store/useResistorStore';

export default function RankedMutationList() {
  const mutations = useResistorStore((state) => state.mutations) || [];
  const selected = useResistorStore((state) => state.selectedMutation);
  const setSelected = useResistorStore((state) => state.setSelectedMutation);

  return (
    <div className="w-full h-full overflow-y-auto pr-2 custom-scrollbar">
      <table className="w-full text-left text-xs">
        <thead className="sticky top-0 bg-glass backdrop-blur-md z-10 border-b border-slate-700">
          <tr className="text-slate-400 uppercase tracking-wider">
            <th className="pb-2">Rank</th>
            <th className="pb-2">Mutation</th>
            <th className="pb-2 text-right">Binding Δ</th>
            <th className="pb-2 text-right">Stability Δ</th>
          </tr>
        </thead>
        <tbody>
          {mutations.map((mut, idx) => {
            const isSelected = selected?.mutation === mut.mutation;
            const isCritical = mut.attribution.matches_known_resistance;
            return (
              <motion.tr 
                initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }}
                key={mut.mutation}
                onClick={() => setSelected(mut)}
                className={`cursor-pointer transition-colors border-b border-white/5 hover:bg-white/5 ${isSelected ? 'bg-white/10' : ''}`}
              >
                <td className="py-3 font-mono text-slate-500">#{mut.rank}</td>
                <td className={`py-3 font-mono font-bold ${isCritical ? 'text-hotMagenta drop-shadow-[0_0_8px_rgba(255,42,133,0.8)]' : 'text-neonCyan'}`}>
                  {mut.mutation}
                </td>
                <td className="py-3 font-mono text-right text-slate-300">{mut.binding_delta.toFixed(4)}</td>
                <td className="py-3 font-mono text-right text-slate-300">{mut.stability_delta.toFixed(4)}</td>
              </motion.tr>
            )
          })}
        </tbody>
      </table>
    </div>
  );
}