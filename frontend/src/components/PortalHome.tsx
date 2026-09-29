import React, { useState, useRef } from 'react';
import {
  Building2,
  ShieldCheck,
  Sparkles,
  Award,
  FileCheck2,
  ShoppingBag,
  Factory,
  FileSpreadsheet,
  BarChart3,
  Layers,
  Globe2,
  CheckCircle2,
  ArrowRight,
  Search,
  Compass,
  PhoneCall,
  Linkedin,
  Youtube,
  ExternalLink,
  ChevronRight,
  Sun,
  Moon,
  FlaskConical,
  Scale,
  FileText,
  AlertTriangle,
  FolderKanban,
  Check
} from 'lucide-react';
import { UserProfile, ChatMode } from '../types';
import { SUPPORTED_LANGUAGES } from '../constants/languages';

interface PortalHomeProps {
  user: UserProfile | null;
  onOpenProfile: () => void;
  onNavigateToAssistant: (initialQuery?: string, targetMode?: ChatMode) => void;
  onOpenLicenseVerify: () => void;
  onOpenComplianceAudit: () => void;
  onOpenNutriScore: () => void;
  onOpenApplyModal: (query?: string) => void;
  onOpenSchemeFinder: () => void;
  onOpenProcurementTender: () => void;
  onOpenBisService: (section: 'standards_clubs' | 'nits_training' | 'lab_recognition' | 'consumer_protection' | 'departments') => void;
  onOpenTelemetry: () => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  selectedLanguage: string;
  onLanguageChange: (lang: string) => void;
}

export const PortalHome: React.FC<PortalHomeProps> = ({
  user,
  onOpenProfile,
  onNavigateToAssistant,
  onOpenLicenseVerify,
  onOpenComplianceAudit,
  onOpenNutriScore,
  onOpenApplyModal,
  onOpenSchemeFinder,
  onOpenProcurementTender,
  onOpenBisService,
  onOpenTelemetry,
  darkMode,
  onToggleDarkMode,
  selectedLanguage,
  onLanguageChange,
}) => {
  const officialPortals = [
    {
      title: "Government e-Marketplace (GeM)",
      url: "https://gem.gov.in",
      domain: "gem.gov.in",
      desc: "National public procurement portal for all Central & State government departments, mandating BIS compliance in tenders.",
      category: "Primary Procurement Portal",
      icon: FileSpreadsheet
    },
    {
      title: "Central Public Procurement Portal (CPPP)",
      url: "https://eprocure.gov.in",
      domain: "eprocure.gov.in",
      desc: "National e-Procurement portal hosting central ministry tenders, defense tenders, and works contracts.",
      category: "E-Procurement & Tenders",
      icon: Building2
    },
    {
      title: "Bureau of Indian Standards (BIS)",
      url: "https://www.bis.gov.in",
      domain: "bis.gov.in",
      desc: "Apex National Standards Body of India formulating Indian Standards (IS), QCO notifications, and certification marks.",
      category: "National Standards Body",
      icon: Award
    },
    {
      title: "Manakonline (e-BIS Portal)",
      url: "https://www.manakonline.in",
      domain: "manakonline.in",
      desc: "Statutory verification for Scheme-I ISI licensing, Laboratory Recognition (LRS), and Hallmarking Unique ID (HUID).",
      category: "Statutory Verification",
      icon: FileCheck2
    },
    {
      title: "NABL Accreditation India",
      url: "https://nabl-india.org",
      domain: "nabl-india.org",
      desc: "Accreditation body for testing and calibration laboratories (ISO/IEC 17025) mandated for government bid test reports.",
      category: "Laboratory Accreditation",
      icon: FlaskConical
    },
    {
      title: "Udyam MSME Registration Portal",
      url: "https://udyamregistration.gov.in",
      domain: "udyamregistration.gov.in",
      desc: "Ministry of MSME official portal offering 50% statutory fee concessions for Micro and Small manufacturing enterprises.",
      category: "MSME Development",
      icon: Factory
    },
    {
      title: "FSSAI Food Safety Authority",
      url: "https://www.fssai.gov.in",
      domain: "fssai.gov.in",
      desc: "Apex food safety authority laying down statutory standards for institutional food & canteen public procurement.",
      category: "Food Regulatory",
      icon: ShoppingBag
    },
    {
      title: "National Consumer Helpline (NCH)",
      url: "https://consumerhelpline.gov.in",
      domain: "consumerhelpline.gov.in",
      desc: "Toll-Free statutory consumer grievance redressal portal (Toll-Free: 1915 / Jago Grahak Jago).",
      category: "Statutory Helpline",
      icon: Scale
    }
  ];

  const socialLinks = [
    {
      platform: "LinkedIn",
      entity: "Government e-Marketplace (GeM)",
      url: "https://www.linkedin.com/company/government-e-marketplace-gem",
      desc: "Official GeM updates on public procurement guidelines, Buyer/Seller handbooks, and tender clauses."
    },
    {
      platform: "LinkedIn",
      entity: "Bureau of Indian Standards (BIS)",
      url: "https://www.linkedin.com/company/bureau-of-indian-standards",
      desc: "Statutory Quality Control Orders (QCOs), new standard releases, and technical committee revisions."
    },
    {
      platform: "LinkedIn",
      entity: "Food Safety and Standards Authority (FSSAI)",
      url: "https://www.linkedin.com/company/fssai",
      desc: "Statutory labeling regulations, institutional food safety benchmarks, and nutrition advisories."
    },
    {
      platform: "YouTube",
      entity: "BIS National Standards Channel",
      url: "https://www.youtube.com/@BIS_India",
      desc: "Capacity-building webinars, procurement officer training, and laboratory testing video demonstrations."
    }
  ];

  const procurementSampleQueries = [
    {
      product: "TMT Steel Rebars Fe 500D (50 MT)",
      desc: "School & hospital infrastructure project requiring mandatory ISI Mark under Steel QCO",
      standard: "IS 1786:2008",
      query: "Supply of 50 MT TMT steel rebars Fe 500D for school building construction under IS 1786"
    },
    {
      product: "Fire-Resistant Building Wires (2,000 m)",
      desc: "Hospital electrical wiring requiring flame retardant low smoke (FRLS) statutory compliance",
      standard: "IS 694:2010",
      query: "2000 fire-resistant electrical cables for hospital under IS 694"
    },
    {
      product: "Outdoor LED Street Lighting IP66 (45W)",
      desc: "Municipal road lighting requiring 10kV surge protection and photometric safety",
      standard: "IS 10322:2019",
      query: "45W outdoor LED street lighting luminaire IP66 with 10kV surge protection conforming to IS 10322"
    },
    {
      product: "PE-100 HDPE Water Pipes PN 10 (110mm)",
      desc: "Potable drinking water distribution network with hydrostatic pressure verification",
      standard: "IS 4984:2016",
      query: "110mm PE-100 HDPE pipes PN 10 for drinking water transmission conforming to IS 4984"
    }
  ];

  const [searchQuery, setSearchQuery] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  const handleGlobalMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    containerRef.current.style.setProperty('--mouse-x', `${e.clientX}px`);
    containerRef.current.style.setProperty('--mouse-y', `${e.clientY}px`);
  };

  const handleCardMouseMove = (e: React.MouseEvent<HTMLElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    e.currentTarget.style.setProperty('--card-mouse-x', `${x}px`);
    e.currentTarget.style.setProperty('--card-mouse-y', `${y}px`);
  };

  const filteredSampleQueries = procurementSampleQueries.filter(q =>
    q.product.toLowerCase().includes(searchQuery.toLowerCase()) ||
    q.standard.toLowerCase().includes(searchQuery.toLowerCase()) ||
    q.desc.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredPortals = officialPortals.filter(p =>
    p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.desc.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div
      ref={containerRef}
      onMouseMove={handleGlobalMouseMove}
      className="min-h-screen w-screen bg-slate-50 dark:bg-slate-950 font-sans antialiased text-slate-900 dark:text-slate-100 flex flex-col overflow-x-hidden relative"
    >
      {/* Ambient Mouse-Follow Spotlight Layer */}
      <div className="cursor-spotlight-layer" />
      
      {/* 1. Official National Tricolor Ribbon */}
      <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600 shrink-0 z-10" />

      {/* 2. Top Ministry / Government Identity Bar */}
      <div className="bg-slate-100/90 dark:bg-slate-900/90 border-b border-slate-200 dark:border-slate-800/80 px-4 sm:px-8 py-2 flex flex-wrap items-center justify-between text-[11px] text-slate-600 dark:text-slate-400">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-slate-800 dark:text-slate-200">भारत सरकार</span>
          <span className="text-slate-400 dark:text-slate-600">•</span>
          <span>Government of India</span>
          <span className="text-slate-400 dark:text-slate-600 hidden sm:inline">•</span>
          <span className="hidden sm:inline">Ministry of Commerce & Industry • Ministry of Consumer Affairs</span>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 text-indigo-700 dark:text-indigo-400 font-bold">
            <span className="px-1.5 py-0.5 rounded bg-indigo-100 dark:bg-indigo-900/60 text-[10px]">PRIMARY FOCUS</span>
            <span>SIH26108: AI for Indian Standards in GeM Procurement</span>
          </div>
          <span className="text-slate-300 dark:text-slate-700">|</span>
          <div className="flex items-center space-x-1 text-slate-500 dark:text-slate-400">
            <PhoneCall className="w-3 h-3 text-emerald-500" />
            <span>GeM Helpdesk: 1800-419-3436</span>
          </div>
        </div>
      </div>

      {/* 3. Main Navigation Header */}
      <header className="px-4 sm:px-8 py-3.5 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30 flex items-center justify-between">
        
        {/* Left: Brand Identity Focused on SIH26108 */}
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-700 via-blue-600 to-indigo-900 border border-amber-400/40 flex items-center justify-center text-white shadow-md p-1.5 shrink-0">
            <img src="/bis-emblem.svg" alt="Emblem" className="w-7 h-7 drop-shadow" />
          </div>
          <div className="text-left">
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-base sm:text-lg text-slate-900 dark:text-white tracking-tight leading-none">
                BIS Tender Standards Engine
              </span>
              <span className="px-2 py-0.5 text-[9px] font-bold bg-indigo-600 text-white rounded-full">
                SIH26108
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              AI Recommendation Engine for GeM & CPPP Public Procurement Specifications
            </p>
          </div>
        </div>

        {/* Right: Controls & View Switcher */}
        <div className="flex items-center space-x-3">
          
          {/* Primary View Switcher Button */}
          <button
            onClick={() => onNavigateToAssistant()}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm hover:shadow-indigo-500/20 transition-all cursor-pointer"
            title="Switch to Interactive AI Chat Assistant"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Launch Tender Assistant</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          {/* Multilingual Selector */}
          <div className="hidden md:inline-flex items-center space-x-1 px-2 py-1 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700">
            <Globe2 className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
            <select
              value={selectedLanguage}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer pr-1"
            >
              {SUPPORTED_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code} className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100">
                  {l.flag} {l.name}
                </option>
              ))}
            </select>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={onToggleDarkMode}
            className="p-1.5 px-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-colors flex items-center gap-1 text-xs font-semibold"
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {darkMode ? (
              <Sun className="w-3.5 h-3.5 text-amber-500" />
            ) : (
              <Moon className="w-3.5 h-3.5 text-indigo-600" />
            )}
            <span className="hidden sm:inline text-[11px]">{darkMode ? 'Light' : 'Dark'}</span>
          </button>

          {/* User Profile Pill */}
          {user && (
            <button
              onClick={onOpenProfile}
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded-xl bg-slate-100 hover:bg-indigo-50 dark:bg-slate-800 dark:hover:bg-indigo-950/50 border border-slate-300 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500/50 transition-all text-xs cursor-pointer group"
              title="Manage profile and switch operational role"
            >
              <div className="w-5 h-5 rounded-md bg-indigo-600 group-hover:bg-indigo-700 text-white font-bold flex items-center justify-center text-[10px] shrink-0">
                {user.name.slice(0, 1).toUpperCase()}
              </div>
              <div className="hidden sm:flex flex-col text-left leading-none">
                <span className="font-bold text-slate-800 dark:text-slate-200 text-[11px] truncate max-w-[85px]">
                  {user.name.split(' ')[0]}
                </span>
                <span className="text-[9px] text-indigo-600 dark:text-indigo-400 font-semibold capitalize">
                  {user.role === 'citizen' ? 'Citizen' : user.role === 'industry' ? 'MSME' : user.role === 'procurement' ? 'GeM Officer' : 'BIS Official'}
                </span>
              </div>
            </button>
          )}
        </div>
      </header>

      {/* 4. Priority Hero Section (SIH26108 Front & Center) */}
      <section className="relative overflow-hidden bg-gradient-to-b from-indigo-50/80 via-blue-50/30 to-white dark:from-slate-900 dark:via-slate-950 dark:to-slate-950 py-12 sm:py-16 px-4 sm:px-8 border-b border-slate-200 dark:border-slate-800">
        
        {/* Floating Ambient Glowing Gradient Orbs */}
        <div className="ambient-glow-orb w-96 h-96 -top-20 -left-20 bg-indigo-500/20 dark:bg-indigo-600/15" />
        <div className="ambient-glow-orb w-80 h-80 top-40 -right-20 bg-blue-500/15 dark:bg-blue-600/10" style={{ animationDelay: '-6s' }} />

        <div className="max-w-5xl mx-auto text-center space-y-6 relative z-10">
          
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-100/90 dark:bg-indigo-950/80 border border-indigo-300 dark:border-indigo-800 text-indigo-800 dark:text-indigo-300 text-xs font-bold shadow-2xs">
            <Award className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
            <span>Smart India Hackathon 2026 | Problem Statement ID: SIH26108</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
            AI Recommendation Engine for Indian Standards <br />
            <span className="bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-800 bg-clip-text text-transparent">
              in GeM Public Procurement
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
            Find the right <strong>Indian Standards (BIS codes)</strong> for government tenders on <strong>GeM</strong>. This smart assistant helps procurement officers avoid mistakes by instantly finding mandatory standards, checking quality rules (QCOs), and creating ready-to-use tender clauses in 1 click.
          </p>

          {/* Hero Action Buttons - Simple and Clear */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <button
              onClick={() => onNavigateToAssistant()}
              className="px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white font-bold text-sm shadow-md hover:shadow-indigo-500/25 transition-all flex items-center space-x-2 cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-amber-300" />
              <span>Start GeM Tender Assistant</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={onOpenProcurementTender}
              className="px-5 py-3 rounded-2xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 active:scale-95 text-slate-800 dark:text-white font-bold text-sm border border-slate-300 dark:border-slate-700 transition-all flex items-center space-x-2 cursor-pointer shadow-xs"
            >
              <FileSpreadsheet className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Write Tender Clauses (BoQ)</span>
            </button>

            <button
              onClick={() => onOpenBisService('departments')}
              className="px-5 py-3 rounded-2xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 active:scale-95 text-slate-800 dark:text-white font-bold text-sm border border-slate-300 dark:border-slate-700 transition-all flex items-center space-x-2 cursor-pointer shadow-xs"
            >
              <FolderKanban className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Browse 17 Buying Sectors</span>
            </button>
          </div>

          {/* Live Interactive Search & Filter Bar */}
          <div className="max-w-xl mx-auto pt-3 px-2">
            <div className="relative flex items-center">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-indigo-500">
                <Search className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search standards: Type 'cables', 'steel', 'water pipes', 'LED lighting', 'IS 1786'..."
                className="w-full pl-10 pr-10 py-2.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-xs transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  ✕
                </button>
              )}
            </div>
            {searchQuery && (
              <p className="text-[11px] text-indigo-600 dark:text-indigo-400 font-semibold mt-1 text-center">
                Showing results matching "{searchQuery}"
              </p>
            )}
          </div>

          {/* National Metrics Ticker */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-8 max-w-4xl mx-auto">
            <div className="p-3 rounded-2xl bg-white/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-2xs">
              <div className="text-xl sm:text-2xl font-black text-indigo-600 dark:text-indigo-400">24,000+</div>
              <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Indian Standards</div>
            </div>
            <div className="p-3 rounded-2xl bg-white/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-2xs">
              <div className="text-xl sm:text-2xl font-black text-blue-600 dark:text-blue-400">100%</div>
              <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Quality Rules Checked</div>
            </div>
            <div className="p-3 rounded-2xl bg-white/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-2xs">
              <div className="text-xl sm:text-2xl font-black text-purple-600 dark:text-purple-400">Linked</div>
              <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Related Standards</div>
            </div>
            <div className="p-3 rounded-2xl bg-white/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-2xs">
              <div className="text-xl sm:text-2xl font-black text-emerald-600 dark:text-emerald-400">1-Click</div>
              <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Tender Clauses</div>
            </div>
            <div className="col-span-2 sm:col-span-1 p-3 rounded-2xl bg-white/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-2xs">
              <div className="text-xl sm:text-2xl font-black text-amber-600 dark:text-amber-400">11</div>
              <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">Indian Languages</div>
            </div>
          </div>

        </div>
      </section>

      {/* 5. SIH26108 Core Procurement Capabilities Grid */}
      <section className="py-12 px-4 sm:px-8 max-w-6xl mx-auto w-full text-left">
        <div className="mb-8">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider mb-1">
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>How It Works (SIH26108)</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            How It Works for Government Buyers
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Simple, automated tools for procurement officers, tender committees, and GeM buyers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          
          <div
            onMouseMove={handleCardMouseMove}
            className="card-spotlight p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between transition-all"
          >
            <div>
              <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 w-fit mb-3">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-base text-slate-900 dark:text-white">
                1. 1-Click Tender Clause Generator
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                Turn product names or requirements into complete, legally valid tender clauses with the exact BIS standards and ISI mark rules.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400">
                Ready to copy and paste directly into GeM & CPPP bids →
              </span>
            </div>
          </div>

          <div
            onMouseMove={handleCardMouseMove}
            className="card-spotlight p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between transition-all"
          >
            <div>
              <div className="p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 w-fit mb-3">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-base text-slate-900 dark:text-white">
                2. Mandatory Quality Rule Checker
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                Checks whether the product must legally have BIS certification under government Quality Control Orders (QCO). Avoids illegal non-BIS purchases.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-rose-600 dark:text-rose-400">
                Keeps your purchases 100% audit-safe →
              </span>
            </div>
          </div>

          <div
            onMouseMove={handleCardMouseMove}
            className="card-spotlight p-5 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between transition-all"
          >
            <div>
              <div className="p-2.5 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 w-fit mb-3">
                <Layers className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-base text-slate-900 dark:text-white">
                3. Related Standards & Testing Guide
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
                Finds all related testing methods, safety rules, and installation standards so suppliers cannot dispute test results or quality benchmarks.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
              <span className="text-[11px] font-semibold text-blue-600 dark:text-blue-400">
                Prevents supplier disputes during inspection →
              </span>
            </div>
          </div>

        </div>

        {/* Live Tender Query Examples */}
        <div className="mt-8 p-6 rounded-3xl bg-indigo-50/50 dark:bg-slate-900/60 border border-indigo-100 dark:border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold text-sm text-slate-900 dark:text-white flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>Try Sample Tender Queries:</span>
            </h4>
            <span className="text-[11px] text-slate-500 dark:text-slate-400">Click any card to try it in the Assistant</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {filteredSampleQueries.length > 0 ? (
              filteredSampleQueries.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => onNavigateToAssistant(item.query, 'industry')}
                  onMouseMove={handleCardMouseMove}
                  className="card-spotlight p-3.5 rounded-2xl bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 hover:border-indigo-400 dark:hover:border-indigo-500 active:scale-95 cursor-pointer transition-all shadow-2xs group"
                >
                  <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 mb-1.5">
                    {item.standard}
                  </span>
                  <h5 className="font-bold text-xs text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                    {item.product}
                  </h5>
                  <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                    {item.desc}
                  </p>
                  <div className="mt-2 flex items-center text-[10px] font-semibold text-indigo-600 dark:text-indigo-400">
                    <span>View Tender Details</span>
                    <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full py-4 text-center text-xs text-slate-400">
                No sample specifications matched "{searchQuery}". Try "steel", "wires", "LED", or "pipes".
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 6. UNIQUE VALUE-ADDED FEATURES SECTION (SIH26107 Highlighted as Unique Capabilities) */}
      <section className="py-12 px-4 sm:px-8 bg-gradient-to-b from-white via-slate-50 to-slate-100/60 dark:from-slate-950 dark:via-slate-900/60 dark:to-slate-950 border-t border-slate-200 dark:border-slate-800 text-left">
        <div className="max-w-6xl mx-auto">
          
          <div className="mb-8">
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs font-bold mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>Extra Smart Features</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
              Supplier Verification & Quality Checks
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-3xl">
              Why our tool is unique: In addition to finding standards (SIH26108), we give you <strong>4 simple verification tools</strong> to check winning bidders, verify licenses, and inspect test reports before awarding contracts.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Unique Feature 1: Supplier License Verification */}
            <div
              onClick={onOpenLicenseVerify}
              onMouseMove={handleCardMouseMove}
              className="card-spotlight p-5 rounded-3xl bg-white dark:bg-slate-900 border-2 border-emerald-500/20 hover:border-emerald-500 dark:hover:border-emerald-500 active:scale-95 shadow-sm transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div>
                <div className="p-2.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 w-fit mb-3 group-hover:scale-105 transition-transform">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div className="inline-block px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 mb-1.5">
                  EXTRA FEATURE
                </div>
                <h3 className="font-extrabold text-sm text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400">
                  Supplier License Verifier
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  Check any supplier's BIS license number (CM/L), electronic registration (CRS), or Hallmark gold code (HUID) to stop fake suppliers.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs font-bold text-emerald-600 dark:text-emerald-400">
                <span>Check License</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            {/* Unique Feature 2: Lab Test Report Checker */}
            <div
              onClick={onOpenComplianceAudit}
              onMouseMove={handleCardMouseMove}
              className="card-spotlight p-5 rounded-3xl bg-white dark:bg-slate-900 border-2 border-blue-500/20 hover:border-blue-500 dark:hover:border-blue-500 active:scale-95 shadow-sm transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div>
                <div className="p-2.5 rounded-2xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 w-fit mb-3 group-hover:scale-105 transition-transform">
                  <FlaskConical className="w-5 h-5" />
                </div>
                <div className="inline-block px-2 py-0.5 rounded text-[9px] font-bold bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300 mb-1.5">
                  EXTRA FEATURE
                </div>
                <h3 className="font-extrabold text-sm text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  Lab Test Report Checker
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  Upload or enter lab test reports to see if the tested numbers meet official BIS standards with a simple PASS or FAIL verdict.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs font-bold text-blue-600 dark:text-blue-400">
                <span>Check Test Report</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            {/* Unique Feature 3: Factory Setup & MSME Concession */}
            <div
              onClick={() => onOpenApplyModal()}
              onMouseMove={handleCardMouseMove}
              className="card-spotlight p-5 rounded-3xl bg-white dark:bg-slate-900 border-2 border-purple-500/20 hover:border-purple-500 dark:hover:border-purple-500 active:scale-95 shadow-sm transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div>
                <div className="p-2.5 rounded-2xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 w-fit mb-3 group-hover:scale-105 transition-transform">
                  <Factory className="w-5 h-5" />
                </div>
                <div className="inline-block px-2 py-0.5 rounded text-[9px] font-bold bg-purple-100 dark:bg-purple-900/60 text-purple-700 dark:text-purple-300 mb-1.5">
                  EXTRA FEATURE
                </div>
                <h3 className="font-extrabold text-sm text-slate-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400">
                  Factory Setup & MSME Concession
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  Check if a manufacturer has the required testing equipment and see if MSME suppliers qualify for a 50% government fee concession.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs font-bold text-purple-600 dark:text-purple-400">
                <span>Check Factory & Fee</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            {/* Unique Feature 4: Food Safety & Nutrition Checker */}
            <div
              onClick={onOpenNutriScore}
              onMouseMove={handleCardMouseMove}
              className="card-spotlight p-5 rounded-3xl bg-white dark:bg-slate-900 border-2 border-amber-500/20 hover:border-amber-500 dark:hover:border-amber-500 active:scale-95 shadow-sm transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div>
                <div className="p-2.5 rounded-2xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 w-fit mb-3 group-hover:scale-105 transition-transform">
                  <ShoppingBag className="w-5 h-5" />
                </div>
                <div className="inline-block px-2 py-0.5 rounded text-[9px] font-bold bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300 mb-1.5">
                  EXTRA FEATURE
                </div>
                <h3 className="font-extrabold text-sm text-slate-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400">
                  Food Safety & Nutrition Checker
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  For canteens, schools, and ration buying: see simple nutrition grades (A to E) and catch hidden unhealthy ingredients or banned additives.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs font-bold text-amber-600 dark:text-amber-400">
                <span>Check Food Safety</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* 7. Official Government Portals Directory (Verified External Links) */}
      <section className="py-12 px-4 sm:px-8 bg-slate-100/70 dark:bg-slate-900/40 border-y border-slate-200 dark:border-slate-800 text-left">
        <div className="max-w-6xl mx-auto">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-8">
            <div>
              <div className="inline-flex items-center space-x-1.5 text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider mb-1">
                <Building2 className="w-3.5 h-3.5" />
                <span>Official Government Websites</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
                Official Government Portals
              </h2>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                Direct links to verified government portals for GeM buying, tenders, BIS standards, and testing labs.
              </p>
            </div>
            <div className="mt-3 md:mt-0 text-xs text-slate-500 dark:text-slate-400 flex items-center space-x-1">
              <span>All links open official government websites securely</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {filteredPortals.length > 0 ? (
              filteredPortals.map((portal, idx) => {
                const IconComp = portal.icon;
                return (
                  <a
                    key={idx}
                    href={portal.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onMouseMove={handleCardMouseMove}
                    className="card-spotlight p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500 hover:shadow-md active:scale-95 transition-all group flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                          <IconComp className="w-4 h-4" />
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                          {portal.category}
                        </span>
                      </div>

                      <h3 className="font-bold text-xs text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                        {portal.title}
                      </h3>
                      <div className="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 mt-0.5">
                        {portal.domain}
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed line-clamp-2">
                        {portal.desc}
                      </p>
                    </div>

                    <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] font-semibold text-slate-600 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      <span>Visit Portal</span>
                      <ExternalLink className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </a>
                );
              })
            ) : (
              <div className="col-span-full py-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xs">
                <p className="text-sm font-semibold text-slate-600 dark:text-slate-400">
                  No official government portals match "{searchQuery}"
                </p>
                <button
                  onClick={() => setSearchQuery('')}
                  className="mt-2 text-xs text-indigo-600 dark:text-indigo-400 font-bold hover:underline"
                >
                  Clear search filter
                </button>
              </div>
            )}
          </div>

        </div>
      </section>

      {/* 8. Official Social Channels (LinkedIn & YouTube) */}
      <section className="py-12 px-4 sm:px-8 max-w-6xl mx-auto w-full text-left">
        <div className="mb-6">
          <div className="inline-flex items-center space-x-1.5 text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider mb-1">
            <Linkedin className="w-3.5 h-3.5" />
            <span>Official News & Channels</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            Connect with Official Authorities
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Follow official notifications, new quality rules (QCOs), and GeM public procurement updates.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {socialLinks.map((s, idx) => (
            <a
              key={idx}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              onMouseMove={handleCardMouseMove}
              className="card-spotlight p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-500 active:scale-95 transition-all group flex flex-col justify-between shadow-2xs"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2 rounded-xl ${
                    s.platform === 'LinkedIn'
                      ? 'bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400'
                      : 'bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400'
                  }`}>
                    {s.platform === 'LinkedIn' ? <Linkedin className="w-4 h-4" /> : <Youtube className="w-4 h-4" />}
                  </div>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                    Official
                  </span>
                </div>

                <h4 className="font-bold text-xs text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  {s.entity}
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                  {s.desc}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] font-semibold text-blue-600 dark:text-blue-400">
                <span>Follow on {s.platform}</span>
                <ExternalLink className="w-3 h-3" />
              </div>
            </a>
          ))}
        </div>
      </section>

      {/* 9. Official GIGW Government Website Footer */}
      <footer className="mt-auto bg-slate-900 text-slate-300 border-t border-slate-800 text-xs text-left">
        
        {/* Tricolor Stripe on Footer */}
        <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600 shrink-0" />

        <div className="max-w-6xl mx-auto px-4 sm:px-8 py-10 grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Col 1: About */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-700 flex items-center justify-center p-1">
                <img src="/bis-emblem.svg" alt="Emblem" className="w-5 h-5 drop-shadow" />
              </div>
              <span className="font-extrabold text-sm text-white">BIS Tender Standards Engine</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              AI Recommendation Engine for Indian Standards (BIS) in Public Procurement (GeM / CPPP). Developed for Smart India Hackathon 2026 under Problem Statement ID: <strong>SIH26108</strong>.
            </p>
          </div>

          {/* Col 2: Procurement Portals */}
          <div className="space-y-2">
            <h4 className="font-bold text-white text-xs uppercase tracking-wider">Public Procurement</h4>
            <ul className="space-y-1.5 text-[11px] text-slate-400">
              <li><a href="https://gem.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Government e-Marketplace (GeM)</a></li>
              <li><a href="https://eprocure.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Central Public Procurement Portal (CPPP)</a></li>
              <li><a href="https://udyamregistration.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Udyam MSME Portal</a></li>
              <li><a href="https://nabl-india.org" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">NABL Accredited Testing Labs</a></li>
            </ul>
          </div>

          {/* Col 3: Statutory Standards */}
          <div className="space-y-2">
            <h4 className="font-bold text-white text-xs uppercase tracking-wider">Statutory Authorities</h4>
            <ul className="space-y-1.5 text-[11px] text-slate-400">
              <li><a href="https://www.bis.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Bureau of Indian Standards (BIS)</a></li>
              <li><a href="https://www.manakonline.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Manakonline (e-BIS Portal)</a></li>
              <li><a href="https://www.fssai.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">FSSAI Food Safety Authority</a></li>
              <li><a href="https://consumerhelpline.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">National Consumer Helpline (1915)</a></li>
            </ul>
          </div>

          {/* Col 4: Legal & Standards */}
          <div className="space-y-2">
            <h4 className="font-bold text-white text-xs uppercase tracking-wider">Statutory Mandate</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Enforcing Quality Control Orders (QCO) and BIS Act statutory compliance for all public procurement tenders under General Financial Rules (GFR).
            </p>
            <div className="pt-2">
              <span className="inline-block px-2.5 py-1 rounded bg-slate-800 text-[10px] font-semibold text-indigo-400 border border-slate-700">
                ✓ Priority Focus: SIH26108 Tender Engine
              </span>
            </div>
          </div>

        </div>

        {/* Bottom Disclaimer */}
        <div className="border-t border-slate-800 py-4 px-4 sm:px-8 text-center text-[11px] text-slate-500">
          <p>© 2026 Bureau of Indian Standards Procurement Engine • Smart India Hackathon 2026 (SIH26108) • Designed in compliance with GIGW</p>
        </div>
      </footer>

    </div>
  );
};

export default PortalHome;
