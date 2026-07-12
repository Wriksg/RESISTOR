import React, { useEffect, useState } from 'react';
import { useResistorStore } from '../store/useResistorStore';

export default function ForecastReport() {
  const reportText = useResistorStore((state) => state.executiveSummary) || "Loading AI report...";
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    let i = 0;
    setDisplayedText('');
    const interval = setInterval(() => {
      setDisplayedText(reportText.slice(0, i));
      i++;
      if (i > reportText.length) clearInterval(interval);
    }, 10); // Typewriter speed
    return () => clearInterval(interval);
  }, [reportText]);

  return (
    <div className="w-full h-full text-slate-300 text-sm leading-relaxed overflow-y-auto pr-2 custom-scrollbar">
      <p className="whitespace-pre-wrap">{displayedText}<span className="animate-pulse bg-neonCyan text-transparent">_</span></p>
    </div>
  );
}