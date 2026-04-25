import React, { useState, useEffect } from 'react';
import { Shield, TrendingUp, ChevronRight, Zap } from 'lucide-react';
import { motion } from 'motion/react';

interface BattleCardProps {
  competitorId?: string;
}

export default function BattleCard({ competitorId }: BattleCardProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (competitorId) {
      setLoading(true);
      fetch(`/api/v1/match/${competitorId}`)
        .then(res => res.json())
        .then(res => {
          setData(res);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [competitorId]);

  if (!competitorId) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-400">
        <Shield size={64} className="mb-4 opacity-20" />
        <p className="text-lg font-medium">Select a competitor to generate a Battle Card</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-12 space-y-8 animate-pulse">
        <div className="h-32 bg-slate-200 rounded-xl"></div>
        <div className="grid grid-cols-3 gap-6">
          <div className="h-64 bg-slate-100 rounded-xl"></div>
          <div className="h-64 bg-slate-100 rounded-xl"></div>
          <div className="h-64 bg-slate-100 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!data || !data.target_competitor) return null;

  return (
    <div className="space-y-8">
      {/* Target Competitor Header */}
      <div className="bg-brand-navy text-white p-8 rounded-xl shadow-xl flex justify-between items-center relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-3xl"></div>
        <div className="relative z-10">
          <span className="bg-brand-blue/20 text-brand-blue px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest border border-brand-blue/30">
            {data.target_competitor.tier} Tier
          </span>
          <h1 className="text-4xl font-black mt-4 tracking-tighter">
            {data.target_competitor.vendor} <span className="text-slate-400">{data.target_competitor.model}</span>
          </h1>
          <div className="flex gap-4 mt-4">
             {Object.entries(data.target_competitor.specs_json.quantitative || {}).slice(0, 3).map(([key, val]: any) => (
               <span key={key} className="text-xs font-mono text-slate-400 bg-white/5 px-2 py-1 rounded">
                 {key}: {val}
               </span>
             ))}
          </div>
        </div>
        <div className="text-right relative z-10">
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-1">Target Pricing</p>
          <p className="text-4xl font-black text-brand-blue">${data.target_competitor.price_usd}</p>
        </div>
      </div>

      {/* Match Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {data.matches.map((m: any, idx: number) => (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            key={m.id} 
            className={`p-6 rounded-2xl border-2 transition-all group relative ${
              idx === 0 
                ? 'bg-white border-brand-blue shadow-2xl shadow-brand-blue/10 scale-105' 
                : 'bg-slate-50 border-slate-200 hover:border-slate-300'
            }`}
          >
            {idx === 0 && (
              <div className="absolute top-[-12px] left-1/2 -translate-x-1/2 bg-brand-blue text-white text-[10px] font-black px-4 py-1 rounded-full uppercase tracking-widest shadow-lg">
                Recommended Solution
              </div>
            )}
            
            <div className="flex justify-between items-start mb-6">
              <span className={`text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest ${
                idx === 0 ? 'bg-brand-blue text-white' : 'bg-slate-200 text-slate-600'
              }`}>
                {m.final_score}% Match
              </span>
              {m.final_score > 90 && <Zap size={16} className="text-yellow-500 fill-yellow-500" />}
            </div>

            <h3 className="text-xl font-bold text-slate-900 mb-1 group-hover:text-brand-blue transition-colors">
              Omada {m.model}
            </h3>
            <p className="text-2xl font-black text-brand-blue mb-6">${m.price_usd}</p>

            <div className="space-y-2 mb-8">
              {Object.entries(m.specs.quantitative || {}).slice(0, 4).map(([key, val]: any) => (
                <div key={key} className="flex justify-between text-xs border-b border-dashed border-slate-200 pb-1">
                  <span className="text-slate-400 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="font-mono font-bold text-slate-700">{val}</span>
                </div>
              ))}
            </div>

            {m.sales_justification ? (
              <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-800 italic leading-relaxed">
                <span className="font-bold block mb-1">🤖 AI Justification</span>
                "{m.sales_justification}"
              </div>
            ) : (
               <button className="w-full py-2 bg-slate-900 text-white rounded-lg text-xs font-black uppercase tracking-widest hover:bg-brand-navy transition-all flex items-center justify-center gap-2">
                 Generate Rationale <ChevronRight size={14} />
               </button>
            )}
          </motion.div>
        ))}
      </div>
      
      {/* Market Sentiment / Stats */}
      <div className="grid grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl border border-slate-200">
           <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Competitive Gap Analysis</p>
           <div className="space-y-4">
             <div className="flex items-center gap-4">
               <div className="w-24 text-[10px] font-bold text-slate-500 uppercase">Pricing Edge</div>
               <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                 <div className="h-full bg-green-500 w-[75%]"></div>
               </div>
               <div className="text-xs font-bold text-green-600">+12%</div>
             </div>
             <div className="flex items-center gap-4">
               <div className="w-24 text-[10px] font-bold text-slate-500 uppercase">Spec Parity</div>
               <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                 <div className="h-full bg-brand-blue w-[92%]"></div>
               </div>
               <div className="text-xs font-bold text-brand-blue">92%</div>
             </div>
           </div>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 flex items-center justify-between">
           <div>
             <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Win Probability</p>
             <h4 className="text-4xl font-black text-slate-900">84.2%</h4>
           </div>
           <div className="p-4 bg-green-50 rounded-full">
             <TrendingUp size={32} className="text-green-600" />
           </div>
        </div>
      </div>
    </div>
  );
}
