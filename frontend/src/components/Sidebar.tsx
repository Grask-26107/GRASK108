import React, { useState } from 'react';
import {
  X,
  Search,
  Building2,
  FlaskConical,
  ShieldCheck,
  Award,
  FileCheck2,
  GraduationCap,
  Scale,
  Compass,
  BarChart3,
  Sun,
  Moon,
  FolderKanban,
  FileSpreadsheet,
  Layers,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { ChatMode, UserProfile } from '../types';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  currentMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  selectedLanguage: string;
  onLanguageChange: (lang: string) => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  onNewChat: () => void;
  onOpenLicenseVerify: () => void;
  onOpenComplianceAudit: () => void;
  onOpenNutriScore?: () => void;
  onOpenApplyModal?: () => void;
  onOpenSchemeFinder?: () => void;
  onOpenProcurementTender?: () => void;
  onOpenBisService: (section: 'standards_clubs' | 'nits_training' | 'lab_recognition' | 'consumer_protection' | 'departments') => void;
  onOpenTelemetry: () => void;
  user?: UserProfile | null;
  onOpenProfile?: () => void;
  onNavigateToPortal?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  darkMode,
  onToggleDarkMode,
  onOpenLicenseVerify,
  onOpenComplianceAudit,
  onOpenNutriScore,
  onOpenApplyModal,
  onOpenSchemeFinder,
  onOpenProcurementTender,
  onOpenBisService,
  onOpenTelemetry,
  user,
  onOpenProfile,
  onNavigateToPortal,
}) => {
  const [filterText, setFilterText] = useState('');

  if (!isOpen) return null;

  const tools = [
    {
      category: 'Directories & Standards Catalog',
      items: [
        {
          id: 'departments',
          title: '17 Technical Buying Sectors',
          desc: '24,000+ standards across Civil, Electrical, Mechanical, Food...',
          icon: Building2,
          badge: '24,000+ Standards',
          action: () => onOpenBisService('departments')
        },
        {
          id: 'laboratories',
          title: 'Recognized Testing Labs',
          desc: '16 apex testing laboratories directory',
          icon: FlaskConical,
          badge: '16 Labs',
          action: () => onOpenBisService('lab_recognition')
        },
        {
          id: 'sectors',
          title: 'Browse Procurement Sectors',
          desc: 'Find standards by Civil, Electrical, Electronics, Pipes, Textiles...',
          icon: FolderKanban,
          badge: 'SIH26108',
          action: () => onOpenProcurementTender?.()
        },
        {
          id: 'nits',
          title: 'NITS Training & Learning',
          desc: 'National Institute of Training for Standardization',
          icon: GraduationCap,
          action: () => onOpenBisService('nits_training')
        },
        {
          id: 'clubs',
          title: 'Standards Clubs in Schools & Colleges',
          desc: 'Student quality awareness clubs and student visits',
          icon: Award,
          action: () => onOpenBisService('standards_clubs')
        }
      ]
    },
    {
      category: 'Supplier Verification & Quality Checks',
      items: [
        {
          id: 'license_verify',
          title: 'Supplier License & Hallmark Verifier',
          desc: 'Verify CM/L license, CRS electronics registration & Gold Hallmarks',
          icon: ShieldCheck,
          badge: 'Instant Check',
          action: () => onOpenLicenseVerify()
        },
        {
          id: 'audit_studio',
          title: 'Lab Test Report Checker',
          desc: 'Upload lab test reports and check if results meet official standards',
          icon: FileCheck2,
          badge: 'PDF / Image',
          action: () => onOpenComplianceAudit()
        },
        {
          id: 'nutri_score',
          title: 'Food Safety & Nutrition Checker',
          desc: 'Check nutrition grades, hidden sugars, palm oil & banned additives',
          icon: Scale,
          badge: 'Food Check',
          action: () => onOpenNutriScore?.()
        }
      ]
    },
    {
      category: 'MSME Support & System Logs',
      items: [
        {
          id: 'ready_to_apply',
          title: 'MSME Factory Setup & Concession',
          desc: 'Check required factory equipment, forms, and 50% fee concession',
          icon: FileSpreadsheet,
          badge: 'MSME 50% Off',
          action: () => onOpenApplyModal?.()
        },
        {
          id: 'scheme_finder',
          title: 'Scheme Finder (Pathways & Grants)',
          desc: 'Eligibility checker for Scheme-I, CRS, Hallmarking & Eco-Mark',
          icon: Compass,
          action: () => onOpenSchemeFinder?.()
        },
        {
          id: 'telemetry',
          title: 'System Activity & Analytics',
          desc: 'Real-time query metrics, response times, and system safety logs',
          icon: BarChart3,
          badge: 'System Log',
          action: () => onOpenTelemetry()
        }
      ]
    }
  ];

  const filteredCategories = tools.map(cat => ({
    ...cat,
    items: cat.items.filter(item => 
      !filterText.trim() || 
      item.title.toLowerCase().includes(filterText.toLowerCase()) || 
      item.desc.toLowerCase().includes(filterText.toLowerCase())
    )
  })).filter(cat => cat.items.length > 0);

  return (
    <div className="fixed inset-0 z-50 flex animate-in fade-in duration-200">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity" 
        onClick={onToggle}
      />

      {/* Slide-out Drawer Panel */}
      <aside className="relative z-50 w-full max-w-sm sm:max-w-md h-full bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-100 flex flex-col shadow-2xl animate-in slide-in-from-left duration-300">
        
        {/* Top National Tricolor Bar */}
        <div className="h-1.5 w-full flex shrink-0 shadow-sm">
          <div className="w-1/3 bg-[#FF9933]"></div>
          <div className="w-1/3 bg-[#FFFFFF]"></div>
          <div className="w-1/3 bg-[#138808]"></div>
        </div>

        {/* Drawer Header */}
        <div className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-blue-700 border border-indigo-400/40 flex items-center justify-center text-white shadow-md p-1.5">
              <img src="/bis-emblem.svg" alt="Emblem" className="w-6 h-6 drop-shadow" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-extrabold text-base text-slate-900 dark:text-white tracking-tight">Tools & Directories</h3>
                <span className="px-1.5 py-0.2 text-[10px] font-bold bg-indigo-50 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 rounded">
                  BIS Services
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">Secondary Utilities & Statutory Registers</p>
            </div>
          </div>

          <button
            onClick={onToggle}
            className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg transition-colors"
            title="Close Menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Official Portal Home Link */}
        {onNavigateToPortal && (
          <div className="p-3 border-b border-slate-200 dark:border-slate-800 bg-indigo-50/50 dark:bg-indigo-950/30">
            <button
              onClick={() => {
                onNavigateToPortal();
                onToggle();
              }}
              className="w-full p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs flex items-center justify-between shadow-xs cursor-pointer transition-all"
            >
              <div className="flex items-center space-x-2">
                <Building2 className="w-4 h-4" />
                <span>Official Government Portal Home</span>
              </div>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Search / Filter in Drawer */}
        <div className="p-3 border-b border-slate-200 dark:border-slate-800/80 bg-slate-50/70 dark:bg-slate-900/80">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              placeholder="Search tools, 17 departments, labs..."
              className="w-full bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            />
            {filterText && (
              <button 
                onClick={() => setFilterText('')}
                className="absolute right-2.5 top-2 text-xs text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Tools List */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-5 custom-scrollbar bg-white dark:bg-slate-900">
          {filteredCategories.map((group, gIdx) => (
            <div key={gIdx} className="space-y-2">
              <h4 className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider px-2">
                {group.category}
              </h4>
              <div className="space-y-1">
                {group.items.map((tool) => {
                  const Icon = tool.icon;
                  return (
                    <button
                      key={tool.id}
                      onClick={() => {
                        tool.action();
                        onToggle();
                      }}
                      className="w-full p-2.5 rounded-xl bg-slate-50/80 hover:bg-indigo-50/80 dark:bg-slate-950/40 dark:hover:bg-indigo-950/40 border border-slate-200 hover:border-indigo-300 dark:border-slate-800/60 dark:hover:border-indigo-500/40 flex items-center justify-between text-left transition-all group shadow-2xs"
                    >
                      <div className="flex items-start space-x-3 min-w-0 pr-2">
                        <div className="p-2 rounded-lg bg-white dark:bg-slate-800/80 group-hover:bg-indigo-600 group-hover:text-white dark:group-hover:bg-indigo-600/20 text-slate-600 dark:text-slate-300 dark:group-hover:text-indigo-300 border border-slate-200 dark:border-slate-700/60 group-hover:border-indigo-600 dark:group-hover:border-indigo-500/30 transition-colors shrink-0 mt-0.5 shadow-2xs">
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-indigo-700 dark:group-hover:text-indigo-200 truncate">
                              {tool.title}
                            </span>
                            {tool.badge && (
                              <span className="px-1.5 py-0.2 text-[9px] font-bold bg-slate-200/80 text-slate-700 dark:bg-slate-800 dark:text-indigo-300 rounded border border-slate-300 dark:border-slate-700 shrink-0">
                                {tool.badge}
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5">
                            {tool.desc}
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-400 dark:text-slate-600 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all shrink-0" />
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* User Profile Card */}
        {user && onOpenProfile && (
          <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/60">
            <div
              onClick={() => {
                onOpenProfile();
                onToggle();
              }}
              className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700/60 hover:border-indigo-300 dark:hover:border-indigo-500/40 transition-all cursor-pointer group shadow-2xs"
              title="Click to manage profile, switch operational role, or sign out"
            >
              <div className="flex items-center space-x-2.5 min-w-0 pr-1">
                <div className="w-8 h-8 rounded-xl bg-indigo-600 group-hover:bg-indigo-700 text-white font-bold flex items-center justify-center text-xs shadow-2xs shrink-0">
                  {user.name.slice(0, 1).toUpperCase()}
                </div>
                <div className="min-w-0 text-left">
                  <div className="text-xs font-bold text-slate-900 dark:text-white truncate">
                    {user.name}
                  </div>
                  <div className="text-[10px] text-indigo-600 dark:text-indigo-400 font-semibold capitalize truncate">
                    {user.role === 'citizen' ? 'Citizen' : user.role === 'industry' ? 'MSME Manufacturer' : user.role === 'procurement' ? 'GeM Officer' : 'BIS Official'}
                  </div>
                </div>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 shrink-0">
                Switch Role
              </span>
            </div>
          </div>
        )}

        {/* Drawer Footer with Synchronous Theme Toggle */}
        <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
            <span className="text-[11px] font-medium">SIH26108 Tender Engine</span>
          </div>

          <button
            onClick={onToggleDarkMode}
            className="p-1.5 px-2.5 rounded-lg bg-slate-200/80 hover:bg-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-colors flex items-center space-x-1.5 font-medium shadow-2xs"
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
            aria-label="Toggle Theme"
          >
            {darkMode ? (
              <Sun className="w-3.5 h-3.5 text-amber-500 animate-in spin-in-180 duration-200" />
            ) : (
              <Moon className="w-3.5 h-3.5 text-indigo-600 dark:text-blue-400 animate-in spin-in-180 duration-200" />
            )}
            <span className="text-[11px]">{darkMode ? 'Light Mode' : 'Dark Mode'}</span>
          </button>
        </div>

      </aside>
    </div>
  );
};

export default Sidebar;
