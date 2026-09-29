import React, { useState } from 'react';
import {
  X,
  User,
  Building,
  Mail,
  Phone,
  Shield,
  Check,
  LogOut,
  ShoppingBag,
  Factory,
  FileSpreadsheet,
  BarChart3,
  Sparkles,
  Award
} from 'lucide-react';
import { UserProfile, UserRole } from '../types';

interface UserProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: UserProfile | null;
  onUpdateProfile: (updatedUser: UserProfile) => void;
  onLogout: () => void;
  addToast: (type: 'success' | 'error' | 'info', message: string) => void;
}

const ROLE_OPTIONS: Array<{
  id: UserRole;
  title: string;
  badge: string;
  icon: React.ComponentType<{ className?: string }>;
  accentColor: string;
  description: string;
  features: string[];
}> = [
  {
    id: 'citizen',
    title: 'Citizen & Consumer',
    badge: 'Consumer Mode',
    icon: ShoppingBag,
    accentColor: 'emerald',
    description: 'Check ISI/FSSAI marks, calculate food nutrition grades, and understand consumer rights.',
    features: ['Food Nutrition & Ingredients Checker', 'BIS License & Gold Hallmark Verifier', 'Plain language helpline & grievances']
  },
  {
    id: 'industry',
    title: 'MSME Manufacturer / Lab Engineer',
    badge: 'Manufacturer Mode',
    icon: Factory,
    accentColor: 'indigo',
    description: 'Check factory equipment readiness and audit test certificates against BIS standards.',
    features: ['MSME Factory Setup & 50% Concession', 'In-House Testing Equipment Checklist', 'Lab Test Report Quality Checker']
  },
  {
    id: 'procurement',
    title: 'GeM Procurement Officer',
    badge: 'Tender Engine (SIH26108)',
    icon: FileSpreadsheet,
    accentColor: 'blue',
    description: 'Find required Indian Standards, check mandatory quality rules (QCO), and write tender clauses.',
    features: ['1-Click GeM Tender Clause Generator', 'Mandatory Quality Rules (QCO) Checker', 'Related Standards (Testing, Safety, Installation)']
  },
  {
    id: 'admin',
    title: 'BIS Official / Technical Auditor',
    badge: 'Officer Oversight',
    icon: BarChart3,
    accentColor: 'purple',
    description: 'Full overview of technical departments, recognized testing laboratories, and system activity.',
    features: ['17 Technical Buying Sectors Directory', '16 Recognized Testing Labs Directory', 'System Activity & Analytics Dashboard']
  }
];

export const UserProfileModal: React.FC<UserProfileModalProps> = ({
  isOpen,
  onClose,
  user,
  onUpdateProfile,
  onLogout,
  addToast
}) => {
  if (!isOpen || !user) return null;

  const [name, setName] = useState(user.name);
  const [email, setEmail] = useState(user.email);
  const [organization, setOrganization] = useState(user.organization || '');
  const [mobile, setMobile] = useState(user.mobile || '');
  const [selectedRole, setSelectedRole] = useState<UserRole>(user.role);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      addToast('error', 'Name cannot be empty.');
      return;
    }

    setIsSaving(true);
    const updated: UserProfile = {
      ...user,
      name: name.trim(),
      email: email.trim(),
      organization: organization.trim(),
      mobile: mobile.trim(),
      role: selectedRole
    };

    setTimeout(() => {
      onUpdateProfile(updated);
      setIsSaving(false);
      addToast('success', `Profile updated! Active role set to ${ROLE_OPTIONS.find(r => r.id === selectedRole)?.title}.`);
      onClose();
    }, 200);
  };

  const getInitials = (fullName: string) => {
    return fullName
      .split(' ')
      .map(n => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase() || 'U';
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative bg-white dark:bg-slate-900 w-full max-w-2xl rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[92vh] animate-in fade-in-50 zoom-in-95 duration-150">
        
        {/* Top Tricolor Accent Bar */}
        <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600 shrink-0" />

        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white font-bold flex items-center justify-center text-sm shadow-md">
              {getInitials(name)}
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white leading-tight">
                User Profile & Role Settings
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Update your operational role and personal details anytime
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSave} className="p-6 overflow-y-auto space-y-6 flex-1 text-left">
          
          {/* Section: Operational Role Selection */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Select Your Operational Role
                </label>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Your active role tailors AI responses, recommendations, and available tool workflows.
                </p>
              </div>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                Switch Anytime
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {ROLE_OPTIONS.map((opt) => {
                const IconComponent = opt.icon;
                const isSelected = selectedRole === opt.id;

                return (
                  <div
                    key={opt.id}
                    onClick={() => setSelectedRole(opt.id)}
                    className={`p-3.5 rounded-2xl border-2 cursor-pointer transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/30 shadow-xs'
                        : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div className={`p-2 rounded-xl ${
                          isSelected
                            ? 'bg-indigo-600 text-white'
                            : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
                        }`}>
                          <IconComponent className="w-4 h-4" />
                        </div>
                        {isSelected ? (
                          <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center">
                            <Check className="w-3 h-3 stroke-[3]" />
                          </div>
                        ) : (
                          <div className="w-5 h-5 rounded-full border border-slate-300 dark:border-slate-600" />
                        )}
                      </div>

                      <div className="flex items-center space-x-1.5">
                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                          {opt.title}
                        </h4>
                      </div>
                      <span className="inline-block text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 my-1">
                        {opt.badge}
                      </span>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                        {opt.description}
                      </p>
                    </div>

                    <div className="mt-2.5 pt-2 border-t border-slate-200/60 dark:border-slate-800/60 text-[10px] text-slate-400 space-y-0.5">
                      {opt.features.slice(0, 2).map((feat, idx) => (
                        <div key={idx} className="truncate">• {feat}</div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section: Personal & Organization Details */}
          <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">
              User Details
            </label>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <User className="w-3.5 h-3.5" />
                  </div>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Enter your name"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Mail className="w-3.5 h-3.5" />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="name@domain.gov.in"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Department / Company / Unit
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Building className="w-3.5 h-3.5" />
                  </div>
                  <input
                    type="text"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="e.g. Ministry of Railways, MSME unit"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Phone / Mobile (Optional)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Phone className="w-3.5 h-3.5" />
                  </div>
                  <input
                    type="text"
                    value={mobile}
                    onChange={(e) => setMobile(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="+91 98765 43210"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Footer Actions inside form */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <button
              type="button"
              onClick={onLogout}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 transition-colors flex items-center space-x-1.5 cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>

            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSaving}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-all flex items-center space-x-1.5 cursor-pointer disabled:opacity-70"
              >
                {isSaving ? (
                  <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Check className="w-3.5 h-3.5" />
                )}
                <span>Save Profile & Role</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserProfileModal;
