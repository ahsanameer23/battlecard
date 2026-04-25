import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, RefreshCw, X, AlertCircle, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export default function DatasheetIngestion() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    vendor: '',
    model: '',
    category: 'Switches',
    price_usd: ''
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return setError('Please select a PDF datasheet');
    if (!formData.vendor || !formData.model) return setError('Vendor and Model are required');

    setLoading(true);
    setError(null);

    const data = new FormData();
    data.append('file', file);
    data.append('vendor', formData.vendor);
    data.append('model', formData.model);
    data.append('category', formData.category);
    data.append('price_usd', formData.price_usd);
    data.append('tier', 'Enterprise');

    try {
      const res = await fetch('/api/v1/ingest', {
        method: 'POST',
        body: data
      });
      const result = await res.json();
      if (result.error) throw new Error(result.error);
      setSuccess(result.specs);
      setFile(null);
      setFormData({ vendor: '', model: '', category: 'Switches', price_usd: '' });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm max-w-4xl mx-auto overflow-hidden">
      <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Form Section */}
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">Stage 0: Data Ingestion</h2>
            <p className="text-sm text-slate-500 mt-1">AI-powered PDF normalization pipeline.</p>
          </div>

          <form onSubmit={handleUpload} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Vendor</label>
                <input 
                  type="text" 
                  value={formData.vendor}
                  onChange={(e) => setFormData({...formData, vendor: e.target.value})}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue outline-none transition-all text-sm"
                  placeholder="e.g. Cisco"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Model</label>
                <input 
                  type="text" 
                  value={formData.model}
                  onChange={(e) => setFormData({...formData, model: e.target.value})}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue outline-none transition-all text-sm"
                  placeholder="e.g. C1000-24P"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Target Price (USD)</label>
              <input 
                type="number" 
                value={formData.price_usd}
                onChange={(e) => setFormData({...formData, price_usd: e.target.value})}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue outline-none transition-all text-sm"
                placeholder="e.g. 1299"
              />
            </div>

            <div 
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 transition-all cursor-pointer flex flex-col items-center justify-center gap-3 relative overflow-hidden ${
                file ? 'bg-blue-50 border-brand-blue' : 'bg-slate-50 border-slate-200 hover:border-slate-300'
              }`}
            >
              <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".pdf" />
              {file ? (
                <>
                  <div className="bg-brand-blue p-3 rounded-full text-white shadow-lg shadow-brand-blue/30">
                    <FileText size={24} />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-bold text-slate-900 truncate max-w-[200px]">{file.name}</p>
                    <p className="text-xs text-brand-blue font-bold">Ready for ingestion</p>
                  </div>
                  <button 
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    className="absolute top-2 right-2 p-1 hover:bg-white rounded-full text-slate-400"
                  >
                    <X size={16} />
                  </button>
                </>
              ) : (
                <>
                  <div className="bg-white p-3 rounded-full text-slate-400 shadow-sm border border-slate-200">
                    <Upload size={24} />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-bold text-slate-700">Click to upload PDF</p>
                    <p className="text-[10px] text-slate-400 font-medium">Standard device datasheet formats</p>
                  </div>
                </>
              )}
            </div>

            <button 
              type="submit"
              disabled={loading || !file}
              className={`w-full py-4 rounded-xl font-black text-xs uppercase tracking-widest transition-all shadow-lg active:scale-95 flex items-center justify-center gap-2 ${
                loading || !file 
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed' 
                  : 'bg-brand-blue text-white shadow-brand-blue/30 hover:bg-brand-blue/90'
              }`}
            >
              {loading ? <RefreshCw size={18} className="animate-spin" /> : <Zap size={18} fill="currentColor" />}
              {loading ? 'AI Processing...' : 'Start Extraction'}
            </button>
            
            {error && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded-lg text-xs font-bold">
                <AlertCircle size={14} />
                {error}
              </motion.div>
            )}
          </form>
        </div>

        {/* Results / Info Section */}
        <div className="bg-slate-50/50 rounded-2xl p-8 border border-slate-100 flex flex-col items-center justify-center text-center">
           <AnimatePresence mode="wait">
             {success ? (
               <motion.div 
                 key="success"
                 initial={{ scale: 0.9, opacity: 0 }}
                 animate={{ scale: 1, opacity: 1 }}
                 className="space-y-6 w-full"
               >
                 <div className="bg-green-100 p-4 rounded-full text-green-600 inline-block">
                    <CheckCircle2 size={40} />
                 </div>
                 <div>
                    <h3 className="text-xl font-black text-slate-900">Ingestion Complete</h3>
                    <p className="text-sm text-slate-500 mt-1">Device normalized into Nexus Schema.</p>
                 </div>
                 
                 <div className="bg-white border border-slate-200 rounded-xl p-4 text-left space-y-3">
                   <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Extracted Specs</p>
                   {Object.entries(success.quantitative || {}).map(([key, val]: any) => (
                     <div key={key} className="flex justify-between text-xs border-b border-slate-50 pb-1">
                       <span className="text-slate-500 capitalize">{key.replace(/_/g, ' ')}</span>
                       <span className="font-mono font-bold text-slate-900">{val || 'N/A'}</span>
                     </div>
                   ))}
                 </div>
                 
                 <button 
                  onClick={() => setSuccess(null)}
                  className="text-brand-blue text-xs font-bold uppercase tracking-widest hover:underline"
                 >
                   Inject Another Datasheet
                 </button>
               </motion.div>
             ) : (
               <motion.div 
                 key="idle"
                 initial={{ opacity: 0 }}
                 animate={{ opacity: 1 }}
                 className="space-y-4"
               >
                 <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center border border-slate-200 shadow-sm mx-auto">
                    <FileText size={32} className="text-slate-300" />
                 </div>
                 <div>
                    <h4 className="font-bold text-slate-900">Waiting for Data</h4>
                    <p className="text-xs text-slate-500 max-w-[200px] mx-auto mt-2 leading-relaxed">
                       Our Gemini model will parse technical tables and normalize hardware definitions.
                    </p>
                 </div>
               </motion.div>
             )}
           </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
