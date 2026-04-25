import React, { useState, useEffect } from 'react';

export default function BattleCard({ competitorId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if(competitorId) {
      fetch(`/api/v1/match/${competitorId}`)
        .then(res => res.json())
        .then(setData);
    }
  }, [competitorId]);

  if (!data) return <div className="p-8 text-center animate-pulse text-slate-500">Loading Nexus Engine...</div>;

  return (
    <div className="max-w-6xl mx-auto p-6 font-sans">
      <div className="bg-slate-900 text-white p-6 rounded-xl shadow-lg mb-8 flex justify-between items-center">
        <div>
          <span className="bg-slate-700 px-2 py-1 rounded text-xs uppercase font-bold">{data.target_competitor.tier} Tier</span>
          <h1 className="text-3xl font-bold mt-2">{data.target_competitor.vendor} {data.target_competitor.model}</h1>
        </div>
        <p className="text-3xl font-bold text-emerald-400">${data.target_competitor.price_usd}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {data.matches.map((m, idx) => (
          <div key={m.id} className={`p-6 rounded-xl border-2 ${idx === 0 ? 'bg-emerald-50 border-emerald-500 shadow-xl scale-105' : 'bg-white border-slate-200'}`}>
            <div className="flex justify-between items-start mb-4">
              <span className={`px-3 py-1 text-xs font-bold rounded-full ${idx === 0 ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'}`}>
                #{idx + 1} Match
              </span>
              <span className="text-xl font-black text-slate-800">{m.final_score}%</span>
            </div>
            <h3 className="text-2xl font-bold mb-1">Omada {m.model}</h3>
            <p className="text-2xl font-extrabold text-emerald-600 mb-4">${m.price_usd}</p>
            
            {m.sales_justification && (
              <div className="bg-white/80 p-3 rounded text-sm text-slate-700 italic border border-slate-200">
                🤖 {m.sales_justification}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
