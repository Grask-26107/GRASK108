import React, { useState } from 'react';
import {
  Lock,
  Mail,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  Sun,
  Moon,
  Building2,
  FileCheck2,
  Globe2,
  Layers,
  Award
} from 'lucide-react';
import { UserProfile } from '../types';

interface LoginPageProps {
  onLogin: (user: UserProfile) => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLogin,
  darkMode,
  onToggleDarkMode,
}) => {
  const [identifier, setIdentifier] = useState('officer.sharma@gov.in');
  const [password, setPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim()) {
      setErrorMessage('Please enter your email, mobile number, or employee ID.');
      return;
    }

    setIsLoading(true);
    setErrorMessage('');

    setTimeout(() => {
      // Create user profile - standard user, role can be updated after login in profile
      const newUser: UserProfile = {
        id: `usr_${Date.now()}`,
        name: identifier.includes('@') ? identifier.split('@')[0].replace('.', ' ') : 'Verified User',
        email: identifier.includes('@') ? identifier : `${identifier}@grask.gov.in`,
        role: 'industry', // Default initial role, user can update freely in profile
        organization: 'National Standards & Industry Portal',
        mobile: '+91 98765 43210',
        designation: 'Standard User',
        isGuest: false,
        createdAt: new Date().toISOString(),
      };

      setIsLoading(false);
      onLogin(newUser);
    }, 400);
  };

  const handleDemoLogin = () => {
    setIsLoading(true);
    setErrorMessage('');

    setTimeout(() => {
      const demoUser: UserProfile = {
        id: 'usr_demo_evaluator',
        name: 'Evaluation Officer',
        email: 'evaluator.sih@gov.in',
        role: 'industry',
        organization: 'Smart India Hackathon 2026',
        mobile: '+91 98765 00000',
        designation: 'Technical Jury Member',
        isGuest: false,
        createdAt: new Date().toISOString(),
      };

      setIsLoading(false);
      onLogin(demoUser);
    }, 300);
  };

  const handleGuestLogin = () => {
    const guestUser: UserProfile = {
      id: `guest_${Date.now()}`,
      name: 'Guest Citizen',
      email: 'guest@citizen.in',
      role: 'citizen',
      organization: 'Public Access',
      isGuest: true,
      createdAt: new Date().toISOString(),
    };
    onLogin(guestUser);
  };

  return (
    <div className="min-h-screen w-screen flex flex-col justify-between bg-slate-50 dark:bg-slate-950 font-sans antialiased text-slate-900 dark:text-slate-100 transition-colors">
      {/* Top Statutory Accent Stripe */}
      <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600 shrink-0" />

      {/* Navigation / Header Bar */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/70 backdrop-blur-md sticky top-0 z-20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-700 via-blue-600 to-indigo-900 border border-amber-400/40 flex items-center justify-center text-white shadow-md p-1.5 shrink-0">
            <img src="/bis-emblem.svg" alt="Emblem" className="w-7 h-7 drop-shadow" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-extrabold text-base sm:text-lg tracking-tight text-slate-900 dark:text-white leading-none">
                BIS Tender Standards Engine
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-600 text-white rounded-full">
                SIH26108
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              AI Recommendation Engine for GeM & CPPP Public Procurement Tenders
            </p>
          </div>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={onToggleDarkMode}
          className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition-colors flex items-center space-x-1.5 text-xs font-semibold"
          title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {darkMode ? (
            <Sun className="w-4 h-4 text-amber-500" />
          ) : (
            <Moon className="w-4 h-4 text-indigo-600" />
          )}
          <span className="hidden sm:inline">{darkMode ? 'Light' : 'Dark'}</span>
        </button>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Column: Brand & Feature Highlights Focused on SIH26108 */}
          <div className="lg:col-span-6 space-y-6 text-left">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-100/80 dark:bg-indigo-950/60 border border-indigo-300 dark:border-indigo-800 text-indigo-800 dark:text-indigo-300 text-xs font-bold">
              <Award className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>Smart India Hackathon 2026 • SIH26108</span>
            </div>

            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
              AI Recommendation Engine for <br />
              <span className="bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-800 bg-clip-text text-transparent">
                GeM Procurement & Tenders
              </span>
            </h2>

            <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
              Helping government buyers find mandatory <strong>Indian Standards (BIS codes)</strong>, check <strong>Quality Control Orders (QCOs)</strong>, and write ready-to-use tender clauses for GeM and CPPP tenders.
            </p>

            {/* Feature Pills */}
            <div className="space-y-3 pt-2">
              <div className="flex items-start space-x-3 p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 shadow-xs">
                <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border border-indigo-200/60 dark:border-indigo-800/60 shrink-0">
                  <FileCheck2 className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white">1-Click GeM Tender Clause Generator</h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">Creates ready-to-use tender clauses with the exact Indian Standards required by rules.</p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 shadow-xs">
                <div className="p-2 rounded-lg bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 border border-rose-200/60 dark:border-rose-800/60 shrink-0">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white">Mandatory Quality Rule Checker</h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">Checks Quality Control Orders (QCO) to prevent buying non-compliant or illegal goods.</p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 shadow-xs">
                <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60 shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white">Extra Feature: Supplier & Lab Verification</h3>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">Check winning supplier licenses, lab test certificates, and factory readiness before awarding contracts.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Unified Login Card */}
          <div className="lg:col-span-6 w-full max-w-md mx-auto">
            <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 shadow-xl border border-slate-200 dark:border-slate-800 relative overflow-hidden">
              
              {/* Subtle Card Accent */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-blue-500 to-indigo-600" />

              <div className="mb-6 text-left">
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
                  Sign In
                </h3>
                <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Enter your credentials to access your consultation workspace.
                </p>
              </div>

              {/* Error Message if any */}
              {errorMessage && (
                <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs">
                  {errorMessage}
                </div>
              )}

              {/* Login Form */}
              <form onSubmit={handleSignIn} className="space-y-4 text-left">
                {/* Identifier Input */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                    Email, Mobile, or Parichay ID
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="text"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      placeholder="name@example.gov.in"
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    />
                  </div>
                </div>

                {/* Password Input */}
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Remember Me & Note */}
                <div className="flex items-center justify-between text-xs pt-1">
                  <label className="flex items-center space-x-2 text-slate-600 dark:text-slate-400 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5"
                    />
                    <span>Remember this session</span>
                  </label>
                  <span className="text-[11px] text-slate-400 dark:text-slate-500">
                    Role selectable in profile
                  </span>
                </div>

                {/* Primary Sign In Button */}
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-md hover:shadow-indigo-500/20 transition-all flex items-center justify-center space-x-2 disabled:opacity-70 cursor-pointer"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>Sign In</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {/* Hackathon Quick Evaluation Divider */}
              <div className="relative my-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200 dark:border-slate-800" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-white dark:bg-slate-900 text-slate-400">
                    Quick Access
                  </span>
                </div>
              </div>

              {/* Fast 1-Click Demo Sign In */}
              <button
                type="button"
                onClick={handleDemoLogin}
                disabled={isLoading}
                className="w-full py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-indigo-50 dark:bg-slate-800 dark:hover:bg-indigo-950/40 text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-300 font-semibold text-xs border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-500/40 transition-all flex items-center justify-center space-x-2 mb-3 cursor-pointer"
              >
                <Sparkles className="w-4 h-4 text-amber-500" />
                <span>⚡ 1-Click Demo Sign In (Evaluators)</span>
              </button>

              {/* Continue as Guest */}
              <button
                type="button"
                onClick={handleGuestLogin}
                className="w-full text-center text-xs text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 transition-colors py-1 cursor-pointer font-medium"
              >
                Or Continue as Guest (Public Explorer Mode) →
              </button>

              {/* Bottom Security / Statutory Seal */}
              <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-center space-x-1.5 text-[11px] text-slate-400">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                <span>Secured for BIS & SIH26107 / SIH26108 Evaluation</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 px-6 border-t border-slate-200/80 dark:border-slate-800/80 bg-white/50 dark:bg-slate-900/50 text-center text-xs text-slate-500 dark:text-slate-400">
        <p>GRASK AI • Smart India Hackathon 2026 • AI-Powered Assistant for BIS Standards & GeM Procurement</p>
      </footer>
    </div>
  );
};

export default LoginPage;
