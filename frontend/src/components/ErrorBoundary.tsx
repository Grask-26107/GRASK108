import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ShieldAlert, RotateCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('GRASK AI ErrorBoundary caught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] p-6 text-center">
          <div className="p-4 rounded-3xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 max-w-lg shadow-xl animate-in zoom-in-95 duration-200">
            <div className="w-12 h-12 rounded-2xl bg-rose-600 text-white flex items-center justify-center mx-auto mb-3 shadow-md">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
              GRASK AI Safe Recovery
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 mb-4 leading-relaxed">
              A temporary interface glitch occurred while rendering. Click below to refresh and safely resume your session.
            </p>
            <button
              onClick={this.handleReset}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-700 to-indigo-700 text-white text-xs font-semibold shadow-md hover:opacity-90 active:scale-95 transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Restore GRASK AI Assistant</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
