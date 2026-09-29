import React, { useState, useEffect } from 'react';
import {
  X,
  FileSpreadsheet,
  Search,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Check,
  Download,
  FolderKanban,
  ShieldAlert,
  Flame,
  Zap,
  Building2,
  Droplets,
  HardHat,
  Laptop,
  Layers,
  ArrowRight,
  ExternalLink,
  Info,
  Clock,
  RefreshCw,
  FileText
} from 'lucide-react';
import { procurementApi } from '../services/api';

export interface ProcurementTenderModalProps {
  isOpen: boolean;
  onClose: () => void;
  addToast?: (type: 'success' | 'error' | 'info', message: string) => void;
  onAskAi?: (query: string) => void;
}

export const ProcurementTenderModal: React.FC<ProcurementTenderModalProps> = ({
  isOpen,
  onClose,
  addToast,
  onAskAi
}) => {
  const [activeTab, setActiveTab] = useState<'search' | 'upload' | 'sectors'>('search');
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [copiedClause, setCopiedClause] = useState(false);
  const [activeAlliedTab, setActiveAlliedTab] = useState<'test_methods' | 'normative_references' | 'safety_standards' | 'installation_standards' | 'terminology_standards' | 'related_product_standards'>('test_methods');

  // File Upload State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [parsedItems, setParsedItems] = useState<any[]>([]);
  const [isParsingDoc, setIsParsingDoc] = useState(false);
  const [tenderUploadNotice, setTenderUploadNotice] = useState<string | null>(null);
  const [tenderUploadReason, setTenderUploadReason] = useState<string | null>(null);
  const [tenderUploadIsError, setTenderUploadIsError] = useState(false);

  // Sector & Ministry Directory State
  const [browseMode, setBrowseMode] = useState<'category' | 'ministry'>('category');
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [categoryStandards, setCategoryStandards] = useState<any[]>([]);

  const [ministries, setMinistries] = useState<string[]>([]);
  const [selectedMinistry, setSelectedMinistry] = useState<string>('');
  const [ministryStandards, setMinistryStandards] = useState<any[]>([]);

  // Load categories and ministries on open
  useEffect(() => {
    if (isOpen) {
      loadCategories();
      loadMinistries();
    }
  }, [isOpen]);

  const loadCategories = async () => {
    try {
      const res = await procurementApi.getCategories();
      if (res.success && res.categories) {
        setCategories(res.categories);
        if (res.categories.length > 0 && !selectedCategory) {
          selectCategory(res.categories[0]);
        }
      }
    } catch (e) {
      console.error('Failed to load categories', e);
    }
  };

  const loadMinistries = async () => {
    try {
      const res = await procurementApi.getMinistries();
      if (res.success && res.ministries) {
        setMinistries(res.ministries);
        if (res.ministries.length > 0 && !selectedMinistry) {
          selectMinistry(res.ministries[0]);
        }
      }
    } catch (e) {
      console.error('Failed to load ministries', e);
    }
  };

  const selectCategory = async (cat: string) => {
    setSelectedCategory(cat);
    try {
      const res = await procurementApi.getStandardsByCategory(cat);
      if (res.success) {
        setCategoryStandards(res.standards || []);
      }
    } catch (e) {
      console.error('Failed to load standards for category', e);
    }
  };

  const selectMinistry = async (m: string) => {
    setSelectedMinistry(m);
    try {
      const res = await procurementApi.getStandardsByMinistry(m);
      if (res.success) {
        setMinistryStandards(res.standards || []);
      }
    } catch (e) {
      console.error('Failed to load standards for ministry', e);
    }
  };

  const handleSearch = async (customQuery?: string) => {
    const textToSearch = customQuery || query;
    if (!textToSearch.trim()) {
      addToast?.('error', 'Please enter a product description or technical specification.');
      return;
    }

    setIsLoading(true);
    setRecommendation(null);
    setCopiedClause(false);

    try {
      const res = await procurementApi.recommend(textToSearch);
      if (res.success) {
        setRecommendation(res);
        if (res.match_found) {
          addToast?.('success', `Found standard: ${res.primary_standard?.code}`);
        } else {
          addToast?.('info', 'No direct standard match found. Try entering key technical specs.');
        }
      } else {
        addToast?.('error', res.error || 'Failed to analyze specification.');
      }
    } catch (e: any) {
      console.error('Search error', e);
      addToast?.('error', e.response?.data?.detail || 'Error connecting to recommendation service.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const file = files[0];
    setUploadFile(file);
    setIsParsingDoc(true);
    setParsedItems([]);
    setTenderUploadNotice(null);
    setTenderUploadReason(null);
    setTenderUploadIsError(false);

    try {
      const res = await procurementApi.uploadTender(file);
      if (res.success && res.total_items_found > 0) {
        setParsedItems(res.items || []);
        addToast?.('success', `Extracted ${res.total_items_found} procurement items from tender document!`);
      } else if (res.is_relevant === false || !res.success) {
        setParsedItems([]);
        const reason = res.relevance_reason || 'Non-Procurement Document Detected';
        const msg = res.message || 'The uploaded file does not contain recognized public procurement specifications or Bill of Quantities (BoQ) items.';
        setTenderUploadNotice(msg);
        setTenderUploadReason(reason);
        setTenderUploadIsError(true);
        addToast?.('error', reason);
      } else {
        setParsedItems([]);
        const msg = res.message || 'Tender document read successfully, but no direct Indian Standard matches were found for the line items.';
        setTenderUploadNotice(msg);
        setTenderUploadIsError(false);
        addToast?.('info', 'No direct standard matches found in document.');
      }
    } catch (err: any) {
      console.error('Upload error', err);
      const errMsg = err.response?.data?.detail || 'Error reading tender file.';
      setTenderUploadNotice(errMsg);
      setTenderUploadIsError(true);
      addToast?.('error', errMsg);
    } finally {
      setIsParsingDoc(false);
    }
  };

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
    downloadAnchor.setAttribute('download', `GeM_Tender_Spec_${data.primary_standard?.id || 'IS'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    addToast?.('success', 'Tender specification dossier downloaded!');
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

  const quickSamples = [
    { label: 'TMT Rebars Fe 500D (IS 1786)', query: 'Supply of 50 MT TMT steel rebars Fe 500D for school building construction' },
    { label: 'Structural Steel / Eurocode 3 (IS 2062)', query: 'Procurement of structural steel sections specified under Eurocode 3 for bridge fabrication' },
    { label: 'Concrete Code / RCC (IS 456)', query: 'Reinforced concrete design and M30 grade mix execution under IS 456' },
    { label: 'PVC House Wires (IS 694)', query: '1.5 sq mm copper fire resistant FRLS building wire cables' },
    { label: 'LED Street Lights (IS 10322)', query: '45W outdoor LED street lighting luminaire IP66 with 10kV surge protection' },
    { label: 'OPC 53 Cement (IS 269)', query: 'Ordinary Portland Cement 53 grade fresh bags conforming to BIS' },
    { label: 'HDPE Water Pipes (IS 4984)', query: '110mm PE-100 HDPE pipes PN 10 for drinking water transmission' },
    { label: 'Submersible Pumps (IS 8034)', query: '5 HP submersible borewell pump set with BEE 3-star energy efficiency' },
    { label: 'Fire Extinguishers (IS 15683)', query: '6kg portable ABC dry chemical powder fire extinguishers' },
    { label: 'Solar PV Modules (IS 14286)', query: '540W monocrystalline solar photovoltaic modules under ALMM' },
    { label: '22K Gold Hallmarking HUID (IS 1417)', query: '22 Karat gold bullion coins with mandatory 6-digit alphanumeric HUID marking' }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-5xl max-h-[92vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
        
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-600/20 border border-indigo-500/30 rounded-xl text-indigo-400">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg sm:text-xl font-bold text-white">AI Tender Specification Assistant</h2>
                <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                  SIH26108 • GeM / CPPP
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Semantic Indian Standards (BIS) recommender, allied testing rules, latest amendments & mandatory QCO validator
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 bg-slate-900/60 px-4 sm:px-6 gap-2">
          <button
            onClick={() => setActiveTab('search')}
            className={`py-3 px-3 text-xs sm:text-sm font-medium flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'search'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-4 h-4" />
            Item / Specification Search
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`py-3 px-3 text-xs sm:text-sm font-medium flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'upload'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <UploadCloud className="w-4 h-4" />
            Upload Tender / BoQ Document
          </button>
          <button
            onClick={() => setActiveTab('sectors')}
            className={`py-3 px-3 text-xs sm:text-sm font-medium flex items-center gap-2 border-b-2 transition-all ${
              activeTab === 'sectors'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FolderKanban className="w-4 h-4" />
            Browse Procurement Sectors
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 custom-scrollbar">

          {/* TAB 1: PRODUCT SEARCH */}
          {activeTab === 'search' && (
            <div className="space-y-5">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Search className="w-3.5 h-3.5 text-indigo-400" />
                  Enter Product Description, Technical Specifications, or Vernacular Query
                </label>
                <div className="relative">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSearch();
                      }
                    }}
                    placeholder="E.g., '12mm TMT steel bars Fe 500D for school construction', '2.5 sq mm copper wire', '45W LED streetlight IP66', or in Hindi 'स्कूल भवन के लिए पीवीसी बिजली के तार'..."
                    rows={3}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
                  />
                  <button
                    onClick={() => handleSearch()}
                    disabled={isLoading}
                    className="absolute right-3 bottom-3 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/30"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Search className="w-3.5 h-3.5" />
                        Analyze & Recommend
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Quick Suggestion Chips */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  High-Demand Procurement Items (Click to test):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {quickSamples.map((sample, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuery(sample.query);
                        handleSearch(sample.query);
                      }}
                      className="px-2.5 py-1 text-xs bg-slate-800/80 hover:bg-indigo-900/40 text-slate-300 hover:text-indigo-200 border border-slate-700 hover:border-indigo-500/40 rounded-lg transition-colors"
                    >
                      {sample.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Recommendation Results Display */}
              {recommendation && (
                <div className="mt-6 space-y-4 animate-in fade-in duration-300">
                  {recommendation.match_found ? (
                    <>
                      {/* Top Summary Card */}
                      <div className="bg-slate-950/80 border border-slate-700/80 rounded-xl p-4 sm:p-5 relative overflow-hidden">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <div className="flex flex-wrap items-center gap-2 mb-2">
                              <span className="px-2.5 py-0.5 text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full flex items-center gap-1">
                                <CheckCircle2 className="w-3 h-3" />
                                {recommendation.confidence_score}% Semantic Confidence Match
                              </span>

                              {/* Traffic Light QCO Risk Indicator */}
                              {recommendation.obsolete_warning ? (
                                <span className="px-2.5 py-0.5 text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-full flex items-center gap-1">
                                  <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
                                  🔴 High Risk: Obsolete Standard Cited
                                </span>
                              ) : recommendation.foreign_standard_notice ? (
                                <span className="px-2.5 py-0.5 text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-full flex items-center gap-1">
                                  <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                                  🟡 Foreign Standard Harmonized
                                </span>
                              ) : (
                                <span className="px-2.5 py-0.5 text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full flex items-center gap-1">
                                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                                  🟢 100% GFR 144 & QCO Compliant
                                </span>
                              )}

                              <span className="px-2.5 py-0.5 text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-full">
                                {recommendation.primary_standard.category}
                              </span>
                            </div>
                            <h3 className="text-xl sm:text-2xl font-black text-white flex items-center gap-2">
                              {recommendation.primary_standard.code}
                              <span className="text-xs px-2 py-0.5 font-bold bg-green-500/10 text-green-400 border border-green-500/20 rounded-md">
                                {recommendation.primary_standard.latest_edition}
                              </span>
                            </h3>
                            <p className="text-sm text-slate-300 mt-1 font-medium">
                              {recommendation.primary_standard.title}
                            </p>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleExportGemBoq([{
                                tender_item_description: query,
                                recommendation: recommendation
                              }])}
                              className="px-3 py-1.5 bg-emerald-600/90 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg border border-emerald-500 flex items-center gap-1.5 transition-colors shadow-sm"
                            >
                              <FileSpreadsheet className="w-3.5 h-3.5" />
                              Export GeM BoQ (CSV)
                            </button>
                            <button
                              onClick={() => handleExportJson(recommendation)}
                              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 flex items-center gap-1.5 transition-colors"
                            >
                              <Download className="w-3.5 h-3.5" />
                              Export Spec (JSON)
                            </button>
                          </div>
                        </div>

                        {/* Obsolete Warning Banner */}
                        {recommendation.obsolete_warning && (
                          <div className="mt-3 p-3 bg-amber-500/15 border border-amber-500/40 rounded-lg flex items-start gap-2 text-amber-200 text-xs">
                            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                            <div>
                              <span className="font-bold">Obsolete Standard Warning: </span>
                              {recommendation.obsolete_warning.warning} {recommendation.obsolete_warning.recommendation}
                            </div>
                          </div>
                        )}

                        {/* Foreign Standard Equivalence Notice Banner */}
                        {recommendation.foreign_standard_notice && (
                          <div className="mt-3 p-3 bg-blue-500/15 border border-blue-500/40 rounded-lg flex items-start gap-2.5 text-blue-200 text-xs">
                            <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                            <div>
                              <span className="font-bold text-blue-300">
                                Foreign Standard Detected ({recommendation.foreign_standard_notice.foreign_standard_detected}):
                              </span>
                              <p className="mt-0.5 text-slate-200">
                                {recommendation.foreign_standard_notice.statutory_advice}
                              </p>
                            </div>
                          </div>
                        )}

                        {/* Active Amendments Pill Bar */}
                        <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-2 text-xs">
                          <span className="text-slate-400 font-semibold flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5 text-indigo-400" />
                            Active Amendments ({recommendation.primary_standard.total_amendments}):
                          </span>
                          {recommendation.primary_standard.active_amendments.map((amd: any, i: number) => (
                            <span
                              key={i}
                              title={amd.scope}
                              className="px-2 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300 text-[11px]"
                            >
                              Amd {amd.number} ({amd.year})
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Mandatory Certification (QCO) Alert Box */}
                      {recommendation.mandatory_certification?.is_mandatory && (
                        <div className="bg-amber-950/20 border border-amber-500/40 rounded-xl p-4 flex items-start gap-3 text-slate-200">
                          <div className="p-2 bg-amber-500/20 border border-amber-500/30 rounded-lg text-amber-400 shrink-0 mt-0.5">
                            <ShieldAlert className="w-5 h-5" />
                          </div>
                          <div className="space-y-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-xs font-black text-amber-400 uppercase tracking-wider">
                                Statutory Requirement:
                              </span>
                              <span className="px-2 py-0.5 text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded">
                                {recommendation.mandatory_certification.scheme}
                              </span>
                              <span className="text-xs text-slate-400">
                                Issued by: {recommendation.mandatory_certification.issuing_ministry}
                              </span>
                            </div>
                            <p className="text-xs text-amber-100 font-semibold">
                              {recommendation.mandatory_certification.qco_order} ({recommendation.mandatory_certification.statutory_act})
                            </p>
                            <p className="text-xs text-slate-300">
                              {recommendation.mandatory_certification.tender_warning}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Allied Standards Section */}
                      <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 sm:p-5 space-y-4">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-bold text-white flex items-center gap-2">
                            <Layers className="w-4 h-4 text-indigo-400" />
                            Allied Standards Taxonomy
                          </h4>
                          <span className="text-[11px] text-slate-400">
                            Normative, Testing, Safety & Installation Codes
                          </span>
                        </div>

                        {/* Allied Category Selector Pills */}
                        <div className="flex flex-wrap gap-1.5 border-b border-slate-800 pb-3">
                          {[
                            { id: 'test_methods', label: '🔬 Mandatory Test Methods', count: recommendation.allied_standards.test_methods?.length || 0 },
                            { id: 'normative_references', label: '📐 Normative References', count: recommendation.allied_standards.normative_references?.length || 0 },
                            { id: 'safety_standards', label: '🛡️ Safety Standards', count: recommendation.allied_standards.safety_standards?.length || 0 },
                            { id: 'installation_standards', label: '🏗️ Installation / Practice', count: recommendation.allied_standards.installation_standards?.length || 0 },
                            { id: 'terminology_standards', label: '📖 Terminology', count: recommendation.allied_standards.terminology_standards?.length || 0 },
                            { id: 'related_product_standards', label: '📦 Related Products', count: recommendation.allied_standards.related_product_standards?.length || 0 },
                          ].map((tab) => (
                            <button
                              key={tab.id}
                              onClick={() => setActiveAlliedTab(tab.id as any)}
                              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
                                activeAlliedTab === tab.id
                                  ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                              }`}
                            >
                              {tab.label}
                              <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${
                                activeAlliedTab === tab.id ? 'bg-indigo-800 text-indigo-100' : 'bg-slate-800 text-slate-400'
                              }`}>
                                {tab.count}
                              </span>
                            </button>
                          ))}
                        </div>

                        {/* Active Allied Standards Content */}
                        <div className="space-y-2">
                          {(recommendation.allied_standards[activeAlliedTab] || []).map((item: any, idx: number) => (
                            <div
                              key={idx}
                              className="p-3 bg-slate-900 border border-slate-800/80 rounded-lg flex flex-wrap items-center justify-between gap-2 hover:border-slate-700 transition-colors"
                            >
                              <div>
                                <span className="text-xs font-bold text-indigo-400 font-mono">
                                  {item.code}
                                </span>
                                <p className="text-xs text-slate-200 font-medium mt-0.5">
                                  {item.title}
                                </p>
                                {item.role && (
                                  <p className="text-[11px] text-slate-400 mt-0.5">
                                    Role: {item.role}
                                  </p>
                                )}
                              </div>
                              <div className="flex items-center gap-2">
                                {item.clause && (
                                  <span className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-300 rounded font-mono">
                                    {item.clause}
                                  </span>
                                )}
                                {item.nabl_required && (
                                  <span className="px-2 py-0.5 text-[10px] bg-red-500/20 text-red-300 border border-red-500/30 rounded font-semibold">
                                    NABL Lab Testing Required
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Official GeM Tender Clause Box */}
                      <div className="bg-slate-950 border border-indigo-500/30 rounded-xl p-4 sm:p-5 space-y-3 shadow-lg shadow-indigo-950/20">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-indigo-400" />
                            <h4 className="text-sm font-bold text-white">
                              Official GeM Tender Specification Clause (Ready to Paste)
                            </h4>
                          </div>
                          <button
                            onClick={() => handleCopyClause(recommendation.gem_tender_clause)}
                            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/30"
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
                    </>
                  ) : (
                    <div className="p-6 bg-slate-950 border border-slate-800 rounded-xl text-center space-y-2">
                      <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
                      <h4 className="text-sm font-bold text-white">No Direct Indian Standard Match</h4>
                      <p className="text-xs text-slate-400 max-w-lg mx-auto">
                        {recommendation.message}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: UPLOAD TENDER DOCUMENT */}
          {activeTab === 'upload' && (
            <div className="space-y-5">
              <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 bg-slate-950/50 rounded-2xl p-6 sm:p-8 text-center transition-colors">
                <input
                  type="file"
                  id="tenderFileInput"
                  accept=".pdf,.txt"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <label
                  htmlFor="tenderFileInput"
                  className="cursor-pointer flex flex-col items-center justify-center space-y-3"
                >
                  <div className="p-4 bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 rounded-2xl">
                    <UploadCloud className="w-8 h-8" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">
                      Drop RFP / Tender Document here or <span className="text-indigo-400 underline">browse files</span>
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      Supports PDF and TXT (Extracts Technical Schedules, BoQs, and Product Specifications automatically)
                    </p>
                  </div>
                </label>
              </div>

              {isParsingDoc && (
                <div className="p-6 text-center space-y-3 bg-slate-950/80 border border-slate-800 rounded-xl">
                  <RefreshCw className="w-6 h-6 animate-spin text-indigo-400 mx-auto" />
                  <p className="text-sm font-semibold text-white">Parsing tender clauses & matching Indian Standards...</p>
                  <p className="text-xs text-slate-400">Filtering out EMD/legal noise and extracting technical deliverables</p>
                </div>
              )}

              {!isParsingDoc && tenderUploadNotice && (
                <div className={`p-4 rounded-xl border space-y-2.5 transition-all ${
                  tenderUploadIsError 
                    ? 'bg-rose-950/30 border-rose-500/40 text-rose-200' 
                    : 'bg-amber-950/30 border-amber-500/40 text-amber-200'
                }`}>
                  <div className="flex items-center gap-2">
                    {tenderUploadIsError ? (
                      <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
                    )}
                    <h5 className="text-sm font-bold">
                      {tenderUploadIsError ? 'Document Ingestion Blocked' : 'Tender Ingestion Notice'}
                    </h5>
                  </div>
                  <p className="text-xs leading-relaxed opacity-90">
                    {tenderUploadNotice}
                  </p>
                  {tenderUploadReason && (
                    <div className="text-[11px] font-mono px-2.5 py-1 rounded bg-black/40 border border-white/10 w-fit">
                      Trigger: {tenderUploadReason}
                    </div>
                  )}
                  <div className="pt-1.5 border-t border-white/10 text-[11px] space-y-1 opacity-80">
                    <p className="font-semibold">Recommended Document Requirements:</p>
                    <ul className="list-disc list-inside space-y-0.5">
                      <li>Official GeM / CPPP Tender PDFs or Text files</li>
                      <li>Bill of Quantities (BoQ) schedules or Schedule of Requirements (SOR)</li>
                      <li>Technical specifications specifying materials, grades, or ISI/QCO compliance requirements</li>
                    </ul>
                  </div>
                </div>
              )}

              {parsedItems.length > 0 && (
                <div className="space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-1 border-b border-slate-800">
                    <h4 className="text-sm font-bold text-white flex items-center gap-2">
                      <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
                      <span>Identified Tender Deliverables ({parsedItems.length} items):</span>
                    </h4>
                    <button
                      onClick={() => handleExportGemBoq(parsedItems)}
                      className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg flex items-center gap-1.5 shadow-md shadow-emerald-700/20 transition-all"
                    >
                      <FileSpreadsheet className="w-3.5 h-3.5" />
                      Export Entire Schedule to GeM BoQ (CSV)
                    </button>
                  </div>
                  <div className="space-y-3">
                    {parsedItems.map((item, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition-colors"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-xs font-semibold text-slate-200">
                              {item.tender_item_description}
                            </p>
                            {item.recommendation?.obsolete_warning ? (
                              <span className="mt-1 inline-flex items-center gap-1 text-[11px] font-bold text-rose-400">
                                🔴 Obsolete Standard Cited - Bid Hazard
                              </span>
                            ) : (
                              <span className="mt-1 inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                                🟢 Valid BIS QCO Mandate
                              </span>
                            )}
                          </div>
                          <span className="px-2 py-0.5 text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded shrink-0">
                            {item.recommendation?.primary_standard?.code}
                          </span>
                        </div>
                        <div className="p-2.5 bg-slate-900 rounded-lg text-xs font-mono text-slate-300">
                          {item.recommendation?.gem_tender_clause}
                        </div>
                        <div className="flex items-center justify-between pt-1 text-[11px]">
                          <span className="text-amber-300 font-semibold">
                            {item.recommendation?.mandatory_certification?.scheme}
                          </span>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleExportGemBoq([item])}
                              className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold"
                            >
                              <FileSpreadsheet className="w-3 h-3" /> Export BoQ
                            </button>
                            <button
                              onClick={() => handleCopyClause(item.recommendation?.gem_tender_clause)}
                              className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-semibold"
                            >
                              <Copy className="w-3 h-3" /> Copy Clause
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: BROWSE SECTORS & MINISTRIES */}
          {activeTab === 'sectors' && (
            <div className="space-y-4">
              {/* Directory Filter Switch */}
              <div className="flex items-center gap-2 p-1 bg-slate-950 border border-slate-800 rounded-xl w-fit">
                <button
                  onClick={() => setBrowseMode('category')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                    browseMode === 'category'
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <FolderKanban className="w-3.5 h-3.5" />
                  Browse by Sector ({categories.length})
                </button>
                <button
                  onClick={() => setBrowseMode('ministry')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                    browseMode === 'ministry'
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Building2 className="w-3.5 h-3.5" />
                  Browse by Regulating Ministry QCO ({ministries.length})
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Sidebar Navigation */}
                <div className="md:col-span-1 space-y-1.5 max-h-[500px] overflow-y-auto custom-scrollbar">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block px-1">
                    {browseMode === 'category' ? 'Procurement Sectors' : 'Regulating Ministries'}
                  </span>
                  {browseMode === 'category' ? (
                    categories.map((cat, idx) => (
                      <button
                        key={idx}
                        onClick={() => selectCategory(cat)}
                        className={`w-full text-left px-3 py-2 text-xs font-medium rounded-lg transition-colors flex items-center justify-between ${
                          selectedCategory === cat
                            ? 'bg-indigo-600 text-white font-semibold'
                            : 'bg-slate-950 text-slate-300 hover:bg-slate-800'
                        }`}
                      >
                        <span className="truncate">{cat}</span>
                        <ArrowRight className="w-3.5 h-3.5 opacity-60 shrink-0" />
                      </button>
                    ))
                  ) : (
                    ministries.map((m, idx) => (
                      <button
                        key={idx}
                        onClick={() => selectMinistry(m)}
                        className={`w-full text-left px-3 py-2 text-xs font-medium rounded-lg transition-colors flex items-center justify-between ${
                          selectedMinistry === m
                            ? 'bg-indigo-600 text-white font-semibold'
                            : 'bg-slate-950 text-slate-300 hover:bg-slate-800'
                        }`}
                      >
                        <span className="truncate">{m}</span>
                        <ArrowRight className="w-3.5 h-3.5 opacity-60 shrink-0" />
                      </button>
                    ))
                  )}
                </div>

                {/* Standards Listing */}
                <div className="md:col-span-3 space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <h4 className="text-sm font-bold text-white flex items-center gap-2">
                      <span>{browseMode === 'category' ? selectedCategory : selectedMinistry}</span>
                      <span className="text-xs px-2 py-0.5 bg-slate-800 text-slate-400 rounded-full font-normal">
                        {browseMode === 'category' ? categoryStandards.length : ministryStandards.length} Standards
                      </span>
                    </h4>
                  </div>
                  <div className="space-y-3 max-h-[500px] overflow-y-auto custom-scrollbar">
                    {(browseMode === 'category' ? categoryStandards : ministryStandards).map((std, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition-colors"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <span className="text-sm font-bold text-indigo-400 font-mono">
                              {std.code}
                            </span>
                            <span className="ml-2 text-xs px-2 py-0.5 bg-green-500/10 text-green-400 border border-green-500/20 rounded">
                              {std.latest_edition}
                            </span>
                            {std.mandatory_certification?.is_mandatory && (
                              <span className="ml-2 text-[10px] px-2 py-0.5 bg-amber-500/15 text-amber-300 border border-amber-500/30 rounded font-semibold">
                                Mandatory ISI / CRS
                              </span>
                            )}
                            <h5 className="text-xs font-semibold text-slate-100 mt-1">
                              {std.title}
                            </h5>
                          </div>
                          <button
                            onClick={() => {
                              setQuery(std.code);
                              setActiveTab('search');
                              handleSearch(std.code);
                            }}
                            className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-indigo-900/40 text-slate-200 border border-slate-700 rounded-lg shrink-0 flex items-center gap-1 font-medium transition-colors"
                          >
                            View Full Spec <ArrowRight className="w-3 h-3" />
                          </button>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          {std.gem_tender_clause?.slice(0, 180)}...
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="p-3 sm:p-4 border-t border-slate-800 bg-slate-950 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Grounded in Official Bureau of Indian Standards (BIS) Gazette Notifications & DPIIT QCOs</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors font-medium"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
