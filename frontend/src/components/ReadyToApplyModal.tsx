import React, { useState, useEffect } from 'react';
import {
  X,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Download,
  ExternalLink,
  Building2,
  Sparkles,
  HelpCircle,
  RotateCcw,
  Check,
  TrendingUp,
  Award,
  Layers,
  Wrench,
  Search,
  Loader2
} from 'lucide-react';
import { certificateApi } from '../services/api';

interface ReadyToApplyModalProps {
  isOpen: boolean;
  onClose: () => void;
  addToast: (type: 'success' | 'error' | 'info', message: string) => void;
  initialQuery?: string;
}

export const ReadyToApplyModal: React.FC<ReadyToApplyModalProps> = ({
  isOpen,
  onClose,
  addToast,
  initialQuery = ''
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [applicantName, setApplicantName] = useState('Enterprise Applicant');
  const [turnoverTier, setTurnoverTier] = useState<'micro' | 'small_medium' | 'large'>('small_medium');
  const [hasUdyam, setHasUdyam] = useState(true);
  const [checkedDocs, setCheckedDocs] = useState<string[]>(['doc_identity_pan', 'doc_factory_address']);
  
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [popularProducts, setPopularProducts] = useState<any[]>([]);
  const [assessment, setAssessment] = useState<any | null>(null);
  const [activeTab, setActiveTab] = useState<'checklist' | 'equipment' | 'fees'>('checklist');

  // Load popular products on open
  useEffect(() => {
    if (isOpen) {
      certificateApi.getPopular()
        .then((res) => {
          if (res.success) {
            setPopularProducts(res.popular_products);
          }
        })
        .catch(() => {});
    }
  }, [isOpen]);

  // Trigger assessment when initialQuery changes or user submits
  useEffect(() => {
    if (isOpen && initialQuery) {
      setQuery(initialQuery);
      handleAssess(initialQuery, turnoverTier, hasUdyam, checkedDocs);
    }
  }, [isOpen, initialQuery]);

  const handleAssess = async (
    targetQuery?: string,
    tier = turnoverTier,
    udyam = hasUdyam,
    docs = checkedDocs
  ) => {
    const q = (targetQuery !== undefined ? targetQuery : query).trim();
    if (!q) {
      addToast('error', 'Please enter a product or business category.');
      return;
    }

    setLoading(true);
    try {
      const res = await certificateApi.assessReadiness(q, tier, udyam, docs);
      if (res.success) {
        setAssessment(res);
      } else {
        setAssessment(null);
        addToast('error', res.message || 'Could not recognize product category.');
      }
    } catch (err: any) {
      addToast('error', 'Failed to assess statutory readiness.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleDoc = (docId: string) => {
    const updated = checkedDocs.includes(docId)
      ? checkedDocs.filter((id) => id !== docId)
      : [...checkedDocs, docId];
    
    setCheckedDocs(updated);
    if (query) {
      handleAssess(query, turnoverTier, hasUdyam, updated);
    }
  };

  const handleSelectAll = (select: boolean) => {
    if (!assessment) return;
    const allIds = assessment.prerequisites_checklist.map((p: any) => p.id);
    const updated = select ? allIds : [];
    setCheckedDocs(updated);
    handleAssess(query, turnoverTier, hasUdyam, updated);
  };

  const handleDownloadDossier = async () => {
    if (!assessment) return;
    setDownloading(true);
    addToast('info', 'Compiling and sealing your official statutory dossier...');

    try {
      const blob = await certificateApi.downloadDossier(assessment, applicantName);
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `GRASK_Dossier_${assessment.product.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      addToast('success', 'Statutory application dossier downloaded successfully!');
    } catch (err) {
      addToast('error', 'Could not generate application dossier.');
    } finally {
      setDownloading(false);
    }
  };

  const handleReset = () => {
    setAssessment(null);
    setQuery('');
    setApplicantName('Enterprise Applicant');
    setCheckedDocs(['doc_identity_pan', 'doc_factory_address']);
    addToast('info', 'Reset complete. Enter any new product or industry.');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="relative w-full max-w-4xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col max-h-[92vh] overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-linear-to-r from-blue-50/70 via-indigo-50/40 to-white dark:from-slate-900 dark:via-blue-950/20 dark:to-slate-900 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-linear-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                  Ready to Apply — Statutory Certificate Studio
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                  SIH26107
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Automated eligibility check, document gap analysis, 50% MSME fee savings & 1-click official dossier
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {(assessment || query) && (
              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/50 dark:hover:bg-amber-900/60 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-800 transition-all shadow-xs"
                title="Reset search and check another product"
              >
                <RotateCcw className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                <span>Reset / New Search</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Section 1: Business Details & Search Bar */}
          <div className="bg-slate-50 dark:bg-slate-800/40 rounded-xl p-4 border border-slate-200 dark:border-slate-850 space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAssess()}
                  placeholder="Enter product or business (e.g. Packaged Water, TMT Sariya, Helmets, LED Bulb, Bakery)..."
                  className="w-full pl-9 pr-4 py-2.5 rounded-xl text-sm bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-2xs"
                />
              </div>
              <button
                onClick={() => handleAssess()}
                disabled={loading || !query.trim()}
                className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-xs flex items-center justify-center space-x-2 transition-colors disabled:opacity-50 shrink-0"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                <span>Check Eligibility</span>
              </button>
            </div>

            {/* Popular Suggestion Chips */}
            {popularProducts.length > 0 && !assessment && (
              <div className="space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Popular Regulated Industries:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {popularProducts.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => {
                        setQuery(p.title);
                        handleAssess(p.title);
                      }}
                      className="px-2.5 py-1 rounded-lg text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-750 text-slate-700 dark:text-slate-300 hover:border-blue-400 hover:text-blue-600 transition-colors shadow-2xs flex items-center space-x-1.5"
                    >
                      <span>{p.title}</span>
                      <span className="text-[10px] text-blue-500 font-mono">({p.is_code})</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Business Scale & MSME Sizing */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              {/* Turnover Cards */}
              <div className="sm:col-span-2 space-y-1.5">
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Annual Turnover Tier (Determines License Scheme):
                </span>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'micro', label: 'Micro Enterprise', sub: '< ₹12 Lakhs / yr' },
                    { id: 'small_medium', label: 'Small / Medium', sub: '₹12L to ₹20 Cr' },
                    { id: 'large', label: 'Large Enterprise', sub: '> ₹20 Crores / yr' },
                  ].map((tier) => (
                    <button
                      key={tier.id}
                      type="button"
                      onClick={() => {
                        setTurnoverTier(tier.id as any);
                        if (query) handleAssess(query, tier.id as any, hasUdyam);
                      }}
                      className={`p-2 rounded-xl text-left border transition-all text-xs ${
                        turnoverTier === tier.id
                          ? 'border-blue-600 bg-blue-50/60 dark:bg-blue-950/40 text-blue-900 dark:text-blue-200 ring-1 ring-blue-500'
                          : 'border-slate-200 dark:border-slate-750 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      <div className="font-semibold">{tier.label}</div>
                      <div className="text-[10px] text-slate-500 dark:text-slate-400">{tier.sub}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Udyam MSME Toggle */}
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                  Udyam MSME Registered?
                </span>
                <button
                  type="button"
                  onClick={() => {
                    const next = !hasUdyam;
                    setHasUdyam(next);
                    if (query) handleAssess(query, turnoverTier, next);
                  }}
                  className={`w-full p-2 rounded-xl border text-xs text-left transition-all flex items-center justify-between ${
                    hasUdyam
                      ? 'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 ring-1 ring-emerald-500'
                      : 'border-amber-300 bg-amber-50/50 dark:bg-amber-950/30 text-amber-900 dark:text-amber-200'
                  }`}
                >
                  <div>
                    <div className="font-semibold flex items-center space-x-1">
                      <span>{hasUdyam ? 'Yes (50% Off BIS)' : 'No (Standard Fees)'}</span>
                    </div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400">
                      {hasUdyam ? 'Concession active' : 'Click to toggle'}
                    </div>
                  </div>
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-white ${hasUdyam ? 'bg-emerald-600' : 'bg-slate-300'}`}>
                    <Check className="w-3 h-3" />
                  </div>
                </button>
              </div>
            </div>
          </div>

          {/* Section 2: Assessment Results */}
          {assessment && (
            <div className="space-y-5 animate-in fade-in duration-200">
              
              {/* Product Header & Readiness Score Gauge */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* Product Profile Banner */}
                <div className="md:col-span-2 p-4 rounded-xl bg-linear-to-br from-slate-900 to-blue-950 text-white shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-center space-x-2 text-blue-300 text-xs font-semibold mb-1">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      <span>OFFICIAL STATUTORY STANDARD PROFILE</span>
                    </div>
                    <h3 className="text-base font-bold text-white mb-0.5">
                      {assessment.product.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-2 mt-2">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-blue-500/30 border border-blue-400/40 text-blue-200">
                        {assessment.product.is_code}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-xs bg-slate-800/80 text-slate-300 border border-slate-700">
                        {assessment.product.department}
                      </span>
                      {assessment.product.mandatory_qco && (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/20 text-red-300 border border-red-500/30">
                          Mandatory QCO (100% Law)
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-3 border-t border-slate-800/80 text-xs text-slate-300 flex items-center justify-between">
                    <span>Applicable Certificates: <b>{assessment.certificates.length}</b></span>
                    <span className="text-emerald-400 font-semibold">{assessment.financials.msme_savings_message}</span>
                  </div>
                </div>

                {/* Readiness Gauge Card */}
                <div className={`p-4 rounded-xl border flex flex-col items-center justify-center text-center shadow-xs ${
                  assessment.readiness_score >= 90
                    ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800/60'
                    : assessment.readiness_score >= 60
                    ? 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800/60'
                    : 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800/60'
                }`}>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">
                    Application Readiness
                  </span>
                  
                  <div className="text-4xl font-extrabold my-1 font-mono tracking-tight" style={{
                    color: assessment.readiness_score >= 90 ? '#15803d' : assessment.readiness_score >= 60 ? '#d97706' : '#b91c1c'
                  }}>
                    {assessment.readiness_score}%
                  </div>

                  <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold uppercase ${
                    assessment.readiness_score >= 90
                      ? 'bg-emerald-200 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200'
                      : assessment.readiness_score >= 60
                      ? 'bg-amber-200 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200'
                      : 'bg-red-200 dark:bg-red-900/60 text-red-800 dark:text-red-200'
                  }`}>
                    {assessment.status.replace(/_/g, ' ')}
                  </span>
                  
                  <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-2 px-2 leading-tight">
                    {assessment.readiness_score >= 90 ? 'Ready to submit on Manakonline' : 'Complete missing lab tools before fee payment'}
                  </p>
                </div>
              </div>

              {/* Critical Blockers Alert (If Any) */}
              {assessment.critical_blockers_missing && assessment.critical_blockers_missing.length > 0 && (
                <div className="p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-850 flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
                  <div className="space-y-1 text-xs">
                    <span className="font-bold text-red-900 dark:text-red-200">
                      Mandatory Factory Inspection Blockers Detected ({assessment.critical_blockers_missing.length})
                    </span>
                    <ul className="list-disc list-inside space-y-0.5 text-red-700 dark:text-red-300">
                      {assessment.critical_blockers_missing.map((b: any, idx: number) => (
                        <li key={idx}>
                          <b>{b.document}:</b> {b.reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Navigation Tabs */}
              <div className="border-b border-slate-200 dark:border-slate-800 flex space-x-4">
                {[
                  { id: 'checklist', label: 'Prerequisites Checklist', icon: CheckCircle2, count: assessment.prerequisites_checklist.length },
                  { id: 'equipment', label: 'Factory Lab Equipment', icon: Wrench, count: assessment.product.inhouse_lab_equipment?.length || 0 },
                  { id: 'fees', label: 'Statutory Fee Calculator', icon: TrendingUp, count: assessment.certificates.length }
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`pb-2.5 text-xs font-semibold flex items-center space-x-1.5 border-b-2 transition-colors ${
                        activeTab === tab.id
                          ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                          : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{tab.label}</span>
                      <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                        {tab.count}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Tab 1: Prerequisites Checklist */}
              {activeTab === 'checklist' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Check documents you already have to recalculate readiness score:</span>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleSelectAll(true)}
                        className="text-blue-600 hover:underline font-semibold"
                      >
                        Select All
                      </button>
                      <span>•</span>
                      <button
                        onClick={() => handleSelectAll(false)}
                        className="text-slate-500 hover:underline"
                      >
                        Clear All
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {assessment.prerequisites_checklist.map((p: any) => {
                      const isChecked = checkedDocs.includes(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => handleToggleDoc(p.id)}
                          className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-start space-x-3 select-none ${
                            isChecked
                              ? 'bg-blue-50/50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800 text-slate-900 dark:text-white'
                              : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                          }`}
                        >
                          <div className={`w-4 h-4 rounded-md mt-0.5 flex items-center justify-center shrink-0 border transition-colors ${
                            isChecked
                              ? 'bg-blue-600 border-blue-600 text-white'
                              : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800'
                          }`}>
                            {isChecked && <Check className="w-3 h-3 stroke-3" />}
                          </div>

                          <div className="flex-1 space-y-0.5">
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-slate-800 dark:text-slate-200">
                                {p.name}
                              </span>
                              {p.is_critical_blocker && (
                                <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-300">
                                  Critical
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                              {p.description}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Tab 2: Factory Lab Equipment */}
              {activeTab === 'equipment' && (
                <div className="space-y-3">
                  <div className="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-xs text-blue-800 dark:text-blue-300">
                    <span className="font-bold">BIS In-House Quality Assurance Clause:</span> Under {assessment.product.is_code}, your manufacturing premises must have the following calibrated testing instruments physically installed before the visiting BIS inspecting officer arrives.
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {assessment.product.inhouse_lab_equipment?.map((tool: string, idx: number) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-xs flex items-center space-x-2">
                        <Wrench className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                        <span className="text-slate-800 dark:text-slate-200 font-medium">{tool}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 3: Statutory Fee Calculator */}
              {activeTab === 'fees' && (
                <div className="space-y-4">
                  <div className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold border-b border-slate-200 dark:border-slate-700">
                        <tr>
                          <th className="p-2.5">Certificate / Authority</th>
                          <th className="p-2.5">Statutory Form</th>
                          <th className="p-2.5">Official Portal</th>
                          <th className="p-2.5 text-right">Standard Fee</th>
                          <th className="p-2.5 text-right">MSME Discount</th>
                          <th className="p-2.5 text-right font-bold">Net Fee</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                        {assessment.certificates.map((c: any) => (
                          <tr key={c.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-850/50">
                            <td className="p-2.5 font-semibold text-slate-800 dark:text-slate-200">
                              <div>{c.name}</div>
                              <div className="text-[10px] text-slate-400 font-normal">{c.authority}</div>
                            </td>
                            <td className="p-2.5 font-mono text-[11px] text-slate-600 dark:text-slate-400">
                              {c.statutory_form}
                            </td>
                            <td className="p-2.5">
                              <a
                                href={c.portal_url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-blue-600 hover:underline flex items-center space-x-1"
                              >
                                <span>{c.portal_name}</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </td>
                            <td className="p-2.5 text-right text-slate-500">
                              ₹{c.base_fee.toLocaleString()}
                            </td>
                            <td className="p-2.5 text-right text-emerald-600 font-medium">
                              -₹{c.concession_applied.toLocaleString()}
                            </td>
                            <td className="p-2.5 text-right font-bold text-slate-900 dark:text-white">
                              ₹{c.net_fee.toLocaleString()}
                            </td>
                          </tr>
                        ))}
                        {/* Totals */}
                        <tr className="bg-slate-50 dark:bg-slate-800/80 font-bold border-t-2 border-slate-300 dark:border-slate-700">
                          <td className="p-2.5" colSpan={3}>TOTAL STATUTORY PAYABLE</td>
                          <td className="p-2.5 text-right text-slate-600 dark:text-slate-300">
                            ₹{assessment.financials.gross_statutory_fee.toLocaleString()}
                          </td>
                          <td className="p-2.5 text-right text-emerald-600">
                            -₹{assessment.financials.concessions_unlocked.toLocaleString()}
                          </td>
                          <td className="p-2.5 text-right text-blue-600 dark:text-blue-400 text-sm">
                            ₹{assessment.financials.net_payable_fee.toLocaleString()}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Section 3: Official Actions Bar */}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="text-xs text-slate-500 flex items-center space-x-2">
                  <span className="font-semibold text-slate-700 dark:text-slate-300">Applicant:</span>
                  <input
                    type="text"
                    value={applicantName}
                    onChange={(e) => setApplicantName(e.target.value)}
                    placeholder="Enterprise Name"
                    className="px-2 py-1 rounded-md text-xs bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200 focus:outline-none"
                  />
                </div>

                <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
                  <button
                    onClick={handleDownloadDossier}
                    disabled={downloading}
                    className="w-full sm:w-auto px-5 py-2.5 rounded-xl font-bold text-xs bg-emerald-600 hover:bg-emerald-700 text-white shadow-md flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
                  >
                    {downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                    <span>Download Application Dossier (PDF)</span>
                  </button>
                </div>
              </div>

            </div>
          )}

        </div>

      </div>
    </div>
  );
};
