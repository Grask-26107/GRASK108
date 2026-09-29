import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  X,
  ShieldCheck,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  Volume2,
  VolumeX,
  Upload,
  Camera,
  RotateCcw,
  Sparkles,
  Heart,
  Baby,
  Activity,
  Wheat,
  Globe,
  Loader2,
  ChevronDown,
  ChevronUp,
  FileText,
  Info
} from 'lucide-react';
import { standardsApi } from '../services/api';
import { NutriAnalyzeResult, NutriPersona } from '../types';
import { SUPPORTED_LANGUAGES } from '../constants/languages';
import Tesseract from 'tesseract.js';

interface NutriScoreModalProps {
  isOpen: boolean;
  onClose: () => void;
  addToast: (type: 'success' | 'error' | 'info', message: string) => void;
}

const PRESET_FOODS = [
  {
    name: '🍟 Instant Fried Noodles (High Sodium & MSG)',
    text: `Ingredients: Refined Wheat Flour (Maida), Palm Oil, Salt, Wheat Gluten, Mineral (Calcium Carbonate), Thickener (INS 508), Acidity Regulators (INS 501(i), INS 500(i)), Monosodium Glutamate (INS 621), Tartrazine (INS 102), Sunset Yellow (INS 110), Invert Sugar Syrup.
Per 100g: Energy 450 kcal, Protein 8.5g, Carbohydrates 62.0g, Total Sugar 3.5g, Added Sugar 2.0g, Total Fat 19.5g, Saturated Fat 9.8g, Trans Fat 0.3g, Sodium 940mg.`
  },
  {
    name: '🍪 Chocolate Cream Biscuits (High Sugar & Trans Fat)',
    text: `Ingredients: Refined Wheat Flour, Sugar, Hydrogenated Palm Oil, High Fructose Corn Syrup, Invert Sugar Syrup, Cocoa Solids, Maltodextrin, Emulsifier (INS 322), Synthetic Food Colour (INS 122), Artificial Flavouring Substances, Antioxidant (INS 320).
Per 100g: Energy 495 kcal, Protein 5.0g, Carbohydrates 69.0g, Total Sugar 34.0g, Added Sugar 31.0g, Total Fat 22.0g, Saturated Fat 11.5g, Trans Fat 0.4g, Sodium 420mg.`
  },
  {
    name: '🧃 Commercial Fruit Drink (Hidden Sugar & Coal-Tar Color)',
    text: `Ingredients: Water, Sugar, Liquid Glucose, Apple Juice Concentrate, Acidity Regulator (INS 330), Preservative (INS 211 Sodium Benzoate), Synthetic Colour (INS 110 Sunset Yellow FCF, INS 102 Tartrazine), Artificial Sweetener (INS 955 Sucralose).
Per 100g: Energy 68 kcal, Protein 0.1g, Carbohydrates 16.5g, Total Sugar 15.8g, Added Sugar 14.5g, Total Fat 0g, Saturated Fat 0g, Trans Fat 0g, Sodium 45mg.`
  },
  {
    name: '🌾 100% Whole Grain Rolled Oats (A-Grade Secure)',
    text: `Ingredients: 100% Whole Grain Rolled Oats. Contains soluble dietary fiber (Beta-Glucan).
Per 100g: Energy 389 kcal, Protein 13.5g, Carbohydrates 66.0g, Total Sugar 1.0g, Added Sugar 0g, Total Fat 6.9g, Saturated Fat 1.2g, Trans Fat 0g, Sodium 5mg, Dietary Fiber 10.5g.`
  },
  {
    name: '🥣 Packaged Health Cereal Mix (Clean Grain Audit)',
    text: `Ingredients: Rice Flour, Milk Solids, Maltodextrin, Sugar, Soybean Oil, Mineral Mix (Iron, Zinc), Vitamin C, Vanilla Flavour.
Per 100g: Energy 415 kcal, Protein 12.0g, Carbohydrates 72.0g, Total Sugar 18.0g, Added Sugar 14.0g, Total Fat 8.5g, Saturated Fat 3.5g, Trans Fat 0.05g, Sodium 160mg.`
  }
];

export const NutriScoreModal: React.FC<NutriScoreModalProps> = ({ isOpen, onClose, addToast }) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'manual'>('upload');
  const [inputText, setInputText] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NutriAnalyzeResult | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showRawIngredients, setShowRawIngredients] = useState(false);
  const [isScanningOcr, setIsScanningOcr] = useState(false);
  const [ocrProgress, setOcrProgress] = useState(0);

  // Camera capture state
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsCameraActive(false);
  }, []);

  useEffect(() => {
    return () => {
      stopCamera();
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [stopCamera]);

  const startCamera = async () => {
    try {
      setIsCameraActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      setIsCameraActive(false);
      addToast('error', 'Camera access denied or unavailable.');
    }
  };

  const runLocalOcr = async (imageSrc: string) => {
    try {
      setIsScanningOcr(true);
      setOcrProgress(15);
      const { data } = await Tesseract.recognize(imageSrc, 'eng', {
        logger: (m) => {
          if (m.status === 'recognizing text' && typeof m.progress === 'number') {
            setOcrProgress(Math.round(m.progress * 100));
          }
        }
      });
      if (data && data.text && data.text.trim().length > 10) {
        setInputText(data.text.trim());
        addToast('success', 'Nutrition table & ingredients extracted via local OCR scanner!');
      } else {
        addToast('info', 'Image uploaded. Click "Analyze Food Safety" to inspect.');
      }
    } catch (ocrErr) {
      console.warn('Local OCR scan fallback:', ocrErr);
      addToast('info', 'Image uploaded. Click "Analyze Food Safety" to inspect.');
    } finally {
      setIsScanningOcr(false);
      setOcrProgress(0);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 1280;
    canvas.height = videoRef.current.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const b64 = canvas.toDataURL('image/jpeg', 0.9);
      setImagePreview(b64);
      setResult(null);
      setInputText('');
      stopCamera();
      addToast('info', 'Scanning label photo with OCR...');
      runLocalOcr(b64);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      addToast('error', 'Please upload a valid image (JPEG, PNG, WEBP).');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const b64 = event.target?.result as string;
      setImagePreview(b64);
      setResult(null);
      setInputText('');
      addToast('info', 'Scanning uploaded label with OCR...');
      runLocalOcr(b64);
    };
    reader.readAsDataURL(file);
  };

  const handleLoadPreset = (preset: typeof PRESET_FOODS[0]) => {
    setInputText(preset.text);
    setActiveTab('manual');
    setImagePreview(null);
    setResult(null);
    addToast('info', `Loaded preset: ${preset.name}`);
  };

  const handleAnalyze = async () => {
    if (!imagePreview && !inputText.trim()) {
      addToast('error', 'Please upload a photo of the food label OR enter details manually.');
      return;
    }

    setLoading(true);
    setResult(null);
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }

    try {
      const res = await standardsApi.analyzeIngredients({
        text: inputText.trim() || undefined,
        image_base64: imagePreview || undefined,
        persona: 'general',
        language: selectedLanguage
      });

      setResult(res);
      if (res.status === 'IRRELEVANT_DATA' || res.is_relevant === false) {
        addToast('error', `Irrelevant Data: ${res.relevance_reason || 'Uploaded item is not a packaged food commodity.'}`);
      } else {
        addToast('success', `Analysis complete! Verdict: ${res.verdict}`);
      }
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Failed to analyze nutrition profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = async (newLang: string) => {
    setSelectedLanguage(newLang);
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }

    if (result && (inputText.trim() || imagePreview)) {
      setLoading(true);
      try {
        const res = await standardsApi.analyzeIngredients({
          text: inputText.trim() || undefined,
          image_base64: imagePreview || undefined,
          persona: 'general',
          language: newLang
        });
        setResult(res);
        const langObj = SUPPORTED_LANGUAGES.find((l) => l.code === newLang);
        addToast('info', `Language updated to ${langObj?.name || newLang} (${langObj?.native || ''}). Click 🔊 to listen.`);
      } catch (err: any) {
        console.error('Failed to re-translate analysis:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  const toggleVoiceVerdict = () => {
    if (!result) return;
    if (!('speechSynthesis' in window)) {
      addToast('error', 'Speech synthesis is not supported on this browser.');
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      window.speechSynthesis.cancel();
      const textToSpeak = result.spoken_summary || result.summary_verdict;
      const utterance = new SpeechSynthesisUtterance(textToSpeak);

      const targetVoice = SUPPORTED_LANGUAGES.find((l) => l.code === (result.spoken_language || selectedLanguage)) || SUPPORTED_LANGUAGES[0];
      utterance.lang = targetVoice.voice;
      utterance.rate = 0.95;

      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade?.toUpperCase()) {
      case 'A':
        return 'bg-emerald-600 text-white shadow-emerald-500/30';
      case 'B':
        return 'bg-teal-500 text-white shadow-teal-500/30';
      case 'C':
        return 'bg-amber-500 text-white shadow-amber-500/30';
      case 'D':
        return 'bg-orange-500 text-white shadow-orange-500/30';
      case 'E':
        return 'bg-rose-600 text-white shadow-rose-500/30';
      default:
        return 'bg-slate-500 text-white';
    }
  };

  const getVerdictStyle = (verdict: string) => {
    switch (verdict?.toUpperCase()) {
      case 'HARMFUL':
        return {
          bg: 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-100',
          badge: 'bg-rose-600 text-white border-rose-700',
          icon: <AlertTriangle className="w-7 h-7 text-rose-600 dark:text-rose-400 shrink-0" />
        };
      case 'CAUTION':
        return {
          bg: 'bg-amber-50 dark:bg-amber-950/40 border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-100',
          badge: 'bg-amber-500 text-white border-amber-600',
          icon: <AlertCircle className="w-7 h-7 text-amber-600 dark:text-amber-400 shrink-0" />
        };
      case 'SECURE':
      default:
        return {
          bg: 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-100',
          badge: 'bg-emerald-600 text-white border-emerald-700',
          icon: <ShieldCheck className="w-7 h-7 text-emerald-600 dark:text-emerald-400 shrink-0" />
        };
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-200">
      <div className="relative bg-white dark:bg-slate-900 w-full max-w-5xl rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[92vh]">
        {/* National Tricolor Top Accent */}
        <div className="h-1.5 w-full flex shrink-0 shadow-sm">
          <div className="w-1/3 bg-[#FF9933]"></div>
          <div className="w-1/3 bg-[#FFFFFF]"></div>
          <div className="w-1/3 bg-[#138808]"></div>
        </div>

        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-950/40 shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-700 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
              <span className="text-xl">🥗</span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base sm:text-lg font-black tracking-tight text-slate-900 dark:text-white">
                  FSSAI Nutri-Score & Hidden Ingredient Decrypter
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                  FOPL Safety
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                Audits high sodium, trans fats, palm oil, hidden sugars, and hazardous chemical additives
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              stopCamera();
              onClose();
            }}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          {/* Preset Quick Starters */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span>Quick Test Samples (Instant 1-Click Load):</span>
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {PRESET_FOODS.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => handleLoadPreset(preset)}
                  className="text-left p-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700/70 text-xs font-semibold text-slate-700 dark:text-slate-200 transition-all hover:border-emerald-500 hover:text-emerald-600 dark:hover:text-emerald-400 truncate"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Universal Inspection & Language Configuration */}
          <div className="bg-slate-50 dark:bg-slate-800/40 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-sm shrink-0">
                🌿
              </div>
              <div>
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">
                  Universal Ingredient & FSSAI Statutory Limit Audit
                </span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">
                  Direct ingredient extraction, health advantage/risk analysis, and government safe ceilings
                </span>
              </div>
            </div>

            {/* Spoken Voice Language Selector */}
            <div className="flex items-center space-x-2 shrink-0">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center space-x-1.5 whitespace-nowrap">
                <Globe className="w-3.5 h-3.5 text-blue-500" />
                <span>Spoken Voice & Text:</span>
              </label>
              <select
                value={selectedLanguage}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/30"
              >
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.flag} {lang.name} ({lang.native})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Input Method Tabs */}
          <div>
            <div className="flex border-b border-slate-200 dark:border-slate-800 mb-4">
              <button
                type="button"
                onClick={() => setActiveTab('upload')}
                className={`pb-2.5 px-4 font-bold text-xs flex items-center space-x-2 border-b-2 transition-all ${
                  activeTab === 'upload'
                    ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
                }`}
              >
                <Camera className="w-4 h-4" />
                <span>Photo Upload & Camera Scan</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('manual')}
                className={`pb-2.5 px-4 font-bold text-xs flex items-center space-x-2 border-b-2 transition-all ${
                  activeTab === 'manual'
                    ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>Text / Ingredient Typing</span>
              </button>
            </div>

            {/* Tab 1: Image Upload / Camera */}
            {activeTab === 'upload' && (
              <div className="space-y-3">
                {isCameraActive ? (
                  <div className="relative rounded-2xl overflow-hidden bg-black border-2 border-emerald-500 flex flex-col items-center">
                    <video ref={videoRef} className="w-full max-h-80 object-cover" playsInline muted />
                    <div className="p-3 bg-slate-950/80 w-full flex items-center justify-center space-x-3">
                      <button
                        type="button"
                        onClick={capturePhoto}
                        className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center space-x-1.5 shadow-lg"
                      >
                        <Camera className="w-4 h-4" />
                        <span>Snap Label Photo</span>
                      </button>
                      <button
                        type="button"
                        onClick={stopCamera}
                        className="px-4 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : imagePreview ? (
                  <div className="space-y-3">
                    <div className="relative rounded-2xl border border-slate-200 dark:border-slate-800 p-3 bg-slate-50 dark:bg-slate-800/50 flex flex-col sm:flex-row items-center gap-4">
                      <img
                        src={imagePreview}
                        alt="Food Label"
                        className="max-h-48 rounded-xl object-contain border border-slate-300 dark:border-slate-700"
                      />
                      <div className="flex-1 space-y-2 text-center sm:text-left">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white">Label Image Attached</h4>
                        {isScanningOcr ? (
                          <div className="space-y-1.5 py-1">
                            <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              <span>Scanning packaging label with local OCR ({ocrProgress}%)...</span>
                            </div>
                            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                              <div
                                className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300"
                                style={{ width: `${Math.max(ocrProgress, 15)}%` }}
                              ></div>
                            </div>
                          </div>
                        ) : (
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            {inputText ? 'Ingredients & nutrition table extracted successfully.' : 'Click "Analyze Food Safety" to inspect.'}
                          </p>
                        )}
                        <div className="flex items-center justify-center sm:justify-start space-x-2 pt-1">
                          <button
                            type="button"
                            onClick={() => {
                              setImagePreview(null);
                              setInputText('');
                            }}
                            className="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-600 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 hover:bg-rose-100"
                          >
                            Remove Image
                          </button>
                          <button
                            type="button"
                            onClick={startCamera}
                            className="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 hover:bg-slate-100"
                          >
                            Retake Camera
                          </button>
                        </div>
                      </div>
                    </div>

                    {inputText && (
                      <div className="p-3 bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700/70 shadow-sm text-left">
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-[11px] font-bold text-slate-700 dark:text-slate-200 flex items-center space-x-1.5">
                            <FileText className="w-3.5 h-3.5 text-blue-500" />
                            <span>Scanned Text (Extracted from photo via OCR):</span>
                          </span>
                          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full">
                            Auto-Scanned
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-300 line-clamp-3 font-mono bg-slate-50 dark:bg-slate-900/80 p-2.5 rounded-xl border border-slate-200 dark:border-slate-800">
                          {inputText}
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-emerald-500 rounded-3xl p-8 text-center transition-colors bg-slate-50/50 dark:bg-slate-800/30">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileUpload}
                      accept="image/*"
                      className="hidden"
                    />
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 mx-auto flex items-center justify-center mb-3">
                      <Upload className="w-6 h-6" />
                    </div>
                    <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                      Upload food packaging back label
                    </h3>
                    <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-4">
                      Snap or upload the Nutrition Information table and Ingredients list on chips, biscuits, oils, drinks, or infant food.
                    </p>
                    <div className="flex items-center justify-center space-x-3">
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center space-x-1.5 shadow-sm"
                      >
                        <Upload className="w-3.5 h-3.5" />
                        <span>Choose Photo File</span>
                      </button>
                      <button
                        type="button"
                        onClick={startCamera}
                        className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center space-x-1.5 shadow-sm"
                      >
                        <Camera className="w-3.5 h-3.5" />
                        <span>Live Camera Scan</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Tab 2: Manual Text Entry */}
            {activeTab === 'manual' && (
              <div className="space-y-2">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Paste or type ingredients (e.g. Refined Wheat Flour, Palm Oil, Sugar, Salt, INS 102, INS 621 MSG, Invert Sugar Syrup) and nutrition facts (e.g. Energy 450 kcal, Added Sugar 24g, Sodium 850mg)..."
                  rows={5}
                  className="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-2xl p-3.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                />
                <p className="text-[11px] text-slate-400">
                  Tip: Include both the Ingredients statement and the Nutrition facts per 100g for full FSSAI grading.
                </p>
              </div>
            )}
          </div>

          {/* Action Button */}
          <div className="flex justify-end pt-1">
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={loading || (!imagePreview && !inputText.trim())}
              className="px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 disabled:opacity-50 text-white text-xs font-black tracking-wide shadow-lg shadow-emerald-600/20 flex items-center space-x-2 active:scale-[0.99] transition-all"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Auditing Nutrition & Ingredients...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Analyze Food Safety (Harmful vs Secure)</span>
                </>
              )}
            </button>
          </div>

          {/* Results Section */}
          {result && (result.status === 'IRRELEVANT_DATA' || result.is_relevant === false) && (
            <div className="p-5 rounded-3xl border border-rose-300 dark:border-rose-900 bg-rose-50/95 dark:bg-rose-950/70 shadow-lg space-y-3 animate-in fade-in slide-in-from-bottom-2">
              <div className="flex items-start space-x-3.5">
                <span className="p-2.5 rounded-2xl bg-rose-100 dark:bg-rose-900/60 text-rose-600 dark:text-rose-300 shrink-0">
                  <AlertTriangle className="w-6 h-6" />
                </span>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-rose-600 text-white shadow-sm">
                      IRRELEVANT DATA DETECTED
                    </span>
                    {result.detected_subject && (
                      <span className="text-xs font-bold text-rose-800 dark:text-rose-200">
                        Subject: {result.detected_subject}
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-extrabold text-rose-900 dark:text-rose-100 mt-2">
                    {result.product_name || 'Non-Food Item Uploaded'}
                  </h3>
                  <p className="text-xs text-rose-800 dark:text-rose-200 mt-1 leading-relaxed">
                    {result.relevance_reason || result.summary_verdict}
                  </p>
                </div>
              </div>

              <div className="text-[11px] text-rose-700 dark:text-rose-300 bg-white/80 dark:bg-slate-900/70 p-3 rounded-2xl border border-rose-200 dark:border-rose-900/60 leading-relaxed">
                <strong>Nutri-Score Guidelines:</strong> Please upload a photo of a packaged food label, nutritional information table, or ingredients list. Photos of vehicles, machinery, electronics, landscapes, or faces cannot be analyzed for nutritional safety.
              </div>
            </div>
          )}

          {result && result.status !== 'IRRELEVANT_DATA' && result.is_relevant !== false && (
            <div className="space-y-5 pt-4 border-t border-slate-200 dark:border-slate-800 animate-in fade-in slide-in-from-bottom-2 duration-300">
              {/* Definitive Verdict Banner */}
              {(() => {
                const style = getVerdictStyle(result.verdict);
                return (
                  <div className={`p-4 sm:p-5 rounded-3xl border-2 ${style.bg} shadow-md`}>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-start space-x-3.5">
                        {style.icon}
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className={`px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider ${style.badge} shadow-sm`}>
                              VERDICT: {result.verdict}
                            </span>
                            <span className="text-xs font-bold opacity-75">
                              {result.product_name}
                            </span>
                          </div>
                          <p className="text-xs font-medium mt-1.5 leading-relaxed">
                            {result.summary_verdict}
                          </p>
                        </div>
                      </div>

                      {/* Text to Speech Voice Trigger */}
                      <button
                        type="button"
                        onClick={toggleVoiceVerdict}
                        className={`px-4 py-2.5 rounded-2xl text-xs font-bold flex items-center justify-center space-x-2 shrink-0 transition-all border ${
                          isSpeaking
                            ? 'bg-rose-500 text-white border-rose-600 animate-pulse shadow-md shadow-rose-500/30'
                            : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-sm'
                        }`}
                        title="Listen to Verdict aloud"
                      >
                        {isSpeaking ? (
                          <>
                            <VolumeX className="w-4 h-4" />
                            <span>Stop Voice</span>
                          </>
                        ) : (
                          <>
                            <Volume2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                            <span>🔊 Listen Verdict ({SUPPORTED_LANGUAGES.find(l => l.code === (result.spoken_language || selectedLanguage))?.name})</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                );
              })()}

              {/* FSSAI Nutri-Score Grade Bar */}
              <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-3xl border border-slate-200 dark:border-slate-800">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-xs font-extrabold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
                      FSSAI Front-of-Pack Nutri-Score
                    </h3>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Calculated from energy, saturated fat, sugar, sodium penalties vs protein and dietary fiber points.
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Score Points:</span>
                    <span className="ml-1 text-sm font-black text-slate-800 dark:text-slate-100 font-mono">
                      {result.nutri_score_points}
                    </span>
                  </div>
                </div>

                {/* 5-Grade Score Visualizer */}
                <div className="grid grid-cols-5 gap-2 text-center">
                  {[
                    { grade: 'A', desc: 'Excellent', color: 'bg-emerald-600' },
                    { grade: 'B', desc: 'Good', color: 'bg-teal-500' },
                    { grade: 'C', desc: 'Moderate', color: 'bg-amber-500' },
                    { grade: 'D', desc: 'Caution (HFSS)', color: 'bg-orange-500' },
                    { grade: 'E', desc: 'Harmful (High HFSS)', color: 'bg-rose-600' }
                  ].map((item) => {
                    const isSelected = result.nutri_score_grade?.toUpperCase() === item.grade;
                    return (
                      <div
                        key={item.grade}
                        className={`p-2.5 rounded-2xl border transition-all ${
                          isSelected
                            ? `${item.color} text-white ring-4 ring-slate-900/20 dark:ring-white/20 scale-105 shadow-md font-black`
                            : 'bg-white dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700/80 opacity-60'
                        }`}
                      >
                        <span className="text-xl font-black block">{item.grade}</span>
                        <span className="text-[10px] block mt-0.5 leading-tight font-semibold">
                          {item.desc}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Decrypted Findings Highlights Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {/* 1. Hidden Added Sugars */}
                <div className="p-4 rounded-2xl border bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700/80">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 dark:border-slate-700">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                      <span>🍬</span>
                      <span>Hidden Added Sugars Decrypted</span>
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      result.hidden_sugars.length > 0 ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                    }`}>
                      {result.hidden_sugars.length} Detected
                    </span>
                  </div>

                  {result.hidden_sugars.length > 0 ? (
                    <div className="space-y-2">
                      {result.hidden_sugars.map((s, idx) => (
                        <div key={idx} className="p-2 rounded-xl bg-rose-50/70 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/40 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-rose-700 dark:text-rose-300">{s.name}</span>
                            <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.2 bg-rose-200 dark:bg-rose-900/80 text-rose-900 dark:text-rose-200 rounded">
                              {s.category}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1 leading-tight">
                            {s.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 text-xs text-emerald-600 dark:text-emerald-400 py-2">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>No hidden syrups or deceptive sweeteners identified.</span>
                    </div>
                  )}
                </div>

                {/* 2. Palm Oil & Fat Quality */}
                <div className="p-4 rounded-2xl border bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700/80">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 dark:border-slate-700">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                      <span>🛢️</span>
                      <span>Fat Profile & Palm Oil Check</span>
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      result.has_palm_oil ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                    }`}>
                      {result.has_palm_oil ? 'Palm Oil Present' : 'Palm Free'}
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    {result.has_palm_oil ? (
                      <div className="p-2 rounded-xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/40">
                        <span className="font-bold text-amber-800 dark:text-amber-200">Atherogenic Fat Warning:</span>
                        <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1 leading-tight">
                          {result.palm_oil_details}
                        </p>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 py-1">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>No palm oil or cheap palmolein fraction detected.</span>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-2 pt-1">
                      <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700 text-center">
                        <span className="text-[10px] text-slate-400 block">Saturated Fat</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">
                          {result.saturated_fat_g !== null && result.saturated_fat_g !== undefined ? `${result.saturated_fat_g}g / 100g` : 'Not Stated'}
                        </span>
                      </div>
                      <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700 text-center">
                        <span className="text-[10px] text-slate-400 block">Trans Fat</span>
                        <span className={`font-bold ${result.trans_fat_status === 'HIGH / DANGEROUS' ? 'text-rose-600' : 'text-emerald-600'}`}>
                          {result.trans_fat_g !== null && result.trans_fat_g !== undefined ? `${result.trans_fat_g}g / 100g` : 'Zero'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 3. Sodium & Salt Level */}
                <div className="p-4 rounded-2xl border bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700/80">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 dark:border-slate-700">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                      <span>🧂</span>
                      <span>Sodium & Salt Content</span>
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      result.sodium_level === 'CRITICAL'
                        ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300'
                        : result.sodium_level === 'HIGH'
                        ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                        : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                    }`}>
                      {result.sodium_level}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700 text-xs">
                    <div>
                      <span className="text-[10px] text-slate-400 block">Sodium Quantity:</span>
                      <span className="font-extrabold text-sm text-slate-900 dark:text-white font-mono">
                        {result.sodium_mg !== null && result.sodium_mg !== undefined ? `${result.sodium_mg} mg / 100g` : 'Not Disclosed'}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-slate-400 block">ICMR Safe Limit:</span>
                      <span className="font-semibold text-slate-600 dark:text-slate-400 text-xs">
                        &lt; 400 mg / 100g
                      </span>
                    </div>
                  </div>
                  {result.sodium_mg && result.sodium_mg >= 800 && (
                    <p className="text-[11px] text-rose-600 dark:text-rose-400 mt-2 font-medium">
                      ⚠️ Extremely high sodium! One serving consumes over 45% of the daily limit recommended by ICMR & WHO.
                    </p>
                  )}
                </div>

                {/* 4. Chemical Additives & INS E-Numbers */}
                <div className="p-4 rounded-2xl border bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700/80">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 dark:border-slate-700">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5">
                      <span>🧪</span>
                      <span>Harmful Additives (INS E-Numbers)</span>
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      result.harmful_additives.length > 0 ? 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                    }`}>
                      {result.harmful_additives.length} Flagged
                    </span>
                  </div>

                  {result.harmful_additives.length > 0 ? (
                    <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                      {result.harmful_additives.map((add, idx) => (
                        <div key={idx} className="p-2 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900 dark:text-white">{add.name}</span>
                            <span className="text-[9px] font-black px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-600 dark:text-rose-300">
                              {add.risk}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 leading-tight">
                            {add.hazard}
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 text-xs text-emerald-600 dark:text-emerald-400 py-2">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Clean label: No hazardous synthetic colors, preservatives or MSG flagged.</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Statutory FSSAI & WHO Safe Recommended Limits Audit */}
              {result.govt_limit_comparison && result.govt_limit_comparison.length > 0 && (
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 shadow-sm space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-700">
                    <div>
                      <h4 className="text-xs font-black text-slate-900 dark:text-white flex items-center space-x-2">
                        <span className="text-base">🏛️</span>
                        <span>Statutory FSSAI & WHO Safe Recommended Limits Audit</span>
                      </h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        Identifies parameters exceeding statutory Indian food safety thresholds & ICMR daily ceilings
                      </p>
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300">
                      Official Standards
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {result.govt_limit_comparison.map((item, idx) => {
                      const isCritical = item.status === 'CRITICAL_EXCESS';
                      const isExceed = item.status === 'EXCEEDS_RECOMMENDED_LIMIT';
                      return (
                        <div
                          key={idx}
                          className={`p-3 rounded-xl border transition-all ${
                            isCritical
                              ? 'bg-rose-50/70 dark:bg-rose-950/30 border-rose-200 dark:border-rose-900/60'
                              : isExceed
                              ? 'bg-amber-50/70 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/60'
                              : 'bg-emerald-50/70 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-900/60'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-1.5">
                            <div>
                              <span className="text-xs font-bold text-slate-900 dark:text-white block">
                                {item.parameter}
                              </span>
                              <span className="text-[10px] text-slate-500 dark:text-slate-400">
                                Safe Limit: {item.govt_recommended_limit}
                              </span>
                            </div>
                            <span
                              className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold whitespace-nowrap ${
                                isCritical
                                  ? 'bg-rose-600 text-white'
                                  : isExceed
                                  ? 'bg-amber-500 text-white'
                                  : 'bg-emerald-600 text-white'
                              }`}
                            >
                              {item.exceed_percentage || (isCritical ? 'CRITICAL' : isExceed ? 'EXCEEDS' : 'COMPLIANT')}
                            </span>
                          </div>

                          <div className="flex items-center justify-between text-xs py-1 px-2 rounded-lg bg-white/80 dark:bg-slate-900/70 border border-slate-200/60 dark:border-slate-700/60 mb-1.5 font-mono">
                            <span className="text-[11px] text-slate-500 dark:text-slate-400">Detected Value:</span>
                            <span className="font-bold text-slate-900 dark:text-white">{item.found_value}</span>
                          </div>

                          <p className="text-[11px] text-slate-700 dark:text-slate-300 leading-snug">
                            {item.warning_or_guidance}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Extracted Ingredients & Health Advantage/Risk Breakdown */}
              {result.all_ingredients_analysis && result.all_ingredients_analysis.length > 0 && (
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 shadow-sm space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-700">
                    <div>
                      <h4 className="text-xs font-black text-slate-900 dark:text-white flex items-center space-x-2">
                        <span className="text-base">📋</span>
                        <span>Extracted Ingredients & Health Advantage/Risk Breakdown</span>
                      </h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        Full exploration of {result.all_ingredients_analysis.length} extracted ingredient(s), physiological impact, and everyday harmlessness
                      </p>
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                      {result.all_ingredients_analysis.length} Items Analyzed
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-96 overflow-y-auto pr-1">
                    {result.all_ingredients_analysis.map((ing, idx) => {
                      const isHarmful = ing.health_effect === 'HARMFUL';
                      const isCaution = ing.health_effect === 'MODERATE_CAUTION';
                      const isBeneficial = ing.health_effect === 'BENEFICIAL';
                      return (
                        <div
                          key={idx}
                          className={`p-3 rounded-xl border flex flex-col justify-between ${
                            isHarmful
                              ? 'bg-rose-50/50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/50'
                              : isCaution
                              ? 'bg-amber-50/50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/50'
                              : isBeneficial
                              ? 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-900/50'
                              : 'bg-slate-50/50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700'
                          }`}
                        >
                          <div>
                            <div className="flex items-start justify-between gap-1 mb-1">
                              <span className="font-bold text-xs text-slate-900 dark:text-white leading-tight">
                                {ing.name}
                              </span>
                              <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 shrink-0">
                                {ing.category}
                              </span>
                            </div>

                            <p className="text-[11px] text-slate-600 dark:text-slate-300 mt-1 leading-snug">
                              {ing.health_advantage_or_risk}
                            </p>
                          </div>

                          <div className="mt-2.5 pt-2 border-t border-slate-200/50 dark:border-slate-700/50 flex items-center justify-between text-[10px]">
                            <span className="font-semibold text-slate-500 dark:text-slate-400">
                              Harmlessness:
                            </span>
                            <span className="font-bold text-slate-800 dark:text-slate-200">
                              {ing.harmlessness_level}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Everyday Usual Things We Use Breakdown */}
              {result.usual_items_summary && result.usual_items_summary.length > 0 && (
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 shadow-sm space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-700">
                    <div>
                      <h4 className="text-xs font-black text-slate-900 dark:text-white flex items-center space-x-2">
                        <span className="text-base">🏡</span>
                        <span>Everyday Usual Things We Use: Truth & Harmlessness Guide</span>
                      </h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        Scientific clarity on how everyday kitchen staples compare between home culinary use vs industrial ultra-processed foods
                      </p>
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300">
                      Kitchen Staples
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {result.usual_items_summary.map((item, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-50/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-700/80 flex flex-col justify-between space-y-2"
                      >
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-bold text-xs text-slate-900 dark:text-white">
                              {item.item_name}
                            </span>
                          </div>
                          <span className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 mb-2">
                            {item.harmlessness_verdict}
                          </span>

                          <div className="space-y-1.5 text-[11px]">
                            <div>
                              <span className="font-bold text-slate-700 dark:text-slate-300">Home Use Context: </span>
                              <span className="text-slate-600 dark:text-slate-400">{item.everyday_use_context}</span>
                            </div>
                            <div>
                              <span className="font-bold text-slate-700 dark:text-slate-300">Safe Daily Ceiling: </span>
                              <span className="text-emerald-700 dark:text-emerald-400 font-medium">{item.safe_daily_limit}</span>
                            </div>
                            <div>
                              <span className="font-bold text-rose-700 dark:text-rose-400">Packaged Food Danger: </span>
                              <span className="text-slate-600 dark:text-slate-400">{item.processed_food_risk}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Beneficial Grains / Positives */}
              {result.beneficial_ingredients && result.beneficial_ingredients.length > 0 && (
                <div className="p-3.5 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/50 flex items-center space-x-2 text-xs text-emerald-900 dark:text-emerald-200">
                  <span className="font-bold shrink-0">🥦 Wholesome Ingredients:</span>
                  <span>{result.beneficial_ingredients.join(', ')}</span>
                </div>
              )}

              {/* Raw Extracted Ingredients Toggle */}
              <div className="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden">
                <button
                  type="button"
                  onClick={() => setShowRawIngredients(!showRawIngredients)}
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/40 text-left text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  <span>Inspect Full Extracted Ingredient Tokens ({result.raw_extracted_ingredients?.length || 0})</span>
                  {showRawIngredients ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
                {showRawIngredients && (
                  <div className="p-3.5 bg-white dark:bg-slate-900 text-xs text-slate-600 dark:text-slate-400 space-y-2">
                    <div className="flex flex-wrap gap-1.5">
                      {result.raw_extracted_ingredients?.map((ing, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                          {ing}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-5 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 shrink-0">
          <div className="flex items-center space-x-1.5">
            <Info className="w-3.5 h-3.5 text-blue-500" />
            <span>Audited under FSSAI (Labelling and Display) Regulations & Front-of-Pack Norms</span>
          </div>
          <button
            type="button"
            onClick={() => {
              stopCamera();
              onClose();
            }}
            className="px-4 py-1.5 rounded-xl bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
