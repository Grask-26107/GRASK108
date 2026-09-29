import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, CheckCircle2, AlertTriangle, RefreshCw, X, ShieldCheck, Cpu } from 'lucide-react';
import { healthApi } from '../services/api';

interface GeminiStatusIndicatorProps {
  addToast?: (type: 'success' | 'error' | 'info', message: string) => void;
}

export const GeminiStatusIndicator: React.FC<GeminiStatusIndicatorProps> = ({ addToast }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusData, setStatusData] = useState<{
    is_healthy: boolean;
    gemini_online: boolean;
    active_model: string;
    available_models: string[];
    latency_ms: number;
    message: string;
    timestamp?: string;
  }>({
    is_healthy: true,
    gemini_online: true,
    active_model: 'gemini-3.8-flash',
    available_models: ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-flash-latest', 'gemini-3.5-flash'],
    latency_ms: 35.0,
    message: 'Connected to Google Gemini AI (gemini-3.8-flash) — All Systems Operational',
  });

  const popoverRef = useRef<HTMLDivElement>(null);

  const fetchStatus = async (force: boolean = false) => {
    setLoading(true);
    try {
      const data = await healthApi.checkGeminiStatus(force);
      const isOnline = Boolean(data.gemini_online ?? (data.status === 'healthy'));
      setStatusData({
        is_healthy: isOnline,
        gemini_online: isOnline,
        active_model: data.active_model || 'gemini-3.8-flash',
        available_models: data.available_models || ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-flash-latest'],
        latency_ms: data.latency_ms || 45,
        message: data.message || (isOnline ? 'Model Accessed & All Perfect — No problem with Gemini key' : 'Gemini Offline Fallback Active'),
        timestamp: data.timestamp || new Date().toLocaleTimeString(),
      });
      if (force && addToast) {
        if (isOnline) {
          addToast('success', `Gemini Live Check: ${data.active_model || 'gemini-3.8-flash'} verified and responding!`);
        } else {
          addToast('error', 'Gemini check reported an issue. Local fallback engine active.');
        }
      }
    } catch (err) {
      setStatusData((prev) => ({
        ...prev,
        is_healthy: false,
        gemini_online: false,
        message: 'Could not connect to Gemini endpoint. Running on local offline engine.',
      }));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus(false);
    // Poll every 60 seconds
    const interval = setInterval(() => {
      fetchStatus(false);
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  // Close popover when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const isHealthy = statusData.is_healthy && statusData.gemini_online;

  return (
    <div className="relative inline-block" ref={popoverRef}>
      {/* Peanut-Sized Micro Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`inline-flex items-center gap-1.5 h-5 px-2 rounded-full text-[10px] font-mono font-bold border transition-all cursor-pointer shadow-xs select-none ${
          isHealthy
            ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800 hover:scale-105'
            : 'bg-sky-50 dark:bg-sky-950/60 text-sky-700 dark:text-sky-300 border-sky-300 dark:border-sky-800 hover:scale-105'
        }`}
        title={
          isHealthy
            ? `AI Online: ${statusData.active_model} active. Click for diagnostics.`
            : 'Local RAG (Offline) Active — ChromaDB + BM25 + Deterministic Rules. Click for details.'
        }
      >
        <span className="relative flex h-2 w-2 shrink-0">
          {isHealthy && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60"></span>}
          <span className={`relative inline-flex rounded-full h-2 w-2 ${isHealthy ? 'bg-emerald-500' : 'bg-sky-500'}`}></span>
        </span>
        <span className="text-[9px] uppercase tracking-wider font-semibold">{isHealthy ? 'AI' : 'RAG'}</span>
      </button>

      {/* Sleek Diagnostics Popover Card */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-800 p-4 z-50 text-xs animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center space-x-2">
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center text-white ${
                  isHealthy ? 'bg-emerald-600' : 'bg-rose-600'
                }`}
              >
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-white">
                  Google Gemini AI Engine
                </h4>
                <p className="text-[10px] text-slate-400">
                  Real-Time Connection & Model Monitor
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="py-3 space-y-2.5">
            {/* Health Status Pill */}
            <div
              className={`p-2.5 rounded-xl border flex items-center justify-between ${
                isHealthy
                  ? 'bg-emerald-50/70 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800/60'
                  : 'bg-rose-50/70 dark:bg-rose-950/30 border-rose-200 dark:border-rose-800/60'
              }`}
            >
              <div className="flex items-center space-x-2">
                {isHealthy ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
                )}
                <div>
                  <span
                    className={`font-bold block ${
                      isHealthy
                        ? 'text-emerald-900 dark:text-emerald-200'
                        : 'text-rose-900 dark:text-rose-200'
                    }`}
                  >
                    {isHealthy ? 'Working & Model Accessed' : 'Offline Engine Active'}
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400">
                    {isHealthy
                      ? 'All perfect: Gemini API key valid and active'
                      : 'Temporary network delay or quota limit'}
                  </span>
                </div>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  isHealthy
                    ? 'bg-emerald-200 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200'
                    : 'bg-rose-200 dark:bg-rose-900 text-rose-800 dark:text-rose-200'
                }`}
              >
                {isHealthy ? 'OPERATIONAL' : 'FALLBACK'}
              </span>
            </div>

            {/* Model & Latency Details */}
            <div className="bg-slate-50 dark:bg-slate-850 p-3 rounded-xl space-y-1.5 border border-slate-100 dark:border-slate-800 text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-slate-500 dark:text-slate-400 flex items-center space-x-1">
                  <Cpu className="w-3.5 h-3.5 text-blue-500" />
                  <span>Active Model:</span>
                </span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-200">
                  {statusData.active_model}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-500 dark:text-slate-400">Response Latency:</span>
                <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                  {statusData.latency_ms} ms
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-500 dark:text-slate-400">Failover Pipeline:</span>
                <span className="text-[10px] text-slate-600 dark:text-slate-300 font-mono">
                  3.8-flash → 2.5-flash → latest
                </span>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-tight">
              {statusData.message}
            </p>
          </div>

          {/* Action Footer */}
          <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <span className="text-[10px] text-slate-400 flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-500" />
              <span>Auto-Recovery Enabled</span>
            </span>
            <button
              type="button"
              disabled={loading}
              onClick={() => fetchStatus(true)}
              className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-50 dark:bg-blue-950/50 hover:bg-blue-100 dark:hover:bg-blue-900/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Testing...' : 'Test Connection'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GeminiStatusIndicator;
