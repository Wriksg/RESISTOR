import React from 'react';
import { useResistorStore } from './store/useResistorStore';
import LiveScanCounter from './components/LiveScanCounter';
import SpeedComparisonPanel from './components/SpeedComparisonPanel';
import RankedMutationList from './components/RankedMutationList';
import ForecastReport from './components/ForecastReport';
import StructuralView from './components/StructuralView';

function App() {
  const targetName = useResistorStore((state) => state.targetName);

  return (
    <div className="min-h-screen bg-obsidian font-sans p-4 lg:p-8 flex flex-col gap-6 overflow-x-hidden relative">
      
      {/* Subtle Background Glow */}
      <div className="fixed top-[-20%] left-[-10%] w-[50vw] h-[50vw] bg-neonCyan/5 blur-[150px] rounded-full pointer-events-none"></div>

      {/* 🔴 HEADER */}
      <header className="flex justify-between items-end pb-4 border-b border-white/10 relative z-10">
        <div>
          <h1 className="text-4xl font-black tracking-widest text-white uppercase flex items-center gap-3">
            RESISTOR <span className="text-neonCyan text-2xl">///</span>
          </h1>
          <p className="text-sm font-mono text-slate-500 mt-2 tracking-widest uppercase">
            TARGET: <span className="text-slate-300">{targetName}</span>
          </p>
        </div>
        <div className="flex items-center gap-3 font-mono text-xs text-telemetryAmber bg-telemetryAmber/10 px-4 py-2 rounded-full border border-telemetryAmber/20 shadow-[0_0_15px_rgba(255,184,0,0.15)]">
          <div className="w-2 h-2 rounded-full bg-telemetryAmber animate-pulse"></div>
          PIPELINE TRACKER: BATCH ACTIVE
        </div>
      </header>

      {/* 🔴 MAIN DASHBOARD GRID */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10">
        
        {/* LEFT PANEL: Telemetry & Compute Hub */}
        <section className="lg:col-span-4 flex flex-col gap-6">
          <div className="flex-1 bg-glass/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl flex flex-col gap-6">
            <h2 className="text-xs font-bold tracking-widest text-slate-500 uppercase">System & Controls</h2>
            <LiveScanCounter />
            <SpeedComparisonPanel />
          </div>
        </section>

        {/* RIGHT PANEL: 3D / SVG Structural View */}
        <section className="lg:col-span-8 flex flex-col gap-6">
          <div className="flex-1 bg-glass/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl relative overflow-hidden flex flex-col">
            <h2 className="text-xs font-bold tracking-widest text-slate-500 uppercase relative z-10 mb-4">Structural Visualization</h2>
            <StructuralView />
          </div>
        </section>

        {/* BOTTOM PANEL: Insights */}
        <section className="lg:col-span-12 grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Ranked Mutation Feed */}
          <div className="bg-glass/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl flex flex-col h-80">
            <h2 className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-4">Ranked Mutation Feed</h2>
            <RankedMutationList />
          </div>

          {/* AI Forecast Report */}
          <div className="bg-glass/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl flex flex-col h-80">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xs font-bold tracking-widest text-slate-500 uppercase">Fireworks AI Forecast</h2>
              <div className="flex items-center gap-2 font-mono text-[10px] text-green-400">
                <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></div>
                [ LIVE ]
              </div>
            </div>
            <ForecastReport />
          </div>

        </section>

      </main>
    </div>
  );
}

export default App;