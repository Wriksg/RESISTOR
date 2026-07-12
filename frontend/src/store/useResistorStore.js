import { create } from 'zustand';

// Direct import guarantees zero network failure on stage
import dashboardPayload from '../data/dashboard_payload.json';
import benchmarkResults from '../data/benchmark_results.json';

export const useResistorStore = create((set) => ({
  // --- STATIC DATA ---
  targetName: dashboardPayload.target,
  mutations: dashboardPayload.top_mutations,
  executiveSummary: dashboardPayload.executive_summary,
  benchmark: benchmarkResults,

  // --- DYNAMIC UI STATE ---
  // Default the selected mutation to the #1 most dangerous threat
  selectedMutation: dashboardPayload.top_mutations[0], 
  reportStatus: 'LIVE', 

  // --- ACTIONS ---
  setSelectedMutation: (mutation) => set({ selectedMutation: mutation }),
  setReportStatus: (status) => set({ reportStatus: status })
}));