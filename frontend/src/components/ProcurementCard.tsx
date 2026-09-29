import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  FileText,
  Layers,
  Copy,
  Check,
  Download,
  FileSpreadsheet,
  ShieldAlert,
  Info,
  Clock,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { procurementApi } from '../services/api';

interface ProcurementCardProps {
  recommendation?: any;
  isTenderUpload?: boolean;
  tenderItems?: any[];
  tenderFileName?: string;
  addToast?: (type: 'success' | 'error' | 'info', message: string) => void;
}

export const ProcurementCard: React.FC<ProcurementCardProps> = ({
  recommendation,
  isTenderUpload,
  tenderItems,
  tenderFileName,
  addToast
}) => {
  const [copiedClause, setCopiedClause] = useState(false);
  const [activeAlliedTab, setActiveAlliedTab] = useState<
    'test_methods' | 'normative_references' | 'safety_standards' | 'installation_standards' | 'terminology_standards' | 'related_product_standards'
  >('test_methods');
  const [isAlliedExpanded, setIsAlliedExpanded] = useState(true);

  const handleCopyClause = (clauseText: string) => {
    navigator.clipboard.writeText(clauseText);
    setCopiedClause(true);
    addToast?.('success', 'Official GeM tender clause copied to clipboard!');
    setTimeout(() => setCopiedClause(false), 2500);
  };

  const handleExportJson = (data: any) => {
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(data, null, 2))}`;
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', jsonString);
    downloadAnchor.setAttribute('download', `Tender_Spec_${data.primary_standard?.code || 'IS'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    addToast?.('success', 'Tender specification JSON dossier downloaded!');
  };

  const handleExportGemBoq = async (itemsToExport: any[]) => {
    try {
      const res = await procurementApi.exportGemBoq(itemsToExport);
      if (res.success && res.csv_data) {
        const blob = new Blob([res.csv_data], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', res.filename || 'gem_boq_procurement_schedule.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
        addToast?.('success', 'GeM BoQ Schedule exported successfully as CSV!');
      } else {
        addToast?.('error', res.error || 'Failed to export GeM BoQ CSV');
      }
    } catch (e) {
      console.error('Failed to export BoQ CSV', e);
      addToast?.('error', 'Network error exporting GeM BoQ CSV');
    }
  };

  // Case 1: Batch Tender Upload Items View
  if (isTenderUpload && tenderItems && tenderItems.length > 0) {
    return (
      <div className="mt-3 bg-slate-900/90 border border-indigo-500/40 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4 text-slate-100">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                SIH26108 • Multi-Item Tender Parser
              </span>
              <span className="text-xs text-slate-400">
                Source: <span className="text-slate-200 font-mono">{tenderFileName || 'Document'}</span>
              </span>
            </div>
            <h4 className="text-base font-bold text-white mt-1">
              Extracted Line Items & Recommended Indian Standards ({tenderItems.length})
            </h4>
          </div>

          <button
            onClick={() => handleExportGemBoq(tenderItems)}
            className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl flex items-center gap-1.5 shadow-md shadow-emerald-600/20 transition-all active:scale-[0.98]"
          >
            <FileSpreadsheet className="w-4 h-4" />
            Export Complete GeM BoQ (CSV)
          </button>
        </div>

        {/* Items Table / Cards */}
        <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar pr-1">
          {tenderItems.map((item, idx) => {
            const rec = item.recommendation;
            const primary = rec?.primary_standard;
            const isMandatory = rec?.mandatory_certification?.is_mandatory;
            return (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 transition-all space-y-2"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="flex items-start gap-2.5">
                    <span className="w-5 h-5 rounded-full bg-indigo-900/60 border border-indigo-500/40 text-indigo-300 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <div>
                      <p className="text-xs font-semibold text-white">
                        {item.tender_item_description}
                      </p>
                      {primary && (
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          {primary.title}
                        </p>
                      )}
                    </div>
                  </div>

                  {primary ? (
                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded">
                        {primary.code}
                      </span>
                      {isMandatory && (
                        <span className="px-1.5 py-0.5 text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded">
                          QCO Mandatory
                        </span>
                      )}
                    </div>
                  ) : (
                    <span className="text-xs text-amber-400">Manual review recommended</span>
                  )}
                </div>

                {rec?.gem_tender_clause && (
                  <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px]">
                    <span className="text-slate-400 truncate max-w-md font-mono text-[10px]">
                      {rec.gem_tender_clause.slice(0, 100)}...
                    </span>
                    <button
                      onClick={() => handleCopyClause(rec.gem_tender_clause)}
                      className="px-2 py-0.5 text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-200 rounded flex items-center gap-1 shrink-0"
                    >
                      <Copy className="w-3 h-3" />
                      Copy Clause
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Case 2: Single Product / Specification Recommendation Card
  if (!recommendation || !recommendation.match_found) return null;

  const primary = recommendation.primary_standard;
  const mandatory = recommendation.mandatory_certification;
  const allied = recommendation.allied_standards || {};

  return (
    <div className="mt-3 bg-slate-900 border border-indigo-500/40 rounded-2xl p-4 sm:p-5 shadow-2xl space-y-4 text-slate-100">
      
      {/* Top Header Card */}
      <div className="flex flex-wrap items-start justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {recommendation.confidence_score || 95}% Semantic Confidence Match
            </span>

            {/* Compliance Badge */}
            {recommendation.obsolete_warning ? (
              <span className="px-2.5 py-0.5 text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-full flex items-center gap-1">
                🔴 Obsolete Standard Cited
              </span>
            ) : recommendation.foreign_standard_notice ? (
              <span className="px-2.5 py-0.5 text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-full flex items-center gap-1">
                🟡 Foreign Standard Harmonized
              </span>
            ) : (
              <span className="px-2.5 py-0.5 text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full flex items-center gap-1">
                🟢 100% GFR 144 & QCO Compliant
              </span>
            )}

            {recommendation.security_flag && (
              <span className="px-2.5 py-0.5 text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-full flex items-center gap-1">
                🛡️ Query Shielded
              </span>
            )}

            {primary?.category && (
              <span className="px-2 py-0.5 text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-full">
                {primary.category}
              </span>
            )}
          </div>

          {recommendation.security_flag && recommendation.security_notice && (
            <div className="mb-2 p-2 bg-amber-950/40 border border-amber-500/30 rounded-lg text-xs text-amber-200 flex items-center gap-2">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span>{recommendation.security_notice}</span>
            </div>
          )}

          <h3 className="text-xl sm:text-2xl font-black text-white flex flex-wrap items-center gap-2">
            {primary.code}
            {primary.latest_edition && (
              <span className="text-xs px-2 py-0.5 font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md">
                {primary.latest_edition}
              </span>
            )}
          </h3>

          <p className="text-xs sm:text-sm text-slate-300 mt-1 font-medium leading-relaxed">
            {primary.title}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExportGemBoq([{
              tender_item_description: primary.title,
              recommendation: recommendation
            }])}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg border border-emerald-500/60 flex items-center gap-1.5 transition-all shadow-sm"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export</span> GeM BoQ
          </button>
          <button
            onClick={() => handleExportJson(recommendation)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">JSON</span>
          </button>
        </div>
      </div>

      {/* Obsolete Warning Banner */}
      {recommendation.obsolete_warning && (
        <div className="p-3 bg-rose-500/15 border border-rose-500/40 rounded-xl flex items-start gap-2.5 text-rose-200 text-xs">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Obsolete Standard Warning: </span>
            {recommendation.obsolete_warning.warning} {recommendation.obsolete_warning.recommendation}
          </div>
        </div>
      )}

      {/* Foreign Standard Equivalence Notice Banner */}
      {recommendation.foreign_standard_notice && (
        <div className="p-3 bg-blue-500/15 border border-blue-500/40 rounded-xl flex items-start gap-2.5 text-blue-200 text-xs">
          <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-blue-300">
              Foreign Standard Harmonized ({recommendation.foreign_standard_notice.foreign_standard_detected}):
            </span>
            <p className="mt-0.5 text-slate-200">
              {recommendation.foreign_standard_notice.statutory_advice}
            </p>
          </div>
        </div>
      )}

      {/* Active Amendments Pill Bar */}
      {primary?.active_amendments && primary.active_amendments.length > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 text-xs bg-slate-950/50 p-2.5 rounded-xl border border-slate-800/80">
          <span className="text-slate-400 font-semibold flex items-center gap-1 text-[11px]">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            Active Amendments ({primary.total_amendments || primary.active_amendments.length}):
          </span>
          {primary.active_amendments.map((amd: any, i: number) => (
            <span
              key={i}
              title={amd.scope || `Amendment ${amd.number}`}
              className="px-2 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-200 text-[10px] font-mono"
            >
              Amd {amd.number} ({amd.year})
            </span>
          ))}
        </div>
      )}

      {/* Mandatory Certification (QCO) Alert Box */}
      {mandatory?.is_mandatory && (
        <div className="bg-amber-950/30 border border-amber-500/40 rounded-xl p-3.5 sm:p-4 flex items-start gap-3 text-slate-200">
          <div className="p-2 bg-amber-500/20 border border-amber-500/30 rounded-lg text-amber-400 shrink-0 mt-0.5">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-black text-amber-400 uppercase tracking-wider">
                Statutory Requirement:
              </span>
              <span className="px-2 py-0.5 text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded">
                {mandatory.scheme || 'BIS Certification'}
              </span>
              {mandatory.issuing_ministry && (
                <span className="text-xs text-slate-300 font-medium">
                  Issued by: {mandatory.issuing_ministry}
                </span>
              )}
            </div>
            {mandatory.qco_order && (
              <p className="text-xs text-amber-100 font-semibold">
                {mandatory.qco_order} ({mandatory.statutory_act || 'BIS Act, 2016'})
              </p>
            )}
            <p className="text-xs text-slate-300 leading-relaxed">
              {mandatory.tender_warning}
            </p>
          </div>
        </div>
      )}

      {/* Allied Standards Taxonomy Section */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 sm:p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            <h4 className="text-xs sm:text-sm font-bold text-white">
              Allied Standards Taxonomy
            </h4>
          </div>
          <button
            onClick={() => setIsAlliedExpanded(!isAlliedExpanded)}
            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            {isAlliedExpanded ? 'Collapse' : 'Expand'}
            {isAlliedExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {isAlliedExpanded && (
          <div className="space-y-3">
            {/* Allied Category Selector Pills */}
            <div className="flex flex-wrap gap-1.5 border-b border-slate-800/80 pb-2.5">
              {[
                { id: 'test_methods', label: '🔬 Test Methods', count: allied.test_methods?.length || 0 },
                { id: 'normative_references', label: '📐 Normative References', count: allied.normative_references?.length || 0 },
                { id: 'safety_standards', label: '🛡️ Safety Standards', count: allied.safety_standards?.length || 0 },
                { id: 'installation_standards', label: '🏗️ Installation / Practice', count: allied.installation_standards?.length || 0 },
                { id: 'terminology_standards', label: '📖 Terminology', count: allied.terminology_standards?.length || 0 },
                { id: 'related_product_standards', label: '📦 Related Products', count: allied.related_product_standards?.length || 0 },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveAlliedTab(tab.id as any)}
                  className={`px-2.5 py-1 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
                    activeAlliedTab === tab.id
                      ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                      : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                  }`}
                >
                  <span>{tab.label}</span>
                  <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${
                    activeAlliedTab === tab.id ? 'bg-indigo-800 text-indigo-100' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {tab.count}
                  </span>
                </button>
              ))}
            </div>

            {/* Active Allied Standards Content */}
            <div className="space-y-1.5 max-h-48 overflow-y-auto custom-scrollbar">
              {(allied[activeAlliedTab] || []).length > 0 ? (
                (allied[activeAlliedTab] || []).map((item: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-2.5 bg-slate-900 border border-slate-800/80 rounded-lg flex flex-wrap items-center justify-between gap-2 hover:border-slate-700 transition-colors text-xs"
                  >
                    <div>
                      <span className="font-bold text-indigo-400 font-mono">
                        {item.code}
                      </span>
                      <p className="text-slate-200 font-medium mt-0.5">
                        {item.title}
                      </p>
                      {item.role && (
                        <p className="text-[11px] text-slate-400">
                          Role: {item.role}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {item.clause && (
                        <span className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-300 rounded font-mono">
                          {item.clause}
                        </span>
                      )}
                      {item.nabl_required && (
                        <span className="px-2 py-0.5 text-[10px] bg-red-500/20 text-red-300 border border-red-500/30 rounded font-semibold">
                          NABL Lab Test Required
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 py-2 italic text-center">
                  No specific standards listed under this category for {primary.code}.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Official GeM Tender Clause Box */}
      {recommendation.gem_tender_clause && (
        <div className="bg-slate-950 border border-indigo-500/40 rounded-xl p-3.5 sm:p-4 space-y-2.5 shadow-lg shadow-indigo-950/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              <h4 className="text-xs sm:text-sm font-bold text-white">
                Official GeM Tender Specification Clause (Ready to Paste)
              </h4>
            </div>
            <button
              onClick={() => handleCopyClause(recommendation.gem_tender_clause)}
              className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/30 active:scale-95"
            >
              {copiedClause ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-300" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  Copy GeM Clause
                </>
              )}
            </button>
          </div>
          <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono text-slate-300 leading-relaxed select-all">
            {recommendation.gem_tender_clause}
          </div>
        </div>
      )}

    </div>
  );
};

export default ProcurementCard;
