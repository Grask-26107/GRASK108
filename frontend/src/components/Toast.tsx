import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  removeToast: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, removeToast }) => {
  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col space-y-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
};

const ToastItem: React.FC<{ toast: ToastMessage; onClose: () => void }> = ({ toast, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />,
    error: <AlertCircle className="w-4 h-4 text-rose-500 flex-shrink-0" />,
    info: <Info className="w-4 h-4 text-sky-500 flex-shrink-0" />,
  };

  const bgStyles = {
    success: 'bg-white dark:bg-slate-900 border-emerald-500/40 text-slate-800 dark:text-slate-100',
    error: 'bg-white dark:bg-slate-900 border-rose-500/40 text-slate-800 dark:text-slate-100',
    info: 'bg-white dark:bg-slate-900 border-sky-500/40 text-slate-800 dark:text-slate-100',
  };

  return (
    <div
      className={`flex items-center justify-between p-3.5 rounded-xl shadow-lg border text-xs animate-in slide-in-from-bottom-2 ${
        bgStyles[toast.type]
      }`}
    >
      <div className="flex items-center space-x-2.5">
        {icons[toast.type]}
        <span className="font-medium">{toast.message}</span>
      </div>
      <button
        onClick={onClose}
        className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
