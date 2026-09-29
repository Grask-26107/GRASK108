/* =========================================================================
   [FEATURE: SCHEME_FINDER] - START
   Feature Name: BIS Scheme Finder (Certification Route Navigator)
   Description: Standalone 3-step interactive decision navigator to guide 
                manufacturers/businesses to their exact BIS conformity scheme.
   Safety Notice: This component is 100% isolated. To remove this entire feature:
     1. Delete this file: frontend/src/components/SchemeFinderModal.tsx
     2. Remove the matching [FEATURE: SCHEME_FINDER] blocks in ChatInterface.tsx
   ========================================================================= */

import React, { useState } from 'react';
import {
  X,
  Compass,
  CheckCircle2,
  ExternalLink,
  RotateCcw,
  Building2,
  Globe,
  Cpu,
  Factory,
  Gem,
  Leaf,
  Utensils,
  ArrowRight,
  Award,
  MessageSquare,
  Sparkles,
  ShieldCheck,
  Check,
  ChevronRight
} from 'lucide-react';

export interface SchemeFinderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenApplyModal?: (query?: string) => void;
  onAskAi?: (query: string) => void;
  addToast?: (type: 'success' | 'error' | 'info', message: string) => void;
}

type OriginType = 'domestic' | 'foreign';
type SectorType = 'electronics' | 'industrial' | 'jewellery' | 'eco' | 'food';
type ScaleType = 'msme' | 'large';

interface SchemeResult {
  schemeName: string;
  schemeCode: string;
  badge: string;
  authority: string;
  markName: string;
  markSymbol: string;
  timeline: string;
  description: string;
  testingRequirement: string;
  msmeBenefits: string;
  suggestedQuery: string;
  defaultApplyCategory: string;
  officialGovtLinks: {
    title: string;
    description: string;
    url: string;
  }[];
}

export const SchemeFinderModal: React.FC<SchemeFinderModalProps> = ({
  isOpen,
  onClose,
  onOpenApplyModal,
  onAskAi,
  addToast,
}) => {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [origin, setOrigin] = useState<OriginType | null>(null);
  const [sector, setSector] = useState<SectorType | null>(null);
  const [scale, setScale] = useState<ScaleType | null>(null);

  if (!isOpen) return null;

  const handleReset = () => {
    setStep(1);
    setOrigin(null);
    setSector(null);
    setScale(null);
  };

  const QUICK_PRODUCTS = [
    { label: '💧 Packaged Water (IS 14543)', origin: 'domestic' as OriginType, sector: 'food' as SectorType },
    { label: '🏗️ TMT Sariya (IS 1786)', origin: 'domestic' as OriginType, sector: 'industrial' as SectorType },
    { label: '⚡ Electronics / TWS (CRS)', origin: 'domestic' as OriginType, sector: 'electronics' as SectorType },
    { label: '💍 Gold Hallmark (HUID)', origin: 'domestic' as OriginType, sector: 'jewellery' as SectorType },
    { label: '🌍 Foreign Import (FMCS)', origin: 'foreign' as OriginType, sector: 'industrial' as SectorType },
  ];

  const getResult = (): SchemeResult => {
    // 1. Foreign Manufacturer Route
    if (origin === 'foreign') {
      if (sector === 'electronics') {
        return {
          schemeName: 'Compulsory Registration Scheme (CRS) — Foreign Factory Registration',
          schemeCode: 'Scheme-II (MeitY / BIS CRS)',
          badge: 'Self-Declaration of Conformity',
          authority: 'Bureau of Indian Standards & MeitY',
          markName: 'Standard Mark (CRS Logo with R-Number)',
          markSymbol: '⚡ R-XXXXXXXX',
          timeline: '15 to 30 Working Days',
          description:
            'Foreign IT/Electronics manufacturing units exporting to India must have an Authorized Indian Representative (AIR) and register under CRS after lab testing at BIS-recognized Indian laboratories.',
          testingRequirement:
            'Product test report from a BIS-recognized / empanelled testing laboratory situated in India (valid within 90 days of filing).',
          msmeBenefits: 'Standard government filing fees apply; test charges vary per product category.',
          suggestedQuery:
            'Explain the complete procedure, AIR appointment, and required documentation for foreign manufacturer BIS CRS registration (Scheme-II).',
          defaultApplyCategory: 'Electronics & IT Products',
          officialGovtLinks: [
            {
              title: 'BIS CRS Official Portal',
              description: 'Online registration, model inclusion & lab report submission for electronics',
              url: 'https://www.crsbis.in',
            },
            {
              title: 'National Single Window System (NSWS)',
              description: 'Unified Government clearance for foreign direct investment & compliance',
              url: 'https://www.nsws.gov.in',
            },
          ],
        };
      }

      return {
        schemeName: 'Foreign Manufacturers Certification Scheme (FMCS)',
        schemeCode: 'Scheme-IV (ISI Mark for Overseas Units)',
        badge: 'Mandatory Factory Audit',
        authority: 'Bureau of Indian Standards (Central BO)',
        markName: 'Standard ISI Mark with CM/L License',
        markSymbol: '🏛️ ISI Mark (CM/L)',
        timeline: '60 to 90 Working Days',
        description:
          'Mandatory certification scheme for foreign manufacturers supplying products to India under mandatory QCOs. Requires a physical audit of the overseas factory by BIS inspecting officers and performance testing in India.',
        testingRequirement:
          'In-house factory testing capabilities verified on-site by BIS officers, plus duplicate samples tested in independent BIS labs in India.',
        msmeBenefits: 'All fees billed in USD/INR as per BIS FMCS statutory tariff schedule.',
        suggestedQuery:
          'What are the step-by-step requirements, fee structures, and audit processes for BIS FMCS (Scheme-IV) certification for an overseas factory?',
        defaultApplyCategory: 'General Manufacturing & Industrial Goods',
        officialGovtLinks: [
          {
            title: 'BIS FMCS e-Services Portal',
            description: 'Application filing, officer nomination & tracking for foreign manufacturers',
            url: 'https://www.services.bis.gov.in',
          },
          {
            title: 'Manak Online (e-BIS)',
            description: 'Official Bureau of Indian Standards enterprise compliance portal',
            url: 'https://www.manakonline.in',
          },
        ],
      };
    }

    // 2. Domestic Routes
    if (sector === 'electronics') {
      return {
        schemeName: 'Compulsory Registration Scheme (CRS)',
        schemeCode: 'Scheme-II (CRS / MeitY Mandate)',
        badge: 'Self-Declaration Scheme',
        authority: 'Bureau of Indian Standards & Ministry of Electronics and IT',
        markName: 'Standard Mark (R-Number)',
        markSymbol: '⚡ R-XXXXXXXX',
        timeline: '15 to 25 Working Days',
        description:
          'Applicable to electronics, telecom, LED lighting, and consumer IT equipment. Instead of mandatory factory audits, certification is granted through self-declaration backed by compliant test reports from BIS-recognized labs.',
        testingRequirement:
          'Full-parameter type testing from any NABL / BIS accredited laboratory (valid for 90 days from report issuance).',
        msmeBenefits:
          scale === 'msme'
            ? 'Startup India & Udyam registered units receive expedited processing and reduced compliance burden.'
            : 'Standard processing queue with online automated issuance upon document validation.',
        suggestedQuery:
          'What is the step-by-step checklist to apply for BIS CRS (Scheme-II) for domestic electronics manufacturing in India?',
        defaultApplyCategory: 'Electronics & IT Products',
        officialGovtLinks: [
          {
            title: 'BIS CRS Registration Portal',
            description: 'Create user profile, upload lab test reports and generate R-Number certificate',
            url: 'https://www.crsbis.in',
          },
          {
            title: 'Manak Online e-Testing Labs',
            description: 'Book test slots at accredited BIS Group-1 laboratories',
            url: 'https://www.manakonline.in',
          },
        ],
      };
    }

    if (sector === 'jewellery') {
      return {
        schemeName: 'Mandatory Gold & Silver Hallmarking Scheme',
        schemeCode: 'Hallmarking Regulations (HUID Scheme)',
        badge: 'Mandatory Purity Verification',
        authority: 'Bureau of Indian Standards (Hallmarking Division)',
        markName: '6-Digit Alphanumeric HUID + BIS Mark',
        markSymbol: '💍 HUID Mark',
        timeline: 'Instant to 5 Working Days',
        description:
          'Mandatory for all jewellers selling gold jewellery and artefacts in declared districts. Registration is granted automatically online for lifetime validity with zero renewal fees for micro-enterprises.',
        testingRequirement:
          'Testing conducted through BIS-recognized Assaying & Hallmarking Centres (AHCs) using fire assay and XRF spectrometry.',
        msmeBenefits:
          'Micro & small jewellers with turnover under Rs 40 Lakhs enjoy complete exemption or nominal one-time registration charges.',
        suggestedQuery:
          'Explain the rules, fees, and exemptions for mandatory BIS Gold Hallmarking and 6-digit HUID registration for jewellers.',
        defaultApplyCategory: 'Gold & Silver Jewellery',
        officialGovtLinks: [
          {
            title: 'Manak Online Jeweller Portal',
            description: 'Automated 100% online registration for jewellers and AHC network',
            url: 'https://www.manakonline.in',
          },
          {
            title: 'BIS Care Portal',
            description: 'Consumer purity verification and HUID authenticity lookup',
            url: 'https://www.bis.gov.in',
          },
        ],
      };
    }

    if (sector === 'eco') {
      return {
        schemeName: 'Eco Mark Scheme (Green Product Certification)',
        schemeCode: 'Eco Mark under BIS Scheme-I',
        badge: 'Environmental Excellence',
        authority: 'Ministry of Environment, Forest & Climate Change & BIS',
        markName: 'Earthen Pot (Matka) Eco Logo + ISI Mark',
        markSymbol: '🍃 Eco Mark',
        timeline: '45 to 60 Working Days',
        description:
          'Voluntary and statutory labeling scheme for products meeting stringent environmental safety norms alongside fundamental Indian Standard quality metrics.',
        testingRequirement:
          'Dual verification: Indian Standard mechanical/chemical limits + hazardous substance threshold tests (RoHS / Biodegradability).',
        msmeBenefits: 'Green startup incentives and preference in government public procurement (GeM Portal).',
        suggestedQuery:
          'How can an Indian manufacturer apply for the BIS Eco Mark scheme and what are the environmental criteria?',
        defaultApplyCategory: 'General Manufacturing & Industrial Goods',
        officialGovtLinks: [
          {
            title: 'Manak Online Product Certification',
            description: 'Apply for combined ISI + Eco Mark product certification',
            url: 'https://www.manakonline.in',
          },
        ],
      };
    }

    if (sector === 'food') {
      return {
        schemeName: 'Mandatory BIS & FSSAI Dual Certification Route',
        schemeCode: 'Scheme-I (BIS ISI) + FSSAI Central/State License',
        badge: 'Mandatory Public Health Safety',
        authority: 'Bureau of Indian Standards & Food Safety and Standards Authority of India',
        markName: 'ISI Mark + FSSAI 14-Digit License',
        markSymbol: '🥗 ISI + FSSAI',
        timeline: '30 to 60 Working Days',
        description:
          'Items like Packaged Drinking Water (IS 14543), Mineral Water (IS 13428), Infant Milk Food (IS 14433), and Fortified Foods require mandatory ISI certification before obtaining an FSSAI manufacturing license.',
        testingRequirement:
          'Microbiological sterility testing, heavy metals (Lead, Arsenic, Cadmium) analysis, pesticide residues, and strict clean-room hygienic audit.',
        msmeBenefits:
          scale === 'msme'
            ? '50% statutory fee waiver on BIS application fees and marking fees for registered Udyam MSMEs and Startups.'
            : 'Standard statutory annual fee schedule.',
        suggestedQuery:
          'What are the exact mandatory steps to set up an in-house lab and get both BIS ISI mark and FSSAI license for food/water processing?',
        defaultApplyCategory: 'Packaged Drinking Water (IS 14543)',
        officialGovtLinks: [
          {
            title: 'FSSAI FoSCoS Portal',
            description: 'Food Safety Compliance System for State and Central licenses',
            url: 'https://foscos.fssai.gov.in',
          },
          {
            title: 'Manak Online (e-BIS)',
            description: 'Mandatory ISI mark application filing and laboratory scheduling',
            url: 'https://www.manakonline.in',
          },
        ],
      };
    }

    // Default Industrial / Consumer Goods -> Scheme-I
    return {
      schemeName: 'Product Certification Scheme (ISI Mark)',
      schemeCode: 'Scheme-I (Conformity Assessment Regulations)',
      badge: 'Classic ISI Mark License',
      authority: 'Bureau of Indian Standards (Central & Regional Branch Offices)',
      markName: 'ISI Mark with CM/L License Number',
      markSymbol: '🏛️ ISI Mark (CM/L)',
      timeline: '30 to 60 Working Days',
      description:
        'The foundational BIS certification scheme covering over 1,000+ products under mandatory Quality Control Orders (QCOs) including Steel, Cement, Helmets, Toys, and Electrical Cables. Involves in-house testing setup and on-site factory verification.',
      testingRequirement:
        'Complete in-house testing laboratory equipment as per the Scheme of Inspection and Testing (SIT), followed by independent BIS lab verification.',
      msmeBenefits:
        scale === 'msme'
          ? 'Eligible for 50% statutory discount on application and annual minimum marking fees under Government of India MSME/Startup policy.'
          : 'Standard statutory tariff schedule.',
      suggestedQuery:
        'Explain the factory inspection, required lab testing equipment, and 50% MSME fee discount for BIS Scheme-I (ISI Mark).',
      defaultApplyCategory: 'General Manufacturing & Industrial Goods',
      officialGovtLinks: [
        {
          title: 'Manak Online (e-BIS) Product Certification',
          description: 'Official application portal for Scheme-I ISI Mark licenses',
          url: 'https://www.manakonline.in',
        },
        {
          title: 'National Single Window System (NSWS)',
          description: 'Combined portal for business registration, clearances and BIS licensing',
          url: 'https://www.nsws.gov.in',
        },
      ],
    };
  };

  const handleOpenReadyToApply = (category: string) => {
    onClose();
    if (onOpenApplyModal) {
      onOpenApplyModal(category);
    }
  };

  const handleConsultAi = (queryText: string) => {
    onClose();
    if (onAskAi) {
      onAskAi(queryText);
    }
    if (addToast) {
      addToast('info', 'Sent your certification route query to GRASK AI Assistant.');
    }
  };

  const result = step === 4 ? getResult() : null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">
      <div className="relative w-full max-w-2xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col max-h-[92vh] overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        
        {/* Top Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-linear-to-r from-indigo-50/70 via-blue-50/40 to-white dark:from-slate-900 dark:via-indigo-950/20 dark:to-slate-900 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-linear-to-tr from-indigo-600 to-blue-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                  BIS Scheme Finder
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                  Route Navigator
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Identify your mandatory BIS conformity route, testing pathway, and official government portal in 30 seconds
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {step > 1 && (
              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-colors"
                title="Restart Scheme Navigator"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Start Over</span>
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

        {/* Step Progress Indicators */}
        <div className="px-6 py-2.5 bg-slate-50/80 dark:bg-slate-850/50 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
          <div className="flex items-center space-x-1.5">
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${step >= 1 ? 'bg-indigo-600 text-white' : 'bg-slate-200 dark:bg-slate-700'}`}>
              1
            </span>
            <span className={step === 1 ? 'text-indigo-600 dark:text-indigo-400 font-semibold' : ''}>Origin</span>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          <div className="flex items-center space-x-1.5">
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${step >= 2 ? 'bg-indigo-600 text-white' : 'bg-slate-200 dark:bg-slate-700'}`}>
              2
            </span>
            <span className={step === 2 ? 'text-indigo-600 dark:text-indigo-400 font-semibold' : ''}>Sector</span>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          <div className="flex items-center space-x-1.5">
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${step >= 3 ? 'bg-indigo-600 text-white' : 'bg-slate-200 dark:bg-slate-700'}`}>
              3
            </span>
            <span className={step === 3 ? 'text-indigo-600 dark:text-indigo-400 font-semibold' : ''}>Enterprise Scale</span>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          <div className="flex items-center space-x-1.5">
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${step === 4 ? 'bg-emerald-600 text-white' : 'bg-slate-200 dark:bg-slate-700'}`}>
              ✓
            </span>
            <span className={step === 4 ? 'text-emerald-600 dark:text-emerald-400 font-semibold' : ''}>Your Route</span>
          </div>
        </div>

        {/* Modal Body Content */}
        <div className="flex-1 overflow-y-auto p-6">
          
          {/* STEP 1: ORIGIN SELECTION */}
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Step 1: Where is your manufacturing facility located?
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  BIS operates distinct licensing and audit pathways depending on whether production is domestic or overseas.
                </p>
              </div>

              {/* Fast-Track 1-Click Common Product Selector */}
              <div className="bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/60 rounded-xl p-3">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-700 dark:text-indigo-300 mb-2">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Popular Fast-Track Pre-sets (Instant 1-Click Guide):</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {QUICK_PRODUCTS.map((item, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setOrigin(item.origin);
                        setSector(item.sector);
                        setScale('msme');
                        setStep(4);
                      }}
                      className="text-xs font-medium px-2.5 py-1 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors shadow-sm"
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setOrigin('domestic');
                    setStep(2);
                  }}
                  className="p-4 rounded-xl border-2 border-slate-200 dark:border-slate-800 hover:border-indigo-500 dark:hover:border-indigo-500 bg-white dark:bg-slate-850 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/20 text-left transition-all group flex flex-col justify-between"
                >
                  <div className="flex items-start justify-between w-full">
                    <div className="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-950/50 text-orange-600 flex items-center justify-center font-bold text-lg">
                      🇮🇳
                    </div>
                    <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-md border border-emerald-200 dark:border-emerald-800">
                      Standard Domestic Route
                    </span>
                  </div>
                  <div className="mt-4">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      Domestic Indian Manufacturer
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      Factory or premises situated inside India. Eligible for Scheme-I, CRS, and 50% MSME statutory subsidies.
                    </p>
                  </div>
                  <div className="mt-4 flex items-center text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                    <span>Select Domestic</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-1" />
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setOrigin('foreign');
                    setStep(2);
                  }}
                  className="p-4 rounded-xl border-2 border-slate-200 dark:border-slate-800 hover:border-blue-500 dark:hover:border-blue-500 bg-white dark:bg-slate-850 hover:bg-blue-50/30 dark:hover:bg-blue-950/20 text-left transition-all group flex flex-col justify-between"
                >
                  <div className="flex items-start justify-between w-full">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-950/50 text-blue-600 flex items-center justify-center">
                      <Globe className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-bold text-blue-600 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded-md border border-blue-200 dark:border-blue-800">
                      FMCS Route
                    </span>
                  </div>
                  <div className="mt-4">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                      Foreign Manufacturer / Importer
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      Manufacturing unit is outside India. Requires Authorized Indian Representative (AIR) and physical inspection.
                    </p>
                  </div>
                  <div className="mt-4 flex items-center text-xs font-semibold text-blue-600 dark:text-blue-400">
                    <span>Select Foreign / Importer</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-1" />
                  </div>
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: SECTOR SELECTION */}
          {step === 2 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Step 2: What type of product do you manufacture or import?
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  BIS assigns different statutory conformity schemes based on product sector.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                
                {/* Electronics & IT */}
                <button
                  type="button"
                  onClick={() => {
                    setSector('electronics');
                    setStep(3);
                  }}
                  className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-500 bg-white dark:bg-slate-850 hover:bg-indigo-50/30 text-left transition-all group flex items-start space-x-3"
                >
                  <div className="p-2.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600">
                      Electronics, IT & Telecom
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                      Laptops, Mobile Phones, LED Lights, Power Adapters, Smart Watches, Servers
                    </p>
                  </div>
                </button>

                {/* Industrial & Consumer Goods */}
                <button
                  type="button"
                  onClick={() => {
                    setSector('industrial');
                    setStep(3);
                  }}
                  className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-500 bg-white dark:bg-slate-850 hover:bg-indigo-50/30 text-left transition-all group flex items-start space-x-3"
                >
                  <div className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400">
                    <Factory className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600">
                      Industrial, Steel & Consumer Goods
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                      Cement, TMT Steel Bars, Helmets, Toys, Plywood, Cables, Domestic Appliances
                    </p>
                  </div>
                </button>

                {/* Food & Agro */}
                <button
                  type="button"
                  onClick={() => {
                    setSector('food');
                    setStep(3);
                  }}
                  className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-500 bg-white dark:bg-slate-850 hover:bg-indigo-50/30 text-left transition-all group flex items-start space-x-3"
                >
                  <div className="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
                    <Utensils className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600">
                      Food, Water & Agro Products
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                      Packaged Drinking Water, Mineral Water, Infant Formula, Milk Products
                    </p>
                  </div>
                </button>

                {/* Jewellery & Hallmarking */}
                <button
                  type="button"
                  onClick={() => {
                    setSector('jewellery');
                    setStep(3);
                  }}
                  className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-500 bg-white dark:bg-slate-850 hover:bg-indigo-50/30 text-left transition-all group flex items-start space-x-3"
                >
                  <div className="p-2.5 rounded-lg bg-yellow-50 dark:bg-yellow-950/60 text-yellow-600 dark:text-yellow-400">
                    <Gem className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600">
                      Precious Metals & Jewellery
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                      Gold Jewellery, Gold Artefacts, Silver Articles (Mandatory HUID Scheme)
                    </p>
                  </div>
                </button>

                {/* Eco & Green Products */}
                <button
                  type="button"
                  onClick={() => {
                    setSector('eco');
                    setStep(3);
                  }}
                  className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-500 bg-white dark:bg-slate-850 hover:bg-indigo-50/30 text-left transition-all group flex items-start space-x-3 sm:col-span-2"
                >
                  <div className="p-2.5 rounded-lg bg-teal-50 dark:bg-teal-950/60 text-teal-600 dark:text-teal-400">
                    <Leaf className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600">
                      Eco-Friendly & Green Products (Eco Mark)
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                      Recycled Plastics, Biodegradable packaging, Low-carbon materials meeting green labeling standards
                    </p>
                  </div>
                </button>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-semibold"
                >
                  ← Back to Origin Selection
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: SCALE / MSME STATUS */}
          {step === 3 && (
            <div className="space-y-4">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Step 3: What is the scale of your enterprise?
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  The Government of India provides a 50% statutory fee waiver for registered MSMEs and Startups under BIS guidelines.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setScale('msme');
                    setStep(4);
                  }}
                  className="p-4 rounded-xl border-2 border-slate-200 dark:border-slate-800 hover:border-emerald-500 bg-white dark:bg-slate-850 hover:bg-emerald-50/30 text-left transition-all group flex flex-col justify-between"
                >
                  <div className="flex items-start justify-between w-full">
                    <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 flex items-center justify-center font-bold">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100 dark:bg-emerald-950 px-2 py-0.5 rounded-md border border-emerald-300 dark:border-emerald-800">
                      50% Fee Discount
                    </span>
                  </div>
                  <div className="mt-4">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-emerald-600">
                      Micro / Small Enterprise or DPIIT Startup
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      Possesses Udyam Registration Certificate or recognized Startup status with investment under statutory ceiling.
                    </p>
                  </div>
                  <div className="mt-4 flex items-center text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                    <span>Confirm & View Route</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-1" />
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setScale('large');
                    setStep(4);
                  }}
                  className="p-4 rounded-xl border-2 border-slate-200 dark:border-slate-800 hover:border-indigo-500 bg-white dark:bg-slate-850 hover:bg-indigo-50/30 text-left transition-all group flex flex-col justify-between"
                >
                  <div className="flex items-start justify-between w-full">
                    <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 flex items-center justify-center font-bold">
                      <Building2 className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-bold text-slate-600 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-300 dark:border-slate-700">
                      Standard Scheme
                    </span>
                  </div>
                  <div className="mt-4">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600">
                      Medium / Large Scale Enterprise
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      Medium or large industrial manufacturing plant, corporate manufacturer or public sector undertaking.
                    </p>
                  </div>
                  <div className="mt-4 flex items-center text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                    <span>Confirm & View Route</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-1" />
                  </div>
                </button>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 font-semibold"
                >
                  ← Back to Sector Selection
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: RESULT SCREEN */}
          {step === 4 && result && (
            <div className="space-y-5 animate-in fade-in slide-in-from-bottom-2 duration-200">
              
              {/* Primary Scheme Card */}
              <div className="p-4 rounded-xl border border-indigo-200 dark:border-indigo-800 bg-linear-to-br from-indigo-50/80 via-blue-50/40 to-white dark:from-slate-850 dark:via-indigo-950/20 dark:to-slate-900 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-600 text-white shadow-xs">
                    {result.schemeCode}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 flex items-center space-x-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    <span>{result.badge}</span>
                  </span>
                </div>

                <div>
                  <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                    {result.schemeName}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                    {result.description}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1 text-xs">
                  <div className="p-2.5 rounded-lg bg-white/80 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">Mark / Symbol</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{result.markSymbol}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white/80 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">Typical Timeline</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{result.timeline}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white/80 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">Authority</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200 line-clamp-1">{result.authority}</span>
                  </div>
                </div>

                {/* Statutory Requirements */}
                <div className="text-xs space-y-1.5 pt-1 border-t border-slate-200/60 dark:border-slate-800/60">
                  <div className="flex items-start space-x-2 text-slate-600 dark:text-slate-300">
                    <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                    <span><strong className="text-slate-800 dark:text-slate-200">Testing:</strong> {result.testingRequirement}</span>
                  </div>
                  <div className="flex items-start space-x-2 text-slate-600 dark:text-slate-300">
                    <Sparkles className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span><strong className="text-slate-800 dark:text-slate-200">Fee Benefits:</strong> {result.msmeBenefits}</span>
                  </div>
                </div>
              </div>

              {/* THREE MANDATORY USER ACTIONS */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Recommended Next Actions
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  
                  {/* Action 1: Ready to Apply Studio */}
                  <button
                    type="button"
                    onClick={() => handleOpenReadyToApply(result.defaultApplyCategory)}
                    className="p-3 rounded-xl border border-amber-300 dark:border-amber-800 bg-amber-50/70 hover:bg-amber-100/80 dark:bg-amber-950/30 dark:hover:bg-amber-900/40 text-left transition-all group flex items-start space-x-3 shadow-xs"
                  >
                    <div className="p-2 rounded-lg bg-amber-500 text-white shrink-0 shadow-xs">
                      <Award className="w-4 h-4" />
                    </div>
                    <div>
                      <h5 className="text-xs font-bold text-amber-950 dark:text-amber-200 group-hover:text-amber-800 flex items-center">
                        <span>Open Ready to Apply Studio</span>
                        <ArrowRight className="w-3 h-3 ml-1 transition-transform group-hover:translate-x-1" />
                      </h5>
                      <p className="text-[11px] text-amber-800/80 dark:text-amber-400/80 mt-0.5">
                        Audit documents, calculate exact 50% MSME fees & download sealed application dossier PDF.
                      </p>
                    </div>
                  </button>

                  {/* Action 2: Chat with AI Assistant */}
                  <button
                    type="button"
                    onClick={() => handleConsultAi(result.suggestedQuery)}
                    className="p-3 rounded-xl border border-indigo-300 dark:border-indigo-800 bg-indigo-50/70 hover:bg-indigo-100/80 dark:bg-indigo-950/30 dark:hover:bg-indigo-900/40 text-left transition-all group flex items-start space-x-3 shadow-xs"
                  >
                    <div className="p-2 rounded-lg bg-indigo-600 text-white shrink-0 shadow-xs">
                      <MessageSquare className="w-4 h-4" />
                    </div>
                    <div>
                      <h5 className="text-xs font-bold text-indigo-950 dark:text-indigo-200 group-hover:text-indigo-800 flex items-center">
                        <span>Chat with AI (11 Languages)</span>
                        <ArrowRight className="w-3 h-3 ml-1 transition-transform group-hover:translate-x-1" />
                      </h5>
                      <p className="text-[11px] text-indigo-800/80 dark:text-indigo-400/80 mt-0.5">
                        Ask questions in your preferred language and get statutory clause-backed guidance.
                      </p>
                    </div>
                  </button>
                </div>
              </div>

              {/* Official Govt Application Links */}
              <div className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850/60 space-y-2">
                <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                  <ExternalLink className="w-3.5 h-3.5 text-blue-600" />
                  <span>Official Government Portals to Apply</span>
                </h4>
                <div className="space-y-1.5">
                  {result.officialGovtLinks.map((link, idx) => (
                    <a
                      key={idx}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-750 border border-slate-200 dark:border-slate-700 transition-colors text-xs group"
                    >
                      <div>
                        <span className="font-semibold text-blue-600 dark:text-blue-400 group-hover:underline">
                          {link.title}
                        </span>
                        <span className="text-[11px] text-slate-500 dark:text-slate-400 block">
                          {link.description}
                        </span>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 shrink-0 ml-2" />
                    </a>
                  ))}
                </div>
              </div>

            </div>
          )}

        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex items-center justify-between shrink-0 text-xs">
          <div className="text-slate-500 dark:text-slate-400 flex items-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Statutory BIS Act 2016 Conformity Matrix</span>
          </div>

          <div className="flex items-center space-x-2">
            {step === 4 && (
              <button
                type="button"
                onClick={handleReset}
                className="px-3 py-1.5 rounded-lg font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
              >
                Test Another Route
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg font-semibold bg-slate-200 hover:bg-slate-300 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default SchemeFinderModal;

/* =========================================================================
   [FEATURE: SCHEME_FINDER] - END
   ========================================================================= */
