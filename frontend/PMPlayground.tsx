import React, { useState, useEffect } from 'react';

export default function PMPlayground({ category = "Switches" }) {
  const [weights, setWeights] = useState([]);
  
  useEffect(() => {
    fetch(`/api/v1/weights/${category}`)
      .then(res => res.json())
      .then(setWeights);
  }, [category]);

  const totalWeight = weights.reduce((sum, w) => sum + w.weight, 0);
  const isValid = Math.abs(totalWeight - 1.0) < 0.001;

  const handleSave = async () => {
    if (!isValid) return;
    await fetch(`/api/v1/weights/${category}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(weights)
    });
    alert("Algorithm deployed to database!");
  };

  return (
    <div className="max-w-3xl mx-auto p-8 bg-white rounded-xl shadow-lg border border-slate-200 font-sans">
      <h2 className="text-2xl font-bold mb-6">Algorithm Tuning: {category}</h2>
      
      <div className="space-y-6">
        {weights.map((w, idx) => (
          <div key={w.parameter} className="flex items-center gap-4">
            <span className="w-1/3 font-medium capitalize">{w.parameter.replace(/_/g, ' ')}</span>
            <input 
              type="range" min="0" max="1" step="0.05" value={w.weight}
              onChange={(e) => {
                const newWeights = [...weights];
                newWeights[idx].weight = parseFloat(e.target.value);
                setWeights(newWeights);
              }}
              className="flex-1"
            />
            <span className="w-16 text-right font-bold text-blue-600">{(w.weight * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>

      <div className="mt-8 pt-6 border-t flex justify-between items-center">
        <span className={`font-bold ${isValid ? 'text-emerald-600' : 'text-red-500'}`}>
          Total: {(totalWeight * 100).toFixed(0)}% {isValid ? '✓' : '(Must be 100%)'}
        </span>
        <button onClick={handleSave} disabled={!isValid} className="px-6 py-2 bg-slate-900 text-white rounded font-bold disabled:opacity-50">
          Deploy Logic
        </button>
      </div>
    </div>
  );
}
