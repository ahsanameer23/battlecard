/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  Settings2, 
  LayoutGrid, 
  LineChart, 
  History, 
  Settings, 
  Search, 
  Save, 
  Upload, 
  Bell, 
  Play, 
  Info, 
  Cloud, 
  ShieldCheck, 
  RefreshCw, 
  Network, 
  Filter, 
  Download, 
  TrendingUp, 
  Zap,
  ChevronLeft,
  ChevronRight,
  Router,
  FileUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import BattleCard from './components/BattleCard';
import PMPlayground from './components/PMPlayground';
import DatasheetIngestion from './components/DatasheetIngestion';

// --- Components ---

const Sidebar = ({ active, setActive }: { active: string, setActive: (s: string) => void }) => {
  const navItems = [
    { name: 'Weight Tuning', icon: Settings2 },
    { name: 'Competitor Matrix', icon: LayoutGrid },
    { name: 'Data Ingestion', icon: FileUp },
    { name: 'Live Dashboard', icon: LineChart },
    { name: 'Saved Presets', icon: History },
    { name: 'Settings', icon: Settings },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-brand-navy dark:bg-black text-white flex flex-col z-50 overflow-y-auto">
      <div className="px-6 py-8">
        <div className="text-xl font-bold tracking-tight">Omada Nexus</div>
        <div className="text-slate-400 text-xs font-normal mt-1 opacity-70">Network Admin</div>
      </div>
      
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.name}
            onClick={() => setActive(item.name)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-sm font-semibold tracking-wide uppercase ${
              active === item.name 
                ? 'bg-brand-blue text-white shadow-lg shadow-brand-blue/20' 
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <item.icon size={18} />
            <span>{item.name}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 mt-auto">
        <button 
          onClick={() => setActive('Data Ingestion')}
          className="w-full bg-brand-blue hover:bg-brand-blue/90 text-white py-3 rounded-lg font-bold transition-all uppercase tracking-widest text-[11px] shadow-lg shadow-brand-blue/20 active:scale-95"
        >
          New Simulation
        </button>
      </div>
    </aside>
  );
};

const TopNav = ({ onSimulate }: { onSimulate: () => void }) => (
  <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-40">
    <div className="flex items-center gap-8">
      <h1 className="text-xl font-extrabold text-brand-navy tracking-tight">Omada Nexus Playground</h1>
      <nav className="hidden xl:flex items-center gap-6">
        {['Simulations', 'Benchmarks', 'Inventory', 'Documentation'].map((link) => (
          <a key={link} href="#" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">
            {link}
          </a>
        ))}
      </nav>
    </div>
    
    <div className="flex items-center gap-4">
      <div className="relative group">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-brand-blue transition-colors" size={16} />
        <input 
          type="text" 
          placeholder="Global search..." 
          className="pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-md text-sm w-64 focus:bg-white focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue outline-none transition-all"
        />
      </div>
      
      <div className="flex items-center gap-1 border-x border-slate-100 px-2">
        <button className="p-2 text-slate-500 hover:bg-slate-100 rounded-md transition-all"><Save size={18} /></button>
        <button className="p-2 text-slate-500 hover:bg-slate-100 rounded-md transition-all"><Upload size={18} /></button>
        <button className="p-2 text-slate-500 hover:bg-slate-100 rounded-md transition-all relative">
          <Bell size={18} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white shadow-sm"></span>
        </button>
      </div>
      
      <button 
        onClick={onSimulate}
        className="flex items-center gap-2 bg-brand-blue hover:bg-brand-blue/90 text-white px-5 py-2 rounded-lg text-sm font-bold shadow-md shadow-brand-blue/20 transition-all active:scale-95"
      >
        <Play size={16} fill="currentColor" />
        <span>Simulate</span>
      </button>
    </div>
  </header>
);

const SliderField = ({ label, value, onChange }: { label: string, value: number, onChange: (v: number) => void }) => (
  <div className="space-y-3">
    <div className="flex justify-between items-center">
      <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{label}</label>
      <span className="text-sm font-mono font-bold text-brand-blue bg-blue-50 px-2 py-0.5 rounded">{value.toFixed(2)}</span>
    </div>
    <div className="relative group py-2">
      <input 
        type="range" 
        min="0" 
        max="1" 
        step="0.01" 
        value={value} 
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-slate-100 rounded-full appearance-none cursor-pointer accent-brand-blue"
      />
    </div>
  </div>
);

const ToggleField = ({ label, enabled, onToggle }: { label: string, enabled: boolean, onToggle: () => void }) => (
  <button 
    onClick={onToggle}
    className="w-full flex items-center justify-between p-3 rounded-lg bg-slate-50 hover:bg-slate-100/80 transition-colors group"
  >
    <span className="text-sm font-medium text-slate-700 group-hover:text-slate-900">{label}</span>
    <div className={`w-10 h-5 rounded-full relative transition-all duration-300 ${enabled ? 'bg-brand-blue shadow-inner shadow-black/10' : 'bg-slate-300'}`}>
      <motion.div 
        animate={{ x: enabled ? 20 : 2 }}
        initial={false}
        className="absolute top-1 w-3 h-3 bg-white rounded-full shadow-sm"
      />
    </div>
  </button>
);

const EcosystemMultiplier = ({ icon: Icon, value, progress }: { icon: any, value: string, progress: number }) => (
  <div className="flex items-center gap-3">
    <Icon size={18} className="text-slate-400 shrink-0" />
    <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
      <motion.div 
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
        className="h-full bg-brand-blue/60"
      />
    </div>
    <span className="text-xs font-mono font-bold text-slate-500 w-10 text-right">{value}</span>
  </div>
);

export default function App() {
  const [activeView, setActiveView] = useState('Weight Tuning');
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [selectedCompetitorId, setSelectedCompetitorId] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/v1/products?source=competitor')
      .then(res => res.json())
      .then(setCompetitors);
  }, [activeView]);

  const handleSimulate = () => {
    if (selectedCompetitorId) {
      setActiveView('Battle Card');
    }
  };

  return (
    <div className="min-h-screen pl-64 transition-all duration-300">
      <Sidebar active={activeView} setActive={setActiveView} />
      
      <div className="flex flex-col min-h-screen">
        <TopNav onSimulate={handleSimulate} />
        
        <main className="flex-1 p-8 bg-slate-50/50 overflow-y-auto">
          <AnimatePresence mode="wait">
            {activeView === 'Weight Tuning' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} key="tuning">
                <PMPlayground />
              </motion.div>
            )}

            {activeView === 'Data Ingestion' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} key="ingestion">
                <DatasheetIngestion />
              </motion.div>
            )}

            {activeView === 'Competitor Matrix' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} key="matrix" className="space-y-6">
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                  <div className="px-6 py-5 border-b border-slate-100 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-slate-900">Competitor Matrix</h2>
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-widest">{competitors.length} Devices Tracked</div>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="bg-slate-50/50 border-b border-slate-100">
                          <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Device</th>
                          <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Category</th>
                          <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Completeness</th>
                          <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Pricing</th>
                          <th className="px-6 py-4"></th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                        {competitors.map((c) => (
                          <tr 
                            key={c.id} 
                            onClick={() => setSelectedCompetitorId(c.id)}
                            className={`hover:bg-slate-50/80 transition-all cursor-pointer group ${selectedCompetitorId === c.id ? 'bg-blue-50/50' : ''}`}
                          >
                            <td className="px-6 py-4">
                              <div className="flex flex-col">
                                <span className="font-bold text-slate-900 group-hover:text-brand-blue transition-colors">
                                  {c.vendor} <span className="text-slate-400">{c.model}</span>
                                </span>
                                <span className="text-[10px] text-slate-400 uppercase font-medium mt-0.5">{c.tier}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded">
                                {c.subcategory || c.category}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-3">
                                <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden max-w-[80px]">
                                  <div className="h-full bg-brand-blue" style={{ width: `${c.data_completeness * 100}%` }}></div>
                                </div>
                                <span className="text-[10px] font-bold text-slate-500">{(c.data_completeness * 100).toFixed(0)}%</span>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-right">
                              <span className="text-sm font-black text-slate-900">${c.price_usd || '---'}</span>
                            </td>
                            <td className="px-6 py-4 text-right">
                              <button 
                                onClick={(e) => { e.stopPropagation(); setSelectedCompetitorId(c.id); handleSimulate(); }}
                                className="opacity-0 group-hover:opacity-100 bg-brand-blue text-white p-2 rounded-lg transition-all"
                              >
                                <Zap size={14} fill="currentColor" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </motion.div>
            )}

            {activeView === 'Battle Card' && (
              <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} key="battle">
                <BattleCard competitorId={selectedCompetitorId || undefined} />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
        
        {/* Floating Action Button */}
        {selectedCompetitorId && activeView !== 'Battle Card' && (
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={handleSimulate}
            className="fixed bottom-8 right-8 bg-brand-blue hover:bg-brand-blue/90 text-white shadow-2xl shadow-brand-blue/40 px-8 py-5 rounded-full font-black text-sm flex items-center gap-3 transition-all z-50 uppercase tracking-widest active:shadow-lg"
          >
            <Zap size={20} fill="currentColor" />
            <span>Simulate Model</span>
          </motion.button>
        )}
      </div>
    </div>
  );
}
