import React from 'react';
import { ShieldCheck, X, Check, Lock, AlertCircle, FileText } from 'lucide-react';

interface NoticeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NoticeModal: React.FC<NoticeModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-slate-950/75 backdrop-blur-md animate-fade-in">
      <div 
        className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden transform transition-all"
        role="dialog"
        aria-modal="true"
      >
        {/* Tricolor Government Portal Accent Bar */}
        <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600" />

        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-orange-50 dark:bg-orange-950/50 border border-orange-200 dark:border-orange-800 flex items-center justify-center text-orange-600 dark:text-orange-400 shadow-sm">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                Official Demonstration Notice
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                Prototype Interface & Compliance Disclosure
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="px-6 py-5 space-y-4 text-sm text-slate-600 dark:text-slate-300 max-h-[70vh] overflow-y-auto">
          <div className="p-3.5 bg-blue-50/80 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/60 rounded-2xl flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
            <p className="text-xs sm:text-sm text-blue-900 dark:text-blue-200 leading-relaxed font-medium">
              Welcome to <strong>GRASK AI</strong>. This hosted deployment showcases the interactive <strong>Frontend User Interface</strong>, offline statutory databases, and design workflows.
            </p>
          </div>

          <div className="space-y-3">
            <p className="leading-relaxed">
              While the complete <strong>Backend Architecture</strong> (FastAPI microservices, AI RAG retrieval pipeline, and verification algorithms) is fully built and tested, it is <strong>intentionally withheld from public cloud hosting</strong> due to:
            </p>

            <ul className="space-y-2.5 pl-1">
              <li className="flex items-start gap-2.5">
                <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold">
                  ✓
                </div>
                <div>
                  <strong className="text-slate-800 dark:text-slate-100">Security & Privacy Safeguards:</strong>
                  <span className="text-slate-600 dark:text-slate-300 ml-1">
                    Strict protection of core system endpoints, API infrastructure, and cryptographic verification channels.
                  </span>
                </div>
              </li>
              <li className="flex items-start gap-2.5">
                <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0 mt-0.5 text-xs font-bold">
                  ✓
                </div>
                <div>
                  <strong className="text-slate-800 dark:text-slate-100">Regulatory & Statutory Data Protection:</strong>
                  <span className="text-slate-600 dark:text-slate-300 ml-1">
                    Due to the sensitive integration of official government standards, statutory orders, and compliance data, live backend endpoints cannot be publicly deployed without explicit author consent and institutional clearance.
                  </span>
                </div>
              </li>
            </ul>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400 pt-1">
            All UI screens, navigation systems, offline directories, and client-side modules remain fully functional for demonstration and evaluation.
          </p>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 bg-slate-50 dark:bg-slate-900/80 border-t border-slate-100 dark:border-slate-800 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
          >
            <Check className="w-4 h-4" />
            <span>Understood — Proceed to Preview</span>
          </button>
        </div>
      </div>
    </div>
  );
};
