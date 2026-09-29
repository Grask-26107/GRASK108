import React from 'react';
import { X, BookOpen, FileText, CheckCircle2, Table, ExternalLink } from 'lucide-react';
import { Citation } from '../types';

interface CitationModalProps {
  citation: Citation | null;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-white dark:bg-[#111827] rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
              {citation.is_table ? <Table className="w-5 h-5" /> : <BookOpen className="w-5 h-5" />}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-600 text-white">
                  {citation.is_code}
                </span>
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  Page {citation.page_number}
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate max-w-md">
                {citation.title}
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-slate-800 dark:text-slate-200 text-sm leading-relaxed">
          {/* Clause Header Pill */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Normative Section / Clause Reference:
              </span>
              <p className="font-bold text-blue-700 dark:text-blue-400 text-sm mt-0.5">
                {citation.clause} {citation.table_number ? `(${citation.table_number})` : ''}
              </p>
            </div>
            <div className="text-right">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Vector Match Confidence:
              </span>
              <p className="font-mono text-sm font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(citation.similarity_score * 100)}%
              </p>
            </div>
          </div>

          {/* Extracted Grounded Excerpt */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center space-x-1.5">
              <FileText className="w-3.5 h-3.5" />
              <span>Exact Excerpt from Standard Specification:</span>
            </h4>
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 font-mono text-xs text-slate-800 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
              {citation.snippet}
            </div>
          </div>

          {/* Legal Validity Note */}
          <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 text-xs text-amber-900 dark:text-amber-300">
            <p className="font-semibold mb-0.5">Legal Notice under Section 16 of BIS Act 2016:</p>
            <p className="text-[11px] opacity-90">
              The retrieved clause constitutes the mandatory standard specification for quality compliance. Non-conforming manufacturing batches are liable to penalty under the Bureau of Indian Standards Rules.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/40">
          <span className="text-[11px] text-slate-500">
            Retrieved via ChromaDB Persistent Vector Index
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-800 dark:hover:bg-slate-700 transition-colors"
          >
            Close Excerpt
          </button>
        </div>
      </div>
    </div>
  );
};
