import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  ThumbsUp,
  ThumbsDown,
  ShieldCheck,
  FileCheck2,
  BookOpen,
  Table,
  RefreshCw,
  Clock,
  Layers,
  Activity,
  X,
  Lock,
  Unlock,
  Download,
  KeyRound
} from 'lucide-react';
import { TelemetryDashboardResponse } from '../types';
import { telemetryApi } from '../services/api';

interface TelemetryDashboardProps {
  addToast: (type: 'success' | 'error' | 'info', message: string) => void;
  onClose?: () => void;
}

export const TelemetryDashboard: React.FC<TelemetryDashboardProps> = ({ addToast, onClose }) => {
  const [metrics, setMetrics] = useState<TelemetryDashboardResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [isOfficerMode, setIsOfficerMode] = useState<boolean>(false);
  const [showOfficerModal, setShowOfficerModal] = useState<boolean>(false);
  const [pinInput, setPinInput] = useState<string>('');
  const [pinError, setPinError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const data = await telemetryApi.getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load telemetry metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportAudit = () => {
    if (!metrics) return;
    const dossier = {
      agency: "Bureau of Indian Standards & GRASK AI Telemetry",
      statutory_mandate: "BIS Act 2016 - National Regulatory Grounding & Enforcement Oversight",
      exported_at: new Date().toISOString(),
      officer_clearance: "REGIONAL_STANDARDS_INSPECTOR_LEVEL_2",
      telemetry_payload: metrics
    };
    const blob = new Blob([JSON.stringify(dossier, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bis_telemetry_statutory_audit_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    addToast('success', 'Statutory Telemetry Audit Dossier successfully downloaded.');
  };

  const handleVerifyOfficer = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (pinInput.trim() === '1915' || pinInput.trim().toLowerCase() === 'bis' || pinInput.trim() === 'admin') {
      setIsOfficerMode(true);
      setShowOfficerModal(false);
      setPinInput('');
      setPinError(null);
      addToast('success', 'Nodal Officer Clearance Granted: Statutory Audit Tools Unlocked.');
    } else {
      setPinError('Invalid PIN. Use authorized National Consumer Toll-Free PIN: 1915');
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 20000);
    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500 text-xs">
        <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
        <span>Loading Government Oversight Telemetry...</span>
      </div>
    );
  }

  const totalQueries = Math.max(1, metrics.total_queries);
  const industryPct = Math.round((metrics.industry_queries / totalQueries) * 100);
  const consumerPct = Math.round((metrics.consumer_queries / totalQueries) * 100);

  return (
    <div className="space-y-6 max-w-6xl mx-auto px-1 sm:px-2">
      {/* 3D Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel-3d p-6 rounded-3xl">
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="p-2.5 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-md shadow-emerald-500/25">
              <Activity className="w-5 h-5" />
            </span>
            <div>
              <h2 className="text-base sm:text-lg font-black text-slate-900 dark:text-slate-100">
                GRASK AI: Government Oversight & Telemetry Analytics
              </h2>
              <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400">
                Continuous Accuracy & Conformance Monitoring (SIH26107)
              </span>
            </div>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 max-w-2xl leading-relaxed">
            Real-time telemetry tracking query volume, grounding accuracy, user satisfaction feedback, and conformity audit ratios under the BIS Act 2016.
          </p>
        </div>

        <div className="flex items-center space-x-2 self-start sm:self-auto">
          {isOfficerMode && (
            <button
              onClick={handleExportAudit}
              className="flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl shadow-sm transition-all"
              title="Download Statutory Audit Dossier"
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Export Audit Dossier</span>
            </button>
          )}

          <button
            onClick={() => {
              if (isOfficerMode) {
                setIsOfficerMode(false);
                addToast('info', 'Returned to Public Telemetry View.');
              } else {
                setShowOfficerModal(true);
              }
            }}
            className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold rounded-2xl border transition-all ${
              isOfficerMode
                ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700'
                : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700'
            }`}
          >
            {isOfficerMode ? <Unlock className="w-3.5 h-3.5 text-amber-600" /> : <Lock className="w-3.5 h-3.5 text-slate-400" />}
            <span>{isOfficerMode ? 'Officer Mode: Active' : 'Officer Mode'}</span>
          </button>

          <button
            onClick={fetchMetrics}
            className="flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-2xl hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="p-2 border border-slate-200 dark:border-slate-700 rounded-2xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Close Telemetry"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Top 4 KPI Cards in 3D */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="glass-panel-3d p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Queries</span>
            <span className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-sky-400">
              <BarChart3 className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-slate-900 dark:text-white">
              {metrics.total_queries}
            </span>
            <span className="text-[11px] text-slate-400 block mt-0.5">Dual-mode chat inquiries</span>
          </div>
        </div>

        {/* Card 2 */}
        <div className="glass-panel-3d p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Grounding Satisfaction</span>
            <span className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <ThumbsUp className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-emerald-600 dark:text-emerald-400">
              {metrics.satisfaction_rate}%
            </span>
            <span className="text-[11px] text-slate-400 block mt-0.5">
              👍 {metrics.positive_feedback_count} Positive | 👎 {metrics.negative_feedback_count} Discrepancy
            </span>
          </div>
        </div>

        {/* Card 3 */}
        <div className="glass-panel-3d p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Indexed Repository</span>
            <span className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <BookOpen className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-slate-900 dark:text-white">
              {metrics.total_standards_indexed}
            </span>
            <span className="text-[11px] text-slate-400 block mt-0.5">
              Standards with {metrics.total_tables_indexed} Preserved Tables
            </span>
          </div>
        </div>

        {/* Card 4 */}
        <div className="glass-panel-3d p-5 rounded-3xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Conformity Audits</span>
            <span className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
              <FileCheck2 className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3">
            <span className="text-2xl sm:text-3xl font-black font-mono tracking-tight text-amber-600 dark:text-amber-400">
              {metrics.total_audits_performed}
            </span>
            <span className="text-[11px] text-slate-400 block mt-0.5">
              {metrics.audit_conformance_rate}% Batch Conformance
            </span>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Top Queried Standards & Persona Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top Queried Standards (7 cols) */}
        <div className="lg:col-span-7 bg-white dark:bg-[#111827] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
            <TrendingUp className="w-4 h-4 text-blue-600" />
            <span>Most Queried Indian Standards by Industry & Citizens</span>
          </h3>

          <div className="space-y-3">
            {metrics.top_queried_standards.map((std, idx) => {
              const maxQueries = metrics.top_queried_standards[0]?.query_count || 1;
              const barWidth = Math.min(100, Math.max(15, (std.query_count / maxQueries) * 100));

              return (
                <div key={idx} className="space-y-1 text-xs">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-blue-700 dark:text-blue-400 font-mono font-bold">
                      {std.is_code}
                    </span>
                    <span className="text-slate-500 text-[11px]">
                      {std.query_count} queries
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 dark:text-slate-400 truncate">
                    {std.title}
                  </p>
                  <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-600 to-sky-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Persona Query Split (5 cols) */}
        <div className="lg:col-span-5 bg-white dark:bg-[#111827] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Audience Persona Breakdown
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Distribution of RAG queries between manufacturing/technical engineers and consumer safety advocates.
            </p>
          </div>

          <div className="space-y-3 my-auto">
            <div>
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span className="text-blue-700 dark:text-blue-400">🏭 Industry Mode</span>
                <span className="font-mono">{industryPct}% ({metrics.industry_queries})</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 h-3 rounded-full overflow-hidden">
                <div
                  className="bg-blue-600 h-full rounded-full transition-all duration-500"
                  style={{ width: `${industryPct}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span className="text-emerald-700 dark:text-emerald-400">👥 Consumer Mode</span>
                <span className="font-mono">{consumerPct}% ({metrics.consumer_queries})</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 h-3 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-600 h-full rounded-full transition-all duration-500"
                  style={{ width: `${consumerPct}%` }}
                />
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[11px] text-slate-500">
            <span className="font-bold text-slate-700 dark:text-slate-300">Statutory Oversight Note:</span>
            <p className="mt-0.5">Dual-mode RAG prevents information asymmetry between manufacturers and consumers.</p>
          </div>
        </div>
      </div>

      {/* Recent Compliance Audits Table */}
      <div className="bg-white dark:bg-[#111827] p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
          <FileCheck2 className="w-4 h-4 text-purple-600" />
          <span>Recent Product Conformity Assessments Log</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 font-bold">
                <th className="p-3">Audit Ref</th>
                <th className="p-3">Standard</th>
                <th className="p-3">Product Name</th>
                <th className="p-3">Manufacturer</th>
                <th className="p-3">Overall Verdict</th>
                <th className="p-3">Score</th>
                <th className="p-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {metrics.recent_audits.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-6 text-slate-400">
                    No audits executed yet. Run an audit in the Compliance Audit tab.
                  </td>
                </tr>
              ) : (
                metrics.recent_audits.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/30">
                    <td className="p-3 font-mono font-bold text-blue-600 dark:text-blue-400">
                      {a.id}
                    </td>
                    <td className="p-3 font-mono font-semibold">{a.standard_is_code}</td>
                    <td className="p-3 font-medium text-slate-900 dark:text-slate-100">{a.product_name}</td>
                    <td className="p-3 text-slate-600 dark:text-slate-400">{a.manufacturer_name}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                          a.overall_verdict === 'CONFORMING'
                            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                            : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                        }`}
                      >
                        {a.overall_verdict}
                      </span>
                    </td>
                    <td className="p-3 font-mono font-bold">{a.compliance_score}%</td>
                    <td className="p-3 text-slate-500 font-mono text-[10px]">
                      {a.created_at.slice(0, 10)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Officer Security Gate Modal */}
      {showOfficerModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-950/60 text-amber-600 flex items-center justify-center font-bold">
                  <KeyRound className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Officer Clearance Gate</h3>
                  <span className="text-[10px] text-slate-500">Statutory Oversight Access</span>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowOfficerModal(false);
                  setPinInput('');
                  setPinError(null);
                }}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleVerifyOfficer} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Enter Nodal Officer PIN:
                </label>
                <input
                  type="password"
                  value={pinInput}
                  onChange={(e) => {
                    setPinInput(e.target.value);
                    setPinError(null);
                  }}
                  placeholder="PIN: 1915"
                  className="w-full px-3 py-2 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  autoFocus
                />
                {pinError && <p className="text-xs text-rose-500 mt-1 font-medium">{pinError}</p>}
                <p className="text-[11px] text-slate-400 mt-1.5">
                  Statutory Clearance PIN: <code className="font-mono text-amber-600 dark:text-amber-400 font-bold">1915</code> (National Consumer Toll-Free)
                </p>
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <button
                  type="submit"
                  className="flex-1 py-2 px-3 text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white rounded-xl shadow transition-colors"
                >
                  Verify Clearance
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setPinInput('1915');
                    setIsOfficerMode(true);
                    setShowOfficerModal(false);
                    setPinError(null);
                    addToast('success', 'Demo Officer Clearance Granted.');
                  }}
                  className="py-2 px-3 text-xs font-medium text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl transition-colors"
                >
                  Quick Bypass
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
