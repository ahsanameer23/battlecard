import React, { useState, useEffect } from 'react';
import { Save, Info, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';
import { motion } from 'motion/react';

interface PMPlaygroundProps {
  category?: string;
}

export default function PMPlayground({ category = "Switches" }: PMPlaygroundProps) {
  const [weights, setWeights] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetch(`/api/v1/weights/${category}`)
      .then(res => res.json())
      .then(setWeights);
  }, [category]);

  const totalWeight = weights.reduce((sum, w) => sum + w.weight, 0);
  const isValid = Math.abs(totalWeight - 1.0) < 0.001;

  const handleSave = async () => {
    if (!isValid) return;
    setSaving(true);
    try {
      await fetch(`/api/v1/weights/${category}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(weights)
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const updateWeight = (index: number, val: number) => {
    const next = [...weights];
    next[index].weight = Math.round(val * 100) / 100;
    setWeights(next);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm max-w-4xl mx-auto overflow-hidden">
      <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/30">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Algorithm Logic Tuning</h2>
          <p className="text-sm text-slate-500">Configure parameters for {category} matching engine.</p>
        </div>
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-black tracking-widest uppercase transition-all shadow-sm ${
            isValid ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700 animate-pulse'
          }`}>
            {isValid ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
            Total Allocation: {(totalWeight * 100).toFixed(0)}%
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="p-2 text-slate-400 hover:text-brand-blue hover:bg-blue-50 rounded-lg transition-all"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      <div className="p-8 space-y-8">
        {weights.map((w, idx) => (
          <div key={w.parameter} className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-700 capitalize">
                  {w.parameter.replace(/_/g, ' ')}
                </span>
                <Info size={14} className="text-slate-300 cursor-help" />
              </div>
              <div className="flex items-center gap-3">
                 <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-100 px-2 py-0.5 rounded">
                   {w.direction.replace(/_/g, ' ')}
                 </span>
                 <input 
                  type="number"
                  step="0.01"
                  value={w.weight}
                  onChange={(e) => updateWeight(idx, parseFloat(e.target.value))}
                  className="w-20 text-center font-mono font-bold text-brand-blue bg-blue-50 border-none rounded py-1 focus:ring-2 focus:ring-brand-blue/20"
                 />
              </div>
            </div>
            
            <div className="relative h-2 bg-slate-100 rounded-full group cursor-pointer">
              <motion.div 
                animate={{ width: `${w.weight * 100}%` }}
                className="absolute h-full bg-brand-blue rounded-full shadow-[0_0_8px_rgba(0,164,239,0.3)] transition-all"
              />
              <input 
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={w.weight}
                onChange={(e) => updateWeight(idx, parseFloat(e.target.value))}
                className="absolute w-full h-full opacity-0 cursor-pointer"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="px-8 py-6 bg-slate-50 border-t border-slate-100 flex justify-between items-center">
        <p className="text-xs text-slate-500 max-w-md">
          Changes applied here update the production matching engine instantly. 
          Ensure weights total 100% for proper normalization.
        </p>
        <button 
          onClick={handleSave}
          disabled={!isValid || saving}
          className={`flex items-center gap-2 px-8 py-3 rounded-xl font-black text-xs uppercase tracking-widest transition-all shadow-lg active:scale-95 ${
            isValid 
              ? 'bg-brand-blue text-white shadow-brand-blue/30 hover:bg-brand-blue/90' 
              : 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
          }`}
        >
          {saving ? (
            <RefreshCw size={16} className="animate-spin" />
          ) : success ? (
            <CheckCircle2 size={16} />
          ) : (
            <Save size={16} />
          )}
          {success ? 'Deployed' : 'Deploy Logic'}
        </button>
      </div>
    </div>
  );
}
