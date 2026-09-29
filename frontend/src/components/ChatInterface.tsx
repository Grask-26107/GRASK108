import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  Sparkles,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  BookOpen,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  RotateCcw,
  ShieldCheck,
  AlertTriangle,
  FileSpreadsheet,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Globe,
  Loader2,
  Menu,
  Search,
  UploadCloud,
  FileText,
  ArrowUp,
  Layers,
  Sun,
  Moon,
  Building2
} from 'lucide-react';
import { GeminiStatusIndicator } from './GeminiStatusIndicator';
import { ProcurementCard } from './ProcurementCard';
import { ChatMode, ChatMessage, Citation, UserProfile } from '../types';
import { chatApi, feedbackApi, procurementApi } from '../services/api';
import { SUPPORTED_LANGUAGES } from '../constants/languages';
export { SUPPORTED_LANGUAGES };

interface ChatInterfaceProps {
  currentMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  onSelectCitation: (citation: Citation) => void;
  addToast: (type: 'success' | 'error' | 'info', message: string) => void;
  onToggleSidebar?: () => void;
  onOpenLicenseVerify?: () => void;
  onOpenComplianceAudit?: () => void;
  onOpenNutriScore?: () => void;
  onOpenApplyModal?: (query?: string) => void;
  selectedLanguage: string;
  onLanguageChange: (lang: string) => void;
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  externalQuery?: string | null;
  onClearExternalQuery?: () => void;
  darkMode?: boolean;
  onToggleDarkMode?: () => void;
  user?: UserProfile | null;
  onOpenProfile?: () => void;
  onNavigateToPortal?: () => void;
}

const PROCUREMENT_SAMPLE_PROMPTS = [
  {
    standard: 'IS 1786:2008',
    category: 'Civil & Construction',
    title: 'TMT Steel Rebars Fe 500D (QCO Mandatory)',
    prompt: 'Supply of 50 MT TMT steel rebars Fe 500D for school building construction'
  },
  {
    standard: 'IS 694:2010',
    category: 'Electrical & Power',
    title: 'Fire-Resistant Building Wires (QCO Mandatory)',
    prompt: '2000 fire-resistant electrical cables for hospital'
  },
  {
    standard: 'IS 10322:2019',
    category: 'Lighting & Municipal',
    title: 'Outdoor LED Street Lighting IP66',
    prompt: '45W outdoor LED street lighting luminaire IP66 with 10kV surge protection'
  },
  {
    standard: 'IS 2062:2011',
    category: 'Structural Engineering',
    title: 'Eurocode 3 / ASTM Harmonization',
    prompt: 'Procurement of structural steel sections specified under Eurocode 3 for bridge fabrication'
  },
  {
    standard: 'IS 456:2000',
    category: 'Civil Engineering',
    title: 'Reinforced Concrete M30 Grade Mix',
    prompt: 'Reinforced concrete design and M30 grade mix execution under IS 456'
  },
  {
    standard: 'IS 269:2015',
    category: 'Building Materials',
    title: 'Ordinary Portland Cement 53 Grade',
    prompt: 'Ordinary Portland Cement 53 grade fresh bags conforming to BIS'
  },
  {
    standard: 'IS 4984:2016',
    category: 'Water & Utilities',
    title: 'PE-100 HDPE Water Pipes PN 10',
    prompt: '110mm PE-100 HDPE pipes PN 10 for drinking water transmission'
  },
  {
    standard: 'IS 1786 (हिन्दी)',
    category: 'Multilingual / Indic',
    title: 'स्कूल भवन निर्माण हेतु 12mm TMT सरिया',
    prompt: 'स्कूल भवन निर्माण हेतु 12mm TMT सरिया (IS 1786)'
  }
];

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  currentMode,
  onModeChange,
  onSelectCitation,
  addToast,
  onToggleSidebar,
  selectedLanguage,
  onLanguageChange,
  messages,
  setMessages,
  externalQuery,
  onClearExternalQuery,
  darkMode,
  onToggleDarkMode,
  user,
  onOpenProfile,
  onNavigateToPortal,
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isUploadingTender, setIsUploadingTender] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const tenderFileInputRef = useRef<HTMLInputElement>(null);

  // Handle external query injected from other modals
  useEffect(() => {
    if (externalQuery && externalQuery.trim()) {
      handleSendMessage(externalQuery.trim());
      onClearExternalQuery?.();
    }
  }, [externalQuery]);

  // SIH26108 Centric Welcome Message
  useEffect(() => {
    if (messages.length === 0 || (messages.length === 1 && messages[0].id === 'welcome-01')) {
      setMessages([
        {
          id: 'welcome-01',
          role: 'assistant',
          content:
            `### 🇮🇳 BIS AI Tender Assistant for GeM Procurement (SIH26108)\n\n` +
            `I am your **AI-Powered Recommendation Assistant** for public procurement on **GeM & CPPP**. ` +
            `I help government buyers and procurement committees find mandatory **Indian Standards (BIS codes)**, check quality rules, and generate ready-to-use tender clauses.\n\n` +
            `**Key Features:**\n` +
            `- **Smart Standards Finder:** Matches product names or technical descriptions to official Indian Standards (BIS codes).\n` +
            `- **Mandatory Quality Rules (QCO):** Checks statutory Quality Control Orders (**ISI Mark**, **CRS**, **Hallmarking**) to ensure legal compliance.\n` +
            `- **Related Standards Guide:** Identifies required testing methods, safety rules, and installation standards.\n` +
            `- **1-Click GeM Tender Clauses:** Generates ready-to-paste tender clauses compliant with **GFR Rule 144(1)(i)**.\n` +
            `- **Tender Document (BoQ) Upload:** Upload PDF or text tender files to check items in bulk.\n\n` +
            `*Click any sample query below or type your product requirements to begin:*`,
          mode: currentMode,
          confidence_score: 1.0,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    }
  }, [currentMode]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend?: string) => {
    const message = textToSend || inputMessage;
    if (!message.trim() || loading) return;

    const userMessageId = `usr-${Date.now()}`;
    const newMessages: ChatMessage[] = [
      ...messages,
      {
        id: userMessageId,
        role: 'user',
        content: message,
        timestamp: new Date().toLocaleTimeString(),
      },
    ];

    setMessages(newMessages);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(
        message,
        currentMode,
        undefined,
        newMessages,
        selectedLanguage
      );

      const assistantMsg: ChatMessage = {
        id: response?.id || `ast-${Date.now()}`,
        role: 'assistant',
        content: typeof response?.answer === 'string' ? response.answer : String(response?.answer || ''),
        mode: response?.mode || currentMode,
        citations: Array.isArray(response?.citations) ? response.citations : [],
        table_references: Array.isArray(response?.table_references) ? response.table_references : [],
        confidence_score: typeof response?.confidence_score === 'number' ? response.confidence_score : 0.95,
        refusal_triggered: Boolean(response?.refusal_triggered),
        needs_clarification: Boolean(response?.needs_clarification),
        disambiguation_options: Array.isArray(response?.disambiguation_options) ? response.disambiguation_options : [],
        suggested_followups: Array.isArray(response?.suggested_followups) ? response.suggested_followups : [],
        procurement_recommendation: response?.procurement_recommendation || null,
        language: response?.language || selectedLanguage,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Failed to reach BIS RAG Engine.');
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: '⚠️ **Error:** Unable to connect to the backend server. Please verify that the FastAPI backend is running on `http://127.0.0.1:8000`.',
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleTenderFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const file = files[0];

    const userMsgId = `usr-doc-${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: 'user',
      content: `📄 **Uploaded Tender Document:** \`${file.name}\` (${(file.size / 1024).toFixed(1)} KB)\n*Parsing technical deliverables, BoQ line items, and mapping Indian Standards...*`,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsUploadingTender(true);
    setLoading(true);

    try {
      const res = await procurementApi.uploadTender(file);
      if (res.success && res.items && res.items.length > 0) {
        const assistantMsg: ChatMessage = {
          id: `ast-doc-${Date.now()}`,
          role: 'assistant',
          content: `### 📋 Extracted Tender Items & Indian Standards Mapping\n\nIdentified **${res.total_items_found} procurement deliverables** from \`${file.name}\` and mapped to verified Indian Standards under GFR Rule 144(1)(i).`,
          is_tender_upload: true,
          tender_file_name: file.name,
          tender_items: res.items,
          confidence_score: 0.99,
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
        addToast('success', `Extracted ${res.total_items_found} procurement items from ${file.name}!`);
      } else {
        addToast('error', 'Could not extract procurement items from this document.');
      }
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Failed to parse tender document.');
    } finally {
      setIsUploadingTender(false);
      setLoading(false);
      if (tenderFileInputRef.current) {
        tenderFileInputRef.current.value = '';
      }
    }
  };

  const handleFeedback = async (messageId: string, rating: 'thumbs_up' | 'thumbs_down', queryText?: string, responseText?: string) => {
    try {
      await feedbackApi.submitFeedback(messageId, rating, queryText, responseText, currentMode);
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, feedbackGiven: rating } : m))
      );
      addToast('success', 'Thank you! Feedback logged for Government Accuracy Oversight.');
    } catch (err) {
      addToast('error', 'Failed to submit feedback.');
    }
  };

  const handleCopy = (content: string, id: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    addToast('success', 'Answer copied to clipboard!');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleSpeech = (text: string, id: string, langCode: string = 'en') => {
    if (isSpeaking === id) {
      window.speechSynthesis.cancel();
      setIsSpeaking(null);
      return;
    }
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[#*`_~\[\]]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    const langObj = SUPPORTED_LANGUAGES.find((l) => l.code === langCode);
    if (langObj) utterance.lang = langObj.voice;
    utterance.onend = () => setIsSpeaking(null);
    utterance.onerror = () => setIsSpeaking(null);
    setIsSpeaking(id);
    window.speechSynthesis.speak(utterance);
  };

  const toggleSpeechRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      addToast('error', 'Voice input is not supported in this browser.');
      return;
    }
    if (isListening) {
      setIsListening(false);
      return;
    }
    const recognition = new SpeechRecognition();
    const langObj = SUPPORTED_LANGUAGES.find((l) => l.code === selectedLanguage);
    recognition.lang = langObj ? langObj.voice : 'en-IN';
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      addToast('info', `Listening in ${langObj ? langObj.name : 'English'}... Speak now.`);
    };
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInputMessage(transcript);
      setIsListening(false);
      handleSendMessage(transcript);
    };
    recognition.onerror = () => {
      setIsListening(false);
      addToast('error', 'Speech recognition encountered an issue.');
    };
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const clearChat = () => {
    setMessages([]);
    addToast('info', 'Started fresh consultation session.');
  };

  const toggleCitationDrawer = (id: string) => {
    setExpandedCitations((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="flex flex-col h-full w-full bg-slate-50 dark:bg-slate-950 overflow-hidden select-text font-sans">
      
      {/* Top Main Navigation Header */}
      <div className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-3 sm:px-5 flex items-center justify-between z-10 shrink-0 shadow-xs">
        
        {/* Left: Hamburger & Brand */}
        <div className="flex items-center space-x-2.5 sm:space-x-3">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex items-center gap-1.5 font-bold text-xs"
            title="Open Tools, 17 Technical Departments & Testing Laboratories Menu"
          >
            <Menu className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span className="hidden sm:inline">Menu</span>
          </button>

          <div className="h-5 w-px bg-slate-300 dark:bg-slate-700 hidden sm:block" />

          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-700 via-blue-600 to-indigo-900 border border-amber-400/40 flex items-center justify-center text-white shadow-sm p-1 shrink-0">
              <img src="/bis-emblem.svg" alt="Emblem" className="w-5 h-5 drop-shadow" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <h1 className="font-extrabold text-sm sm:text-base text-slate-900 dark:text-white tracking-tight leading-none">
                  BIS Tender Standards Engine
                </h1>
                <span className="px-1.5 py-0.2 text-[9px] font-bold bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border border-indigo-500/30 rounded">
                  SIH26108
                </span>
              </div>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium hidden md:block">
                AI Recommendation Engine for GeM & CPPP Procurement
              </p>
            </div>
          </div>
        </div>

        {/* Right: Controls & Peanut Status */}
        <div className="flex items-center space-x-2">
          
          {/* Official Government Portal Home Button */}
          {onNavigateToPortal && (
            <button
              onClick={onNavigateToPortal}
              className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:hover:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 transition-colors flex items-center gap-1.5 cursor-pointer shadow-2xs"
              title="Return to Official Government Portal Homepage & Statutory Hub"
            >
              <Building2 className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
              <span className="hidden sm:inline">Portal Home</span>
            </button>
          )}

          {/* New Tender Spec Button */}
          <button
            onClick={clearChat}
            className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-colors flex items-center gap-1"
            title="Start New Tender Specification"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New Spec</span>
          </button>

          {/* Multilingual Selector */}
          <div className="inline-flex items-center space-x-1 px-2 py-1 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700">
            <Globe className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
            <select
              value={selectedLanguage}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer pr-1"
              title="Select Language for Natural Language Tender Queries"
            >
              {SUPPORTED_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code} className="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100">
                  {l.flag} {l.name}
                </option>
              ))}
            </select>
          </div>

          {/* Synchronized Theme Toggle (Outside Menu Bar) */}
          {onToggleDarkMode && (
            <button
              onClick={onToggleDarkMode}
              className="p-1.5 px-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-colors flex items-center gap-1.5 text-xs font-semibold shadow-xs"
              title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
              aria-label="Toggle Theme"
            >
              {darkMode ? (
                <Sun className="w-3.5 h-3.5 text-amber-500 animate-in spin-in-180 duration-200" />
              ) : (
                <Moon className="w-3.5 h-3.5 text-indigo-600 dark:text-blue-400 animate-in spin-in-180 duration-200" />
              )}
              <span className="hidden md:inline text-[11px] font-medium">
                {darkMode ? 'Light' : 'Dark'}
              </span>
            </button>
          )}

          {/* Peanut-Sized Local RAG Status Indicator */}
          <GeminiStatusIndicator addToast={addToast} />

          {/* User Profile & Role Switcher Pill */}
          {user && onOpenProfile && (
            <button
              onClick={onOpenProfile}
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-indigo-50 dark:bg-slate-800 dark:hover:bg-indigo-950/50 border border-slate-300 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500/50 transition-all text-xs cursor-pointer group shadow-2xs"
              title="Click to view profile, switch operational role, or sign out"
            >
              <div className="w-5 h-5 rounded-md bg-indigo-600 group-hover:bg-indigo-700 text-white font-bold flex items-center justify-center text-[10px] shadow-2xs shrink-0">
                {user.name.slice(0, 1).toUpperCase()}
              </div>
              <div className="hidden sm:flex flex-col text-left leading-none">
                <span className="font-bold text-slate-800 dark:text-slate-200 text-[11px] truncate max-w-[85px]">
                  {user.name.split(' ')[0]}
                </span>
                <span className="text-[9px] text-indigo-600 dark:text-indigo-400 font-semibold capitalize">
                  {user.role === 'citizen' ? 'Citizen' : user.role === 'industry' ? 'MSME' : user.role === 'procurement' ? 'GeM' : 'Admin'}
                </span>
              </div>
            </button>
          )}
        </div>
      </div>

      {/* Main Messages Stream Container */}
      <div className="flex-1 overflow-y-auto px-3 sm:px-6 lg:px-8 py-5 space-y-5 max-w-4xl mx-auto w-full custom-scrollbar">
        
        {/* Message Feed */}
        {messages.map((msg) => {
          const isAssistant = msg.role === 'assistant';
          const hasCitations = msg.citations && msg.citations.length > 0;
          const isRefusal = msg.refusal_triggered;

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isAssistant ? 'items-start' : 'items-end'} animate-in fade-in duration-200`}
            >
              {/* Message Bubble Container */}
              <div
                className={`w-full max-w-[96%] sm:max-w-[90%] rounded-2xl p-4 sm:p-5 shadow-sm border transition-all ${
                  isAssistant
                    ? isRefusal
                      ? 'bg-rose-50/90 dark:bg-rose-950/30 border-rose-200 dark:border-rose-900/60 text-slate-900 dark:text-slate-100'
                      : 'bg-white dark:bg-slate-900 border-slate-200/90 dark:border-slate-800 text-slate-900 dark:text-slate-100'
                    : 'bg-indigo-600 text-white border-indigo-700 self-end shadow-md shadow-indigo-900/20'
                }`}
              >
                {/* Assistant Message Header */}
                {isAssistant && (
                  <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 dark:border-slate-800 text-xs">
                    <div className="flex items-center space-x-2">
                      <div className="w-5 h-5 rounded-md bg-gradient-to-tr from-indigo-700 to-blue-600 flex items-center justify-center text-white text-[10px] font-black shadow-sm">
                        🇮🇳
                      </div>
                      <span className="font-extrabold text-slate-900 dark:text-white tracking-tight">
                        Tender Specification Assistant
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
                        SIH26108
                      </span>
                    </div>

                    {msg.confidence_score !== undefined && (
                      <div className="flex items-center space-x-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                        <span>Confidence: {Math.round(msg.confidence_score * 100)}%</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Markdown Text */}
                <div className="markdown-content text-sm leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {typeof msg.content === 'string' ? msg.content : String(msg.content || '')}
                  </ReactMarkdown>
                </div>

                {/* SIH26108 Interactive Procurement Specification Card */}
                {(msg.procurement_recommendation || msg.is_tender_upload) && (
                  <ProcurementCard
                    recommendation={msg.procurement_recommendation}
                    isTenderUpload={msg.is_tender_upload}
                    tenderItems={msg.tender_items}
                    tenderFileName={msg.tender_file_name}
                    addToast={addToast}
                  />
                )}

                {/* Grounded Citations Accordion */}
                {isAssistant && hasCitations && (
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <button
                      onClick={() => toggleCitationDrawer(msg.id)}
                      className="flex items-center justify-between w-full text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:opacity-80 py-1"
                    >
                      <div className="flex items-center space-x-1.5">
                        <BookOpen className="w-3.5 h-3.5" />
                        <span>Authoritative BIS Citations ({msg.citations?.length})</span>
                      </div>
                      {expandedCitations[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {expandedCitations[msg.id] && (
                      <div className="mt-2 space-y-2 pt-2">
                        {msg.citations?.map((cit, idx) => (
                          <div
                            key={idx}
                            onClick={() => onSelectCitation(cit)}
                            className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 hover:border-indigo-500 cursor-pointer transition-all text-xs"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-bold text-indigo-600 dark:text-indigo-400 font-mono">
                                {cit.is_code}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                Page {cit.page_number} • {cit.clause}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">
                              {cit.snippet}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Interactive Dynamic Follow-up Suggestions */}
                {isAssistant && msg.suggested_followups && msg.suggested_followups.length > 0 && (
                  <div className="mt-3.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <div className="flex items-center space-x-1.5 text-xs font-semibold text-amber-600 dark:text-amber-400 mb-2">
                      <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                      <span>Suggested Procurement Inquiries:</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.suggested_followups.map((followup, fIdx) => (
                        <button
                          key={fIdx}
                          type="button"
                          onClick={() => handleSendMessage(followup)}
                          className="text-left px-3 py-1.5 rounded-xl border border-amber-200 dark:border-amber-800/60 bg-amber-50/70 dark:bg-amber-950/30 hover:bg-amber-100 dark:hover:bg-amber-900/50 hover:border-amber-400 text-amber-900 dark:text-amber-200 text-xs font-medium transition-all shadow-2xs flex items-center space-x-1.5 group cursor-pointer"
                        >
                          <span>{followup}</span>
                          <span className="opacity-0 group-hover:opacity-100 text-amber-600 dark:text-amber-400 transition-opacity">→</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Toolbar on Assistant Messages */}
                {isAssistant && (
                  <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                    <span className="text-[10px]">{msg.timestamp}</span>

                    <div className="flex items-center space-x-1.5">
                      {/* Copy */}
                      <button
                        onClick={() => handleCopy(msg.content, msg.id)}
                        className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
                        title="Copy answer"
                      >
                        {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>

                      {/* Text to Speech */}
                      <button
                        onClick={() => toggleSpeech(msg.content, msg.id, msg.language)}
                        className={`p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ${
                          isSpeaking === msg.id ? 'text-indigo-600 dark:text-indigo-400 animate-pulse' : 'text-slate-400 hover:text-slate-700'
                        }`}
                        title={isSpeaking === msg.id ? 'Stop reading' : 'Read aloud in native language'}
                      >
                        {isSpeaking === msg.id ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                      </button>

                      {/* Thumbs Up */}
                      <button
                        onClick={() => handleFeedback(msg.id, 'thumbs_up', messages[messages.indexOf(msg) - 1]?.content, msg.content)}
                        disabled={msg.feedbackGiven !== undefined && msg.feedbackGiven !== null}
                        className={`p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ${
                          msg.feedbackGiven === 'thumbs_up'
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : 'text-slate-400 hover:text-emerald-600'
                        }`}
                        title="Accurate Grounding"
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                      </button>

                      {/* Thumbs Down */}
                      <button
                        onClick={() => handleFeedback(msg.id, 'thumbs_down', messages[messages.indexOf(msg) - 1]?.content, msg.content)}
                        disabled={msg.feedbackGiven !== undefined && msg.feedbackGiven !== null}
                        className={`p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ${
                          msg.feedbackGiven === 'thumbs_down'
                            ? 'text-rose-600 dark:text-rose-400'
                            : 'text-slate-400 hover:text-rose-600'
                        }`}
                        title="Report Discrepancy"
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Starter Prompts & Upload Tender Box when only welcome message exists */}
        {messages.length <= 1 && (
          <div className="pt-2 pb-4 space-y-4">
            
            {/* Direct Upload Tender Hero Card */}
            <div className="p-4 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-indigo-600/20 border border-indigo-500/30 rounded-xl text-indigo-400">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white">
                    Upload Tender Document / BoQ (Bill of Quantities)
                  </h4>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Upload an RFP or procurement schedule (.pdf or .txt) to extract line items and batch-recommend Indian Standards.
                  </p>
                </div>
              </div>

              <button
                onClick={() => tenderFileInputRef.current?.click()}
                disabled={isUploadingTender || loading}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/30 active:scale-98"
              >
                <UploadCloud className="w-4 h-4" />
                <span>{isUploadingTender ? 'Analyzing Document...' : 'Upload Tender (PDF / TXT)'}</span>
              </button>
            </div>

            {/* Quick Procurement Templates */}
            <div>
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-2.5 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span>High-Demand Public Procurement Specifications (Click to test):</span>
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {PROCUREMENT_SAMPLE_PROMPTS.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(item.prompt)}
                    className="text-left p-3.5 rounded-2xl bg-white dark:bg-slate-900 hover:bg-indigo-50/50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-800 hover:border-indigo-500/60 text-xs cursor-pointer group transition-all shadow-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[10px] font-bold text-indigo-600 dark:text-indigo-400">
                        {item.standard}
                      </span>
                      <span className="text-[10px] text-slate-400 font-medium">
                        {item.category}
                      </span>
                    </div>
                    <span className="font-semibold text-slate-900 dark:text-slate-100 block mt-1">
                      {item.title}
                    </span>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1 mt-0.5">
                      {item.prompt}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center space-x-2 text-slate-500 dark:text-slate-400 text-xs p-3">
            <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Evaluating semantic specifications, allied test codes & mandatory QCO compliance...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Floating Centered Bottom Input Bar */}
      <div className="p-3 sm:p-4 shrink-0 bg-gradient-to-t from-white via-white to-transparent dark:from-slate-950 dark:via-slate-950 dark:to-transparent">
        <div className="max-w-3xl mx-auto w-full">
          
          {/* Quick Suggestions Strip when in active conversation */}
          {messages.length > 1 && (
            <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-1 scrollbar-none">
              <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center space-x-1 shrink-0">
                <Sparkles className="w-3 h-3 text-amber-500" />
                <span>Templates:</span>
              </span>
              {PROCUREMENT_SAMPLE_PROMPTS.slice(0, 4).map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSendMessage(item.prompt)}
                  className="shrink-0 px-2.5 py-1 rounded-xl text-[11px] font-medium bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:bg-indigo-50 hover:text-indigo-700 dark:hover:bg-indigo-950/60 dark:hover:text-indigo-300 border border-slate-200 dark:border-slate-800 transition-colors truncate max-w-[240px]"
                  title={item.prompt}
                >
                  {item.title}
                </button>
              ))}
            </div>
          )}

          {/* Hidden File Input for Direct Tender Uploads */}
          <input
            type="file"
            ref={tenderFileInputRef}
            accept=".pdf,.txt"
            onChange={handleTenderFileUpload}
            className="hidden"
          />

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="relative bg-white dark:bg-slate-900 rounded-2xl border border-slate-300 dark:border-slate-800 shadow-xl flex items-center p-2 transition-all focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/20"
          >
            {/* Direct Tender Upload Button */}
            <button
              type="button"
              onClick={() => tenderFileInputRef.current?.click()}
              disabled={loading || isUploadingTender}
              className="p-2 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 hover:bg-indigo-50 dark:hover:bg-indigo-950/60 rounded-xl transition-all flex items-center gap-1 shrink-0 text-xs font-semibold"
              title="Upload Tender RFP or BoQ Document (PDF / TXT)"
            >
              <UploadCloud className="w-5 h-5" />
              <span className="hidden md:inline text-[11px]">Upload Tender</span>
            </button>

            {/* Input Text Field */}
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Enter product description, technical specifications, or tender requirements (supports Hindi & regional languages)..."
              className="flex-1 bg-transparent px-3 py-2 text-xs sm:text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none"
              disabled={loading || isUploadingTender}
            />

            {/* Microphone Voice Input */}
            <button
              type="button"
              onClick={toggleSpeechRecognition}
              className={`p-2 rounded-xl border transition-all mr-1 ${
                isListening
                  ? 'bg-rose-500 text-white border-rose-600 animate-pulse shadow-md shadow-rose-500/30'
                  : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 border-transparent hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
              title={isListening ? 'Stop Listening' : 'Voice Input (Web Speech API)'}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!inputMessage.trim() || loading || isUploadingTender}
              className="p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-200 dark:disabled:bg-slate-800 text-white disabled:text-slate-400 transition-all font-semibold shadow-sm active:scale-95"
              title="Send Specification Query"
            >
              <ArrowUp className="w-4 h-4" />
            </button>
          </form>

          <p className="text-[10px] text-center text-slate-400 dark:text-slate-500 mt-2">
            GRASK AI evaluates specifications against official Gazette QCOs and Indian Standards under GFR Rule 144(1)(i).
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
