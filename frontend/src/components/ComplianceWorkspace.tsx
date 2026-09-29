import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  FileCheck2,
  Plus,
  Trash2,
  Download,
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
  Building,
  Beaker,
  ShieldAlert,
  FileText,
  X,
  Camera,
  CameraOff,
  Upload,
  Scan,
  Loader2,
  Eye,
  EyeOff,
  RefreshCw,
  Zap,
  CheckCircle2,
  Layers,
  ArrowRight,
  Maximize2
} from 'lucide-react';
import Tesseract from 'tesseract.js';
import {
  AuditParameterInput,
  AuditRequest,
  AuditResponse,
  AuditTemplate,
  ExtractedLabReportData
} from '../types';
import { auditApi } from '../services/api';

interface ComplianceWorkspaceProps {
  addToast: (type: 'success' | 'error' | 'info', message: string) => void;
  onClose?: () => void;
}

// Preset realistic laboratory test report certificates for 1-click evaluation
const SAMPLE_LAB_REPORTS = [
  {
    id: 'sample_water_pass',
    badge: 'Conforming',
    badgeColor: 'bg-emerald-600',
    title: '💧 Packaged Water Analysis (IS 14543) - Conforming Batch',
    standard_code: 'IS 14543',
    product_name: 'Premium Packaged Drinking Water 1L',
    manufacturer_name: 'Himalayan Mineral Springs Ltd',
    batch_number: 'HMS-2026-B402',
    testing_lab: 'BIS Central Laboratory, Sahibabad (NABL Accredited)',
    raw_text: `GOVERNMENT OF INDIA - MINISTRY OF CONSUMER AFFAIRS
CENTRAL LABORATORY SAHIBABAD (NABL ACCREDITED LAB TC-5421)
OFFICIAL TEST REPORT / CERTIFICATE OF COMPLIANCE
Standard: IS 14543 : 2018 (Packaged Drinking Water Other Than Natural Mineral Water)
Customer / Manufacturer: Himalayan Mineral Springs Ltd
Sample Description: Premium Packaged Drinking Water 1L PET Bottle
Batch / Lot No: HMS-2026-B402
Date of Testing: 18-Feb-2026
Testing Laboratory: BIS Central Laboratory Sahibabad

CHEMICAL & MICROBIOLOGICAL OBSERVED PARAMETERS:
1. pH Value: 7.35
2. Total Dissolved Solids (TDS): 125.0 mg/L
3. Turbidity: 0.45 NTU
4. Lead (as Pb): 0.003 mg/L
5. Arsenic (as As): 0.002 mg/L
6. Nitrate (as NO3): 14.2 mg/L
7. Escherichia coli (E. coli): Nil cfu/250ml
8. Coliform Bacteria: Nil cfu/250ml

OPINION / REMARKS: The submitted sample conforms to all tested requirements of IS 14543:2018.`,
    parameters: [
      { parameter_name: 'pH Value', tested_value: '7.35', unit: '', notes: 'Digital pH meter' },
      { parameter_name: 'Total Dissolved Solids (TDS)', tested_value: '125.0', unit: 'mg/L', notes: 'Gravimetric method' },
      { parameter_name: 'Turbidity', tested_value: '0.45', unit: 'NTU', notes: 'Nephelometric method' },
      { parameter_name: 'Lead (as Pb)', tested_value: '0.003', unit: 'mg/L', notes: 'AAS Graphite furnace' },
      { parameter_name: 'Arsenic (as As)', tested_value: '0.002', unit: 'mg/L', notes: 'Hydride generation method' },
      { parameter_name: 'Nitrate (as NO3)', tested_value: '14.2', unit: 'mg/L', notes: 'Spectrophotometric' },
      { parameter_name: 'Escherichia coli (E. coli)', tested_value: '0', unit: 'cfu/250ml', notes: 'Membrane filtration' },
      { parameter_name: 'Coliform Bacteria', tested_value: '0', unit: 'cfu/250ml', notes: 'Membrane filtration' }
    ]
  },
  {
    id: 'sample_water_fail',
    badge: 'Toxic Violation',
    badgeColor: 'bg-rose-600',
    title: '⚠️ Packaged Water Analysis (IS 14543) - Toxic Lead Violation',
    standard_code: 'IS 14543',
    product_name: 'AquaSpring 1L Packaged Drinking Water',
    manufacturer_name: 'Delta Packaged Beverages Ltd',
    batch_number: 'DPB-2026-FAIL-03',
    testing_lab: 'Northern Regional Quality Testing Laboratory (NABL Accredited)',
    raw_text: `NORTHERN REGIONAL QUALITY TESTING LABORATORY (NABL ACCREDITED)
STATUTORY COMPLIANCE REPORT OF TEST SAMPLE
Standard: IS 14543 : 2018 (Packaged Drinking Water)
Manufacturer: Delta Packaged Beverages Ltd
Batch No: DPB-2026-FAIL-03
Testing Lab: Northern Regional Quality Testing Laboratory

OBSERVED LABORATORY FINDINGS:
1. pH Value: 7.1
2. Total Dissolved Solids (TDS): 480.0 mg/L
3. Turbidity: 1.8 NTU
4. Lead (as Pb): 0.024 mg/L
5. Arsenic (as As): 0.004 mg/L
6. Escherichia coli (E. coli): 0 cfu/250ml

OPINION / REMARKS: CRITICAL FAILURE. Lead content exceeds statutory 0.01 mg/L maximum threshold.`,
    parameters: [
      { parameter_name: 'pH Value', tested_value: '7.1', unit: '', notes: 'Glass electrode' },
      { parameter_name: 'Total Dissolved Solids (TDS)', tested_value: '480.0', unit: 'mg/L', notes: 'Gravimetric' },
      { parameter_name: 'Turbidity', tested_value: '1.8', unit: 'NTU', notes: 'Nephelometric' },
      { parameter_name: 'Lead (as Pb)', tested_value: '0.024', unit: 'mg/L', notes: 'Exceeds 0.01 mg/L limit!' },
      { parameter_name: 'Arsenic (as As)', tested_value: '0.004', unit: 'mg/L', notes: 'Hydride generation' },
      { parameter_name: 'Escherichia coli (E. coli)', tested_value: '0', unit: 'cfu/250ml', notes: 'Membrane filter' }
    ]
  },
  {
    id: 'sample_steel_pass',
    badge: 'Conforming',
    badgeColor: 'bg-emerald-600',
    title: '🏗️ TMT Rebar Metallurgy Certificate (IS 1786 - Fe 500D)',
    standard_code: 'IS 1786',
    product_name: 'High Strength TMT Rebar 16mm Dia Fe 500D',
    manufacturer_name: 'Deccan High-Tensile Steel Mills Ltd',
    batch_number: 'DHSM-FE500D-88A',
    testing_lab: 'Central Metallurgy & Metrology Lab (NABL Accredited)',
    raw_text: `CENTRAL METALLURGY & METROLOGY LABORATORY (NABL ACCREDITED)
METALLURGICAL TEST CERTIFICATE - BATCH VERIFICATION
Standard: IS 1786 : 2008 (High Strength Deformed Steel Bars for Concrete Reinforcement)
Product: High Strength TMT Rebar 16mm Dia Grade Fe 500D
Manufacturer: Deccan High-Tensile Steel Mills Ltd
Batch Identification: DHSM-FE500D-88A
Testing Laboratory: Central Metallurgy Lab

OBSERVED CHEMICAL COMPOSITION & MECHANICAL PROPERTIES:
1. Carbon (C) Content: 0.21 %
2. Sulphur (S) Content: 0.035 %
3. Phosphorus (P) Content: 0.032 %
4. 0.2% Proof Stress / Yield Strength: 528.0 N/mm²
5. Tensile Strength to Yield Strength Ratio: 1.14 ratio
6. Elongation (Gauge Length 5.65√A): 17.5 %

REMARKS: Conforms to all chemical and mechanical specifications of IS 1786:2008 Grade Fe 500D.`,
    parameters: [
      { parameter_name: 'Carbon (C) Content', tested_value: '0.21', unit: '%', notes: 'Optical emission spectrometry' },
      { parameter_name: 'Sulphur (S) Content', tested_value: '0.035', unit: '%', notes: 'Combustion infrared' },
      { parameter_name: 'Phosphorus (P) Content', tested_value: '0.032', unit: '%', notes: 'Spectrometric' },
      { parameter_name: '0.2% Proof Stress / Yield Strength', tested_value: '528.0', unit: 'N/mm²', notes: 'Universal testing machine' },
      { parameter_name: 'Tensile Strength to Yield Strength Ratio', tested_value: '1.14', unit: 'ratio', notes: 'Ductility ratio calculation' },
      { parameter_name: 'Elongation (Gauge Length 5.65√A)', tested_value: '17.5', unit: '%', notes: 'Tensile fracture test' }
    ]
  },
  {
    id: 'sample_hdpe_pass',
    badge: 'Conforming',
    badgeColor: 'bg-emerald-600',
    title: '🔬 CIPET Polymer Pipe Report (IS 4984 - PE 100)',
    standard_code: 'IS 4984',
    product_name: 'HDPE Pipe 110mm OD SDR 11',
    manufacturer_name: 'Bharat High-Density Polymers Corp',
    batch_number: 'BHDP-PE100-LOT12',
    testing_lab: 'CIPET National Polymer Testing Facility (NABL Accredited)',
    raw_text: `CENTRAL INSTITUTE OF PETROCHEMICALS ENGINEERING & TECHNOLOGY (CIPET)
GOVERNMENT OF INDIA - NABL ACCREDITED LABORATORY
Standard: IS 4984 : 2016 (HDPE Pipes for Water Supply)
Product: HDPE Pipe 110mm OD SDR 11 PE 100
Manufacturer: Bharat High-Density Polymers Corp
Batch No: BHDP-PE100-LOT12
Testing Lab: CIPET National Polymer Testing Facility

OBSERVED POLYMER TEST VALUES:
1. Base Polymer Density at 27°C: 952.5 kg/m³
2. Melt Flow Index (190°C / 5 kg): 0.45 g/10 min
3. Carbon Black Content: 2.4 %
4. Hydrostatic Strength (100h at 20°C, PE 100): 12.4 MPa hoop stress

REMARKS: Complies with all material criteria of IS 4984:2016.`,
    parameters: [
      { parameter_name: 'Base Polymer Density at 27°C', tested_value: '952.5', unit: 'kg/m³', notes: 'Density gradient column' },
      { parameter_name: 'Melt Flow Index (190°C / 5 kg)', tested_value: '0.45', unit: 'g/10 min', notes: 'MFI plastometer' },
      { parameter_name: 'Carbon Black Content', tested_value: '2.4', unit: '%', notes: 'Pyrolysis in nitrogen' },
      { parameter_name: 'Hydrostatic Strength (100h at 20°C, PE 100)', tested_value: '12.4', unit: 'MPa hoop stress', notes: 'No burst or leakage observed' }
    ]
  },
  {
    id: 'sample_water_potable',
    badge: 'Conforming',
    badgeColor: 'bg-emerald-600',
    title: '🚰 Potable Municipal Drinking Water (IS 10500)',
    standard_code: 'IS 10500',
    product_name: 'Treated Drinking Water Supply',
    manufacturer_name: 'Delhi Jal Board Water Treatment Plant',
    batch_number: 'DJB-WTP-2026-LOT4',
    testing_lab: 'National Environmental Engineering Research Institute (NEERI)',
    raw_text: `CSIR - NATIONAL ENVIRONMENTAL ENGINEERING RESEARCH INSTITUTE (NEERI)
GOVERNMENT OF INDIA - NABL ACCREDITED LAB
Standard: IS 10500 : 2012 (Drinking Water Specification - Second Revision)
Sample Source: Delhi Jal Board Water Treatment Plant
Sample ID: DJB-WTP-2026-LOT4
Tested by: NEERI Environmental Testing Laboratory

WATER QUALITY TEST FINDINGS:
1. pH Value: 7.4
2. Total Dissolved Solids (TDS): 210.0 mg/L
3. Turbidity: 0.65 NTU
4. Total Hardness (as CaCO3): 140.0 mg/L
5. Chlorides (as Cl): 85.0 mg/L
6. Fluoride (as F): 0.7 mg/L
7. Lead (as Pb): 0.002 mg/L
8. Arsenic (as As): 0.001 mg/L
9. Escherichia coli (E. coli): Absent cfu/100ml

OPINION / REMARKS: Conforms to all desirable limits of IS 10500:2012 for potable domestic water.`,
    parameters: [
      { parameter_name: 'pH Value', tested_value: '7.4', unit: '', notes: 'IS 3025 Part 11' },
      { parameter_name: 'Total Dissolved Solids (TDS)', tested_value: '210.0', unit: 'mg/L', notes: 'IS 3025 Part 16' },
      { parameter_name: 'Turbidity', tested_value: '0.65', unit: 'NTU', notes: 'IS 3025 Part 10' },
      { parameter_name: 'Total Hardness (as CaCO3)', tested_value: '140.0', unit: 'mg/L', notes: 'IS 3025 Part 21' },
      { parameter_name: 'Chlorides (as Cl)', tested_value: '85.0', unit: 'mg/L', notes: 'IS 3025 Part 32' },
      { parameter_name: 'Fluoride (as F)', tested_value: '0.7', unit: 'mg/L', notes: 'IS 3025 Part 60' },
      { parameter_name: 'Lead (as Pb)', tested_value: '0.002', unit: 'mg/L', notes: 'IS 3025 Part 47' },
      { parameter_name: 'Arsenic (as As)', tested_value: '0.001', unit: 'mg/L', notes: 'IS 3025 Part 37' },
      { parameter_name: 'Escherichia coli (E. coli)', tested_value: '0', unit: 'cfu/100ml', notes: 'IS 15185' }
    ]
  },
  {
    id: 'sample_cement_pass',
    badge: 'Conforming',
    badgeColor: 'bg-emerald-600',
    title: '🧱 Ordinary Portland Cement 53 Grade (IS 269)',
    standard_code: 'IS 269',
    product_name: 'Ordinary Portland Cement 53 Grade',
    manufacturer_name: 'UltraTech Cement Corporation Ltd',
    batch_number: 'UTC-53G-2026-WK09',
    testing_lab: 'National Council for Cement and Building Materials (NCCBM)',
    raw_text: `NATIONAL COUNCIL FOR CEMENT AND BUILDING MATERIALS (NCCBM)
OFFICIAL CEMENT QUALITY EVALUATION CERTIFICATE
Standard: IS 269 : 2015 (Ordinary Portland Cement Specification)
Manufacturer: UltraTech Cement Corporation Ltd
Batch / Silo Lot: UTC-53G-2026-WK09
Testing Lab: NCCBM Ballabgarh Central Testing Laboratories

PHYSICAL AND CHEMICAL LABORATORY RESULTS:
1. Soundness (Le Chatelier): 1.5 mm
2. Initial Setting Time: 125.0 minutes
3. Final Setting Time: 210.0 minutes
4. 28-Day Compressive Strength: 56.4 MPa
5. Insoluble Residue: 1.8 %
6. Magnesia (MgO) Content: 2.1 %

REMARKS: Conforms to all mandatory physical and chemical requirements of IS 269:2015 Grade 53.`,
    parameters: [
      { parameter_name: 'Soundness (Le Chatelier)', tested_value: '1.5', unit: 'mm', notes: 'IS 4031 Part 3' },
      { parameter_name: 'Initial Setting Time', tested_value: '125.0', unit: 'minutes', notes: 'IS 4031 Part 5' },
      { parameter_name: 'Final Setting Time', tested_value: '210.0', unit: 'minutes', notes: 'IS 4031 Part 5' },
      { parameter_name: '28-Day Compressive Strength', tested_value: '56.4', unit: 'MPa', notes: 'IS 4031 Part 6' },
      { parameter_name: 'Insoluble Residue', tested_value: '1.8', unit: '%', notes: 'IS 4032' },
      { parameter_name: 'Magnesia (MgO) Content', tested_value: '2.1', unit: '%', notes: 'IS 4032' }
    ]
  }
];

export const ComplianceWorkspace: React.FC<ComplianceWorkspaceProps> = ({ addToast, onClose }) => {
  const [templates, setTemplates] = useState<AuditTemplate[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');

  // Form State
  const [standardCode, setStandardCode] = useState<string>('IS 14543');
  const [productName, setProductName] = useState<string>('Premium Packaged Drinking Water 1L');
  const [manufacturerName, setManufacturerName] = useState<string>('Stark Industries Beverages Pvt Ltd (Tony Stark)');
  const [batchNumber, setBatchNumber] = useState<string>('STARK-2026-B402');
  const [testingLab, setTestingLab] = useState<string>('Dexter Secret Research Laboratory (NABL Accredited)');
  const [parameters, setParameters] = useState<AuditParameterInput[]>([
    { parameter_name: 'pH Value', tested_value: '7.35', unit: '', notes: 'Digital pH meter' },
    { parameter_name: 'Total Dissolved Solids (TDS)', tested_value: '130.0', unit: 'mg/L', notes: 'Gravimetric' },
    { parameter_name: 'Turbidity', tested_value: '0.5', unit: 'NTU', notes: 'Nephelometer' },
    { parameter_name: 'Lead (as Pb)', tested_value: '0.004', unit: 'mg/L', notes: 'AAS Test' },
    { parameter_name: 'Arsenic (as As)', tested_value: '0.002', unit: 'mg/L', notes: 'Hydride generation' },
    { parameter_name: 'Nitrate (as NO3)', tested_value: '18.0', unit: 'mg/L', notes: 'Spectrophotometric' },
    { parameter_name: 'E. Coli', tested_value: '0', unit: 'cfu/250ml', notes: 'Membrane filtration' },
  ]);

  const [loading, setLoading] = useState<boolean>(false);
  const [auditResult, setAuditResult] = useState<AuditResponse | null>(null);

  // Camera & Extraction State
  const [autoVerifyOnExtract, setAutoVerifyOnExtract] = useState<boolean>(true);
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [isCameraLoading, setIsCameraLoading] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const [hasMultipleCameras, setHasMultipleCameras] = useState<boolean>(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);

  // Extraction Progress State
  const [isExtracting, setIsExtracting] = useState<boolean>(false);
  const [ocrProgress, setOcrProgress] = useState<number>(0);
  const [ocrStatus, setOcrStatus] = useState<string>('');
  const [rawExtractedText, setRawExtractedText] = useState<string>('');
  const [showRawText, setShowRawText] = useState<boolean>(false);
  const [extractionMethod, setExtractionMethod] = useState<string>('');
  const [confidenceScore, setConfidenceScore] = useState<number | null>(null);
  const [irrelevantAlert, setIrrelevantAlert] = useState<{ reason: string; subject?: string } | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Check multiple cameras on mount
  useEffect(() => {
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
      navigator.mediaDevices.enumerateDevices()
        .then((devices) => {
          const videoInputs = devices.filter((d) => d.kind === 'videoinput');
          setHasMultipleCameras(videoInputs.length > 1);
        })
        .catch(() => {});
    }
  }, []);

  // Fetch preset templates on load
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const data = await auditApi.getTemplates();
        setTemplates(data);
      } catch (err) {
        console.error('Failed to fetch templates:', err);
      }
    };
    fetchTemplates();
  }, []);

  // Stop camera on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const stopCamera = useCallback(() => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    setIsCameraActive(false);
  }, []);

  const startCamera = async (mode: 'environment' | 'user' = facingMode) => {
    setIsCameraLoading(true);
    setCameraError(null);
    try {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: mode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsCameraActive(true);
    } catch (err: any) {
      console.warn('Camera access issue:', err);
      setCameraError('Camera access denied or unavailable on this device.');
      addToast('error', 'Camera access denied. You can still upload report files or select a sample report.');
    } finally {
      setIsCameraLoading(false);
    }
  };

  const flipCamera = async () => {
    const nextMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextMode);
    await startCamera(nextMode);
  };

  // Process image with OCR + Vision Extraction + Auto-Verification
  const processLabReportImage = async (imageBase64: string, existingText?: string) => {
    setIsExtracting(true);
    setOcrProgress(15);
    setOcrStatus('Optical Scanner initializing for lab report...');
    setCapturedImage(imageBase64);

    // Reset previous audit state & parameters upfront to prevent stale data bleed
    setAuditResult(null);
    setIrrelevantAlert(null);
    setParameters([]);
    setStandardCode('');
    setProductName('');
    setManufacturerName('');
    setBatchNumber('');
    setTestingLab('');
    setRawExtractedText('');

    try {
      let ocrText = existingText || '';

      // If text not already provided, run client Tesseract OCR with live progress
      if (!ocrText) {
        try {
          setOcrStatus('Scanning test certificate text & parameters...');
          const { data } = await Tesseract.recognize(imageBase64, 'eng', {
            logger: (m) => {
              if (m.status === 'recognizing text' && typeof m.progress === 'number') {
                const pct = Math.round(m.progress * 65) + 15;
                setOcrProgress(pct);
              }
            }
          });
          ocrText = data?.text || '';
        } catch (tessErr) {
          console.warn('Browser Tesseract scan fallback:', tessErr);
        }
      }

      setOcrProgress(85);
      setOcrStatus('Extracting parameters & cross-referencing statutory BIS clauses...');

      // Call Backend API
      const extractResult: ExtractedLabReportData = await auditApi.extractLabReport({
        image_base64: imageBase64,
        raw_text: ocrText,
        auto_verify: autoVerifyOnExtract
      });

      // Check for Irrelevant Data Guard
      if (extractResult.status === 'IRRELEVANT_DATA' || extractResult.is_relevant === false) {
        setOcrProgress(100);
        setOcrStatus('Inspection finished: Irrelevant data detected.');
        setAuditResult(null);
        setParameters([]);
        setStandardCode('');
        setProductName('');
        setManufacturerName('');
        setBatchNumber('');
        setTestingLab('');
        setRawExtractedText(extractResult.extracted_text || ocrText || '');
        setIrrelevantAlert({
          reason: extractResult.relevance_reason || 'Uploaded image does not appear to be a laboratory test report or quality certificate.',
          subject: extractResult.detected_subject || 'Non-domain Subject'
        });
        addToast('error', `Irrelevant Data Detected: ${extractResult.relevance_reason || 'Not a valid lab report.'}`);
        return;
      }

      setIrrelevantAlert(null);
      setOcrProgress(100);
      setOcrStatus('Lab report parsed successfully!');

      // Populate Form State
      if (extractResult.standard_is_code) setStandardCode(extractResult.standard_is_code);
      if (extractResult.product_name) setProductName(extractResult.product_name);
      if (extractResult.manufacturer_name) setManufacturerName(extractResult.manufacturer_name);
      if (extractResult.batch_number) setBatchNumber(extractResult.batch_number);
      if (extractResult.testing_lab) setTestingLab(extractResult.testing_lab);

      if (extractResult.parameters && extractResult.parameters.length > 0) {
        setParameters(extractResult.parameters);
      }

      setRawExtractedText(extractResult.extracted_text || ocrText);
      setExtractionMethod(extractResult.extraction_method || 'Optical Recognition');
      setConfidenceScore(extractResult.confidence_score ? Math.round(extractResult.confidence_score * 100) : 95);

      // Handle Auto-Verification Output
      if (extractResult.verification) {
        setAuditResult(extractResult.verification);
        if (extractResult.verification.overall_verdict === 'CONFORMING') {
          addToast('success', `Lab Report Verified: 100% CONFORMING to ${extractResult.standard_is_code}!`);
        } else {
          addToast('error', `Audit Alert: Non-conforming parameters detected in ${extractResult.standard_is_code}!`);
        }
      } else {
        setAuditResult(null);
        addToast('success', `Extracted ${extractResult.parameters.length} parameters from lab report! Click 'Execute Conformity Audit' to verify.`);
      }
    } catch (err: any) {
      console.error('Lab report extraction error:', err);
      addToast('error', err.response?.data?.detail || 'Failed to extract lab report text. Try again or enter manually.');
    } finally {
      setIsExtracting(false);
      setOcrProgress(0);
      setOcrStatus('');
    }
  };

  // Capture frame from active camera
  const captureFrame = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    stopCamera();
    processLabReportImage(dataUrl);
  };

  // File Upload Handler
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type === 'application/pdf') {
      // Direct PDF upload to backend
      setIsExtracting(true);
      setOcrProgress(30);
      setOcrStatus('Uploading PDF laboratory report to parser...');
      // Clear previous states upfront
      setAuditResult(null);
      setIrrelevantAlert(null);
      setParameters([]);
      setStandardCode('');
      setProductName('');
      setManufacturerName('');
      setBatchNumber('');
      setTestingLab('');
      setRawExtractedText('');

      try {
        const result = await auditApi.uploadLabReportFile(file, autoVerifyOnExtract);
        setOcrProgress(100);

        if (result.status === 'IRRELEVANT_DATA' || result.is_relevant === false) {
          setAuditResult(null);
          setParameters([]);
          setStandardCode('');
          setProductName('');
          setManufacturerName('');
          setBatchNumber('');
          setTestingLab('');
          setRawExtractedText(result.extracted_text || '');
          setIrrelevantAlert({
            reason: result.relevance_reason || 'PDF document is not a laboratory test certificate.',
            subject: result.detected_subject || 'Non-domain Document'
          });
          addToast('error', `Irrelevant Data: ${result.relevance_reason || 'Uploaded PDF is not a valid lab report.'}`);
          return;
        }

        setIrrelevantAlert(null);
        if (result.standard_is_code) setStandardCode(result.standard_is_code);
        if (result.product_name) setProductName(result.product_name);
        if (result.manufacturer_name) setManufacturerName(result.manufacturer_name);
        if (result.batch_number) setBatchNumber(result.batch_number);
        if (result.testing_lab) setTestingLab(result.testing_lab);
        if (result.parameters && result.parameters.length > 0) setParameters(result.parameters);

        setRawExtractedText(result.extracted_text);
        setExtractionMethod(result.extraction_method);
        setConfidenceScore(result.confidence_score ? Math.round(result.confidence_score * 100) : 95);

        if (result.verification) {
          setAuditResult(result.verification);
          if (result.verification.overall_verdict === 'CONFORMING') {
            addToast('success', `PDF Lab Report Verified: 100% CONFORMING to ${result.standard_is_code}!`);
          } else {
            addToast('error', `Audit Alert: Non-conformance detected in PDF report!`);
          }
        } else {
          addToast('success', `Extracted ${result.parameters.length} parameters from PDF report!`);
        }
      } catch (err: any) {
        addToast('error', err.response?.data?.detail || 'Failed to process PDF report.');
      } finally {
        setIsExtracting(false);
        setOcrProgress(0);
        setOcrStatus('');
      }
    } else {
      // Image file
      const reader = new FileReader();
      reader.onload = (event) => {
        const b64 = event.target?.result as string;
        if (b64) {
          processLabReportImage(b64);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  // Quick Realistic Sample Report Loader
  const handleLoadSampleReport = (sample: typeof SAMPLE_LAB_REPORTS[0]) => {
    setStandardCode(sample.standard_code);
    setProductName(sample.product_name);
    setManufacturerName(sample.manufacturer_name);
    setBatchNumber(sample.batch_number);
    setTestingLab(sample.testing_lab);
    setParameters(sample.parameters);
    setRawExtractedText(sample.raw_text);
    setExtractionMethod('Simulated NABL Optical Scan');
    setConfidenceScore(98);
    setCapturedImage(null);

    // If auto-verify is active, execute audit immediately
    if (autoVerifyOnExtract) {
      setLoading(true);
      auditApi.runAudit({
        standard_is_code: sample.standard_code,
        product_name: sample.product_name,
        manufacturer_name: sample.manufacturer_name,
        batch_number: sample.batch_number,
        testing_lab: sample.testing_lab,
        parameters: sample.parameters
      })
        .then((res) => {
          setAuditResult(res);
          if (res.overall_verdict === 'CONFORMING') {
            addToast('success', `Auto-verified sample: Batch 100% CONFORMS to ${sample.standard_code}!`);
          } else {
            addToast('error', `Auto-verified sample: Critical non-conformance detected!`);
          }
        })
        .catch((err) => {
          addToast('error', 'Error auto-verifying sample report.');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setAuditResult(null);
      addToast('info', `Loaded sample test report for ${sample.standard_code}. Click 'Execute Conformity Audit' to verify.`);
    }
  };

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplateId(templateId);
    const tmpl = templates.find((t) => t.id === templateId);
    if (tmpl) {
      setStandardCode(tmpl.standard_is_code);
      setProductName(tmpl.product_name);
      setManufacturerName(tmpl.manufacturer_name);
      setBatchNumber(tmpl.batch_number);
      setTestingLab(tmpl.testing_lab);
      setParameters(tmpl.parameters);
      setAuditResult(null);
      setCapturedImage(null);
      setRawExtractedText('');
      addToast('info', `Loaded preset: ${tmpl.name}`);
    }
  };

  const handleAddParameter = () => {
    setParameters([
      ...parameters,
      { parameter_name: '', tested_value: '', unit: '', notes: '' },
    ]);
  };

  const handleRemoveParameter = (index: number) => {
    setParameters(parameters.filter((_, i) => i !== index));
  };

  const handleParameterChange = (index: number, field: keyof AuditParameterInput, value: string) => {
    const updated = [...parameters];
    updated[index] = { ...updated[index], [field]: value };
    setParameters(updated);
  };

  const handleRunAudit = async () => {
    if (!standardCode.trim() || !productName.trim() || parameters.length === 0) {
      addToast('error', 'Please fill in standard code, product name, and at least one parameter.');
      return;
    }

    setLoading(true);
    try {
      const payload: AuditRequest = {
        standard_is_code: standardCode,
        product_name: productName,
        manufacturer_name: manufacturerName,
        batch_number: batchNumber,
        testing_lab: testingLab,
        parameters: parameters.filter((p) => p.parameter_name.trim() && p.tested_value.trim()),
      };

      const result = await auditApi.runAudit(payload);
      setAuditResult(result);

      if (result.overall_verdict === 'CONFORMING') {
        addToast('success', 'Batch Conforms 100% to audited BIS specifications!');
      } else {
        addToast('error', 'Non-conforming parameters detected! See checklist.');
      }
    } catch (err: any) {
      addToast('error', err.response?.data?.detail || 'Failed to execute compliance audit.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = () => {
    if (!auditResult) return;
    const downloadUrl = auditApi.getReportDownloadUrl(auditResult.audit_id);
    window.open(downloadUrl, '_blank');
    addToast('info', 'Downloading Official BIS Conformity Report PDF...');
  };

  const verdictStyles = {
    CONFORMING: {
      bg: 'bg-emerald-50 dark:bg-emerald-950/40',
      border: 'border-emerald-500',
      text: 'text-emerald-700 dark:text-emerald-400',
      badge: 'bg-emerald-600 text-white',
      icon: <CheckCircle className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />,
    },
    NON_CONFORMING: {
      bg: 'bg-rose-50 dark:bg-rose-950/40',
      border: 'border-rose-500',
      text: 'text-rose-700 dark:text-rose-400',
      badge: 'bg-rose-600 text-white',
      icon: <AlertCircle className="w-6 h-6 text-rose-600 dark:text-rose-400" />,
    },
    CONDITIONAL_COMPLIANCE: {
      bg: 'bg-amber-50 dark:bg-amber-950/40',
      border: 'border-amber-500',
      text: 'text-amber-700 dark:text-amber-400',
      badge: 'bg-amber-600 text-white',
      icon: <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400" />,
    },
  };

  const handleResetAudit = () => {
    stopCamera();
    setAuditResult(null);
    setCapturedImage(null);
    setIrrelevantAlert(null);
    setRawExtractedText('');
    setExtractionMethod('');
    setConfidenceScore(null);
    setSelectedTemplateId('');
    setStandardCode('');
    setProductName('');
    setManufacturerName('');
    setBatchNumber('');
    setTestingLab('');
    setParameters([]);
    if (fileInputRef.current) fileInputRef.current.value = '';
    addToast('info', 'Audit Workspace reset. Ready for a new laboratory test audit.');
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto px-1 sm:px-2">
      {/* 3D Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel-3d p-6 rounded-3xl">
        <div>
          <div className="flex items-center space-x-2.5">
            <span className="p-2.5 rounded-2xl bg-gradient-to-tr from-blue-700 to-sky-500 text-white shadow-md shadow-blue-500/25">
              <FileCheck2 className="w-5 h-5" />
            </span>
            <div>
              <h2 className="text-base sm:text-lg font-black text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <span>GRASK AI: Compliance Audit Studio</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-bold border border-blue-300 dark:border-blue-800">
                  Camera & Auto-Verification
                </span>
              </h2>
              <span className="text-[10px] font-bold text-amber-600 dark:text-amber-400">
                Section 16, BIS Act 2016 Conformity Assessment Engine
              </span>
            </div>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 max-w-2xl leading-relaxed">
            Scan physical or digital laboratory test certificates via Camera or File Upload. Automatically extract observed chemical/physical parameters and instantly verify compliance against statutory BIS standards.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Quick Scenario Preset Dropdown */}
          <div className="flex items-center space-x-2 bg-slate-50 dark:bg-slate-900/90 p-2 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
            <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">Preset:</span>
            <select
              value={selectedTemplateId}
              onChange={(e) => handleTemplateSelect(e.target.value)}
              className="text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1 text-slate-800 dark:text-slate-200 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-inner"
            >
              <option value="">-- Choose Preset --</option>
              {templates.map((tmpl) => (
                <option key={tmpl.id} value={tmpl.id}>
                  {tmpl.name}
                </option>
              ))}
            </select>
          </div>

          {(auditResult || capturedImage || rawExtractedText || parameters.length > 0) && (
            <button
              type="button"
              onClick={handleResetAudit}
              className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-2xl border border-amber-300 dark:border-amber-800 bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/50 dark:hover:bg-amber-900/60 text-amber-800 dark:text-amber-200 text-xs font-semibold shadow-xs transition-colors"
              title="Reset workspace and start a fresh laboratory test audit"
            >
              <RotateCcw className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
              <span>Reset Audit</span>
            </button>
          )}

          {onClose && (
            <button
              onClick={onClose}
              className="p-2.5 rounded-2xl border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Close Audit Studio"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Optical Scanner & Auto-Verification Control Bar */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white p-5 rounded-3xl shadow-xl border border-blue-700/40 relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-44 h-44 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />
        
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-amber-500 text-slate-950 flex items-center gap-1 shadow-sm">
                <Zap className="w-3 h-3 fill-slate-950" />
                Optical Report Ingestion
              </span>
              <span className="text-xs text-blue-200 font-medium">
                Live Camera Scanner & AI Text Extraction
              </span>
            </div>
            <h3 className="text-sm sm:text-base font-bold text-white mt-1">
              Scan or Upload Laboratory Test Certificate for Instant Auto-Verification
            </h3>
          </div>

          {/* Action Buttons & Auto-Verify Switch */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Auto-Verify Toggle */}
            <label className="flex items-center space-x-2 cursor-pointer bg-white/10 hover:bg-white/15 px-3 py-1.5 rounded-xl border border-white/20 transition-colors">
              <input
                type="checkbox"
                checked={autoVerifyOnExtract}
                onChange={(e) => setAutoVerifyOnExtract(e.target.checked)}
                className="w-4 h-4 rounded text-blue-600 focus:ring-0 cursor-pointer accent-emerald-500"
              />
              <span className="text-xs font-semibold text-slate-100 flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                Auto-Verify Immediately
              </span>
            </label>

            {/* Camera Scan Button */}
            <button
              onClick={() => (isCameraActive ? stopCamera() : startCamera())}
              disabled={isCameraLoading || isExtracting}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-md ${
                isCameraActive
                  ? 'bg-rose-600 hover:bg-rose-700 text-white'
                  : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-500/20'
              }`}
            >
              {isCameraLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : isCameraActive ? (
                <CameraOff className="w-4 h-4" />
              ) : (
                <Camera className="w-4 h-4" />
              )}
              <span>{isCameraActive ? 'Close Camera' : 'Scan Lab Report (Camera)'}</span>
            </button>

            {/* File Upload Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isExtracting}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-bold transition-colors shadow-sm"
            >
              <Upload className="w-4 h-4 text-blue-300" />
              <span>Upload Certificate</span>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,application/pdf"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>
        </div>

        {/* Quick Sample Test Reports (One-Click Testing) */}
        <div className="mt-4 pt-3 border-t border-white/10 flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-semibold text-blue-200 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-400" />
            Quick Demo Reports:
          </span>
          {SAMPLE_LAB_REPORTS.map((s) => (
            <button
              key={s.id}
              onClick={() => handleLoadSampleReport(s)}
              disabled={isExtracting}
              className="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 border border-white/15 text-[11px] font-medium text-slate-200 hover:text-white transition-all flex items-center gap-1.5"
            >
              <span className={`w-1.5 h-1.5 rounded-full ${s.badgeColor}`} />
              <span>{s.title.split('(')[0].trim()}</span>
              <span className="text-[9px] font-bold text-amber-300 bg-black/30 px-1 rounded">
                {s.standard_code}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Live Camera Scanner Viewport */}
      {isCameraActive && (
        <div className="glass-panel-3d p-4 rounded-3xl border-2 border-blue-500/50 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-rose-500 animate-ping" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                <Camera className="w-4 h-4 text-blue-600" />
                Live Laboratory Report Document Scanner
              </h3>
            </div>
            <div className="flex items-center space-x-2">
              {hasMultipleCameras && (
                <button
                  onClick={flipCamera}
                  className="px-3 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-semibold rounded-lg text-slate-700 dark:text-slate-300 flex items-center gap-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Flip Camera
                </button>
              )}
              <button
                onClick={stopCamera}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {cameraError ? (
            <div className="p-6 text-center text-rose-600 dark:text-rose-400 text-xs">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-rose-500" />
              <p className="font-bold">{cameraError}</p>
            </div>
          ) : (
            <div className="relative mt-3 rounded-2xl overflow-hidden bg-black max-h-[460px] flex items-center justify-center">
              <video
                ref={videoRef}
                playsInline
                muted
                className="w-full max-h-[440px] object-contain"
              />

              {/* Target Bounding Frame & Laser Scanner Line Overlay */}
              <div className="absolute inset-6 border-2 border-dashed border-emerald-400/80 rounded-2xl pointer-events-none flex flex-col justify-between p-4 shadow-[0_0_25px_rgba(16,185,129,0.2)]">
                <div className="flex justify-between items-start">
                  <span className="w-6 h-6 border-t-4 border-l-4 border-emerald-400 rounded-tl-lg" />
                  <span className="px-3 py-1 rounded-full bg-black/60 backdrop-blur-md text-[11px] font-bold text-emerald-300 border border-emerald-400/40">
                    Align Lab Report Table Here
                  </span>
                  <span className="w-6 h-6 border-t-4 border-r-4 border-emerald-400 rounded-tr-lg" />
                </div>

                {/* Animated Horizontal Scanning Laser */}
                <div className="w-full h-0.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent shadow-[0_0_12px_#34d399] animate-pulse" />

                <div className="flex justify-between items-end">
                  <span className="w-6 h-6 border-b-4 border-l-4 border-emerald-400 rounded-bl-lg" />
                  <span className="text-[10px] text-white/70 bg-black/40 px-2 py-0.5 rounded">
                    Hold Steady for Clear Character Recognition
                  </span>
                  <span className="w-6 h-6 border-b-4 border-r-4 border-emerald-400 rounded-br-lg" />
                </div>
              </div>

              {/* Capture Action Floating Overlay */}
              <div className="absolute bottom-5 inset-x-0 flex justify-center">
                <button
                  onClick={captureFrame}
                  className="flex items-center space-x-2 px-6 py-3 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-sm shadow-xl shadow-emerald-950/60 hover:scale-105 active:scale-95 transition-all"
                >
                  <Camera className="w-5 h-5" />
                  <span>Capture & Extract Report</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* OCR Extraction Progress Notification Banner */}
      {isExtracting && (
        <div className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-900 shadow-sm animate-in fade-in slide-in-from-top-2">
          <div className="flex items-center justify-between text-xs font-bold text-blue-900 dark:text-blue-200 mb-2">
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600 dark:text-blue-400" />
              <span>{ocrStatus || 'Analyzing laboratory document...'}</span>
            </span>
            <span className="font-mono">{ocrProgress}%</span>
          </div>
          <div className="w-full h-2 bg-blue-200 dark:bg-blue-900/60 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-600 to-emerald-500 transition-all duration-300 rounded-full"
              style={{ width: `${ocrProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Irrelevant Data Detected Alert Card */}
      {irrelevantAlert && (
        <div className="p-4 rounded-2xl border border-rose-300 dark:border-rose-900 bg-rose-50/95 dark:bg-rose-950/70 shadow-lg space-y-3 animate-in fade-in">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <span className="p-2 rounded-xl bg-rose-100 dark:bg-rose-900/60 text-rose-600 dark:text-rose-300 shrink-0 mt-0.5">
                <AlertTriangle className="w-5 h-5" />
              </span>
              <div>
                <h4 className="text-sm font-extrabold text-rose-900 dark:text-rose-100">
                  Irrelevant Data Detected — Audit Aborted
                </h4>
                <p className="text-xs text-rose-800 dark:text-rose-200 mt-0.5">
                  {irrelevantAlert.reason}
                </p>
                {irrelevantAlert.subject && (
                  <span className="inline-block mt-2 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-200/80 dark:bg-rose-900 text-rose-800 dark:text-rose-200 border border-rose-300 dark:border-rose-800">
                    Detected Subject: {irrelevantAlert.subject}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={() => {
                setIrrelevantAlert(null);
                setCapturedImage(null);
                setRawExtractedText('');
              }}
              className="text-xs text-rose-600 hover:text-rose-800 dark:text-rose-400 font-bold px-2.5 py-1 rounded-lg hover:bg-rose-100 dark:hover:bg-rose-900/50 transition-colors"
            >
              Dismiss
            </button>
          </div>
          <div className="text-[11px] text-rose-700 dark:text-rose-300 bg-white/80 dark:bg-slate-900/70 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900/60 leading-relaxed">
            <strong>Laboratory Audit Requirement:</strong> The uploaded image or document is not related to Indian Standards or laboratory quality compliance. Please capture or upload a genuine NABL/BIS test certificate, chemical/physical test analysis, or parameter table (e.g. IS 14543 water, IS 1786 steel, IS 269 cement).
          </div>
        </div>
      )}

      {/* Extracted Certificate Traceability Banner (If text or image is captured and data is relevant) */}
      {(rawExtractedText || capturedImage) && !irrelevantAlert && (
        <div className="glass-panel-3d p-4 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                Extracted Report Inspection Data
              </span>
              {extractionMethod && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300">
                  {extractionMethod}
                </span>
              )}
              {confidenceScore && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                  Confidence: {confidenceScore}%
                </span>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowRawText(!showRawText)}
                className="text-xs font-semibold text-blue-600 dark:text-sky-400 hover:underline flex items-center gap-1"
              >
                {showRawText ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                <span>{showRawText ? 'Hide Raw OCR' : 'View Raw OCR Text'}</span>
              </button>
              <button
                onClick={() => {
                  setRawExtractedText('');
                  setCapturedImage(null);
                  setAuditResult(null);
                }}
                className="text-xs font-medium text-slate-400 hover:text-rose-600"
                title="Clear scanned data"
              >
                Clear
              </button>
            </div>
          </div>

          {capturedImage && (
            <div className="flex items-center space-x-3 p-2 bg-slate-50 dark:bg-slate-900 rounded-xl">
              <img
                src={capturedImage}
                alt="Captured Lab Certificate"
                className="w-16 h-16 object-cover rounded-lg border border-slate-200 dark:border-slate-700"
              />
              <div className="text-xs">
                <span className="font-semibold text-slate-700 dark:text-slate-300 block">
                  Scanned Lab Certificate Snapshot
                </span>
                <span className="text-slate-500 text-[11px]">
                  All test parameters mapped directly into the audit fields below.
                </span>
              </div>
            </div>
          )}

          {showRawText && (
            <div className="mt-2 p-3 bg-slate-900 text-slate-200 rounded-xl text-[11px] font-mono whitespace-pre-wrap max-h-48 overflow-y-auto border border-slate-800">
              {rawExtractedText}
            </div>
          )}
        </div>
      )}

      {/* Main Form & Results Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Metadata & Parameter Inputs (7 cols) */}
        <div className="lg:col-span-7 space-y-5">
          {/* Metadata Card */}
          <div className="glass-panel-3d p-5 rounded-3xl space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
              <Building className="w-4 h-4 text-blue-600" />
              <span>Audit Sample & Manufacturer Details</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">
                  Target IS Standard Code:
                </label>
                <input
                  type="text"
                  value={standardCode}
                  onChange={(e) => setStandardCode(e.target.value)}
                  placeholder="e.g. IS 14543 or IS 1786"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono font-bold text-blue-700 dark:text-blue-400"
                />
              </div>

              <div>
                <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">
                  Product / Commodity Name:
                </label>
                <input
                  type="text"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  placeholder="e.g. Packaged Drinking Water"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-800 dark:text-slate-200"
                />
              </div>

              <div>
                <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">
                  Manufacturer / Licensee Name:
                </label>
                <input
                  type="text"
                  value={manufacturerName}
                  onChange={(e) => setManufacturerName(e.target.value)}
                  placeholder="e.g. Stark Industries Beverages"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800 dark:text-slate-200"
                />
              </div>

              <div>
                <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">
                  Batch / Lot Identification No:
                </label>
                <input
                  type="text"
                  value={batchNumber}
                  onChange={(e) => setBatchNumber(e.target.value)}
                  placeholder="e.g. HMS-2026-B402"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-slate-800 dark:text-slate-200"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-slate-600 dark:text-slate-400 font-medium mb-1">
                  Accredited Testing Laboratory:
                </label>
                <input
                  type="text"
                  list="recognized-labs-list"
                  value={testingLab}
                  onChange={(e) => setTestingLab(e.target.value)}
                  placeholder="e.g. BIS Central Laboratory, Sahibabad (NABL Accredited)"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800 dark:text-slate-200"
                />
                <datalist id="recognized-labs-list">
                  <option value="BIS Central Laboratory, Sahibabad (NABL TC-5012)" />
                  <option value="BIS Western Regional Laboratory (WRL), Mumbai" />
                  <option value="BIS Southern Regional Laboratory (SRL), Chennai" />
                  <option value="BIS Eastern Regional Laboratory (ERL), Kolkata" />
                  <option value="BIS Northern Regional Laboratory (NRL), Mohali" />
                  <option value="Shriram Institute for Industrial Research (NABL TC-5421)" />
                  <option value="National Council for Cement and Building Materials (NCCBM), Ballabgarh" />
                  <option value="CSIR - National Environmental Engineering Research Institute (NEERI), Nagpur" />
                </datalist>
                <div className="flex items-center gap-1.5 overflow-x-auto pt-1.5 scrollbar-none">
                  <span className="text-[10px] text-slate-400 shrink-0">Quick Select Lab:</span>
                  {[
                    'BIS Central Lab (Sahibabad)',
                    'WRL Mumbai',
                    'SRL Chennai',
                    'Shriram Institute (NABL)',
                    'NCCBM Ballabgarh'
                  ].map((l) => (
                    <button
                      key={l}
                      type="button"
                      onClick={() =>
                        setTestingLab(
                          l.includes('BIS Central')
                            ? 'BIS Central Laboratory, Sahibabad (NABL TC-5012)'
                            : l.includes('Shriram')
                            ? 'Shriram Institute for Industrial Research (NABL TC-5421)'
                            : l.includes('NCCBM')
                            ? 'NCCBM Central Testing Laboratories, Ballabgarh (NABL Accredited)'
                            : `${l} (NABL Accredited)`
                        )
                      }
                      className="px-2 py-0.5 rounded text-[10px] bg-slate-100 hover:bg-blue-50 dark:bg-slate-800 dark:hover:bg-blue-900/30 text-slate-600 dark:text-slate-300 hover:text-blue-600 border border-slate-200 dark:border-slate-700 shrink-0 transition-colors"
                    >
                      {l}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Test Parameters Grid */}
          <div className="bg-white dark:bg-[#111827] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
                <Beaker className="w-4 h-4" />
                <span>Laboratory Observed Test Parameters ({parameters.length})</span>
              </h3>
              <button
                onClick={handleAddParameter}
                className="flex items-center space-x-1 px-3 py-1 text-xs font-semibold bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Parameter</span>
              </button>
            </div>

            <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
              {parameters.map((param, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-2 bg-slate-50 dark:bg-slate-900/80 p-2.5 rounded-xl border border-slate-200 dark:border-slate-800"
                >
                  <div className="flex-1 grid grid-cols-12 gap-2 text-xs">
                    <div className="col-span-5">
                      <input
                        type="text"
                        placeholder="Parameter Name (e.g. pH, Lead)"
                        value={param.parameter_name}
                        onChange={(e) => handleParameterChange(index, 'parameter_name', e.target.value)}
                        className="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none font-semibold text-slate-800 dark:text-slate-200"
                      />
                    </div>
                    <div className="col-span-4">
                      <input
                        type="text"
                        placeholder="Tested Value (e.g. 7.2)"
                        value={param.tested_value}
                        onChange={(e) => handleParameterChange(index, 'tested_value', e.target.value)}
                        className="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none font-mono text-slate-800 dark:text-slate-200"
                      />
                    </div>
                    <div className="col-span-3">
                      <input
                        type="text"
                        placeholder="Unit (mg/L, %)"
                        value={param.unit}
                        onChange={(e) => handleParameterChange(index, 'unit', e.target.value)}
                        className="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none text-slate-500 font-mono"
                      />
                    </div>
                  </div>

                  <button
                    onClick={() => handleRemoveParameter(index)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg transition-colors"
                    title="Remove parameter"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            {/* Run Audit Action Button */}
            <button
              onClick={handleRunAudit}
              disabled={loading || parameters.length === 0}
              className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl bg-gradient-to-r from-blue-700 to-indigo-800 hover:from-blue-800 hover:to-indigo-900 text-white font-bold text-sm shadow-md shadow-blue-500/20 disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Cross-Referencing Standard Tolerances & Generating Verdict...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Execute Automated AI Conformity Audit</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Audit Results & Official Verdict (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          {auditResult ? (
            <div className="space-y-4 animate-in fade-in slide-in-from-right-2 duration-300">
              {/* Verdict Summary Card */}
              <div
                className={`p-6 rounded-2xl border shadow-sm ${
                  verdictStyles[auditResult.overall_verdict]?.bg
                } ${verdictStyles[auditResult.overall_verdict]?.border}`}
              >
                <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800/80">
                  <div className="flex items-center space-x-2">
                    {verdictStyles[auditResult.overall_verdict]?.icon}
                    <span className="font-bold text-xs uppercase tracking-wider text-slate-600 dark:text-slate-300">
                      Audit Conformity Verdict:
                    </span>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-extrabold tracking-wide uppercase ${
                      verdictStyles[auditResult.overall_verdict]?.badge
                    }`}
                  >
                    {auditResult.overall_verdict.replace('_', ' ')}
                  </span>
                </div>

                {/* Score Dial */}
                <div className="py-4 flex items-center justify-between">
                  <div>
                    <span className="text-[11px] font-semibold text-slate-500 block">
                      Overall Compliance Score:
                    </span>
                    <span className="text-3xl font-black font-mono tracking-tight text-slate-900 dark:text-white">
                      {auditResult.compliance_score_percent}%
                    </span>
                  </div>
                  <div className="text-right text-xs">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold block">
                      ✔ {auditResult.passed_count} Passed
                    </span>
                    <span className="text-rose-600 dark:text-rose-400 font-bold block">
                      ✖ {auditResult.failed_count} Failed
                    </span>
                    <span className="text-slate-400 block">
                      Total {auditResult.total_count} Parameters
                    </span>
                  </div>
                </div>

                {/* Summary Text */}
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed pt-2 border-t border-slate-200/80 dark:border-slate-800/80">
                  {auditResult.summary}
                </p>

                {/* PDF Download Button */}
                <button
                  onClick={handleDownloadReport}
                  className="mt-4 w-full flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-slate-900 dark:bg-slate-800 hover:bg-slate-800 text-white text-xs font-bold shadow transition-all cursor-pointer"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Official BIS Audit Report (PDF)</span>
                </button>
              </div>

              {/* Parameter-by-Parameter Checklist */}
              <div className="bg-white dark:bg-[#111827] p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Clause-by-Clause Evaluation Checklist
                  </h3>
                  <span className="text-[10px] text-slate-400 font-mono">
                    IS Code: {auditResult.standard_is_code}
                  </span>
                </div>

                <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
                  {auditResult.parameter_results.map((res, rIdx) => {
                    const isPass = res.status === 'PASS';
                    return (
                      <div
                        key={rIdx}
                        className={`p-3 rounded-xl border text-xs ${
                          isPass
                            ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-900/40'
                            : 'bg-rose-50/40 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/40'
                        }`}
                      >
                        <div className="flex items-center justify-between font-bold">
                          <span className="text-slate-900 dark:text-slate-100">{res.parameter_name}</span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                              isPass ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white'
                            }`}
                          >
                            {res.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-200/60 dark:border-slate-800/60 text-[11px]">
                          <div>
                            <span className="text-slate-500 block">Tested Value:</span>
                            <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                              {res.tested_value}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-500 block">Standard Limit:</span>
                            <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                              {res.standard_limit}
                            </span>
                          </div>
                        </div>

                        <div className="mt-2 text-[10px] text-slate-500">
                          <span className="font-semibold text-blue-600 dark:text-sky-400">
                            {res.clause_reference}
                          </span>
                          {res.deviation && res.deviation !== '0.00% (Within Limits)' && (
                            <span className="ml-2 font-bold text-rose-600 dark:text-rose-400">
                              [{res.deviation}]
                            </span>
                          )}
                          <p className="mt-0.5 italic">{res.remarks}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            /* Blank state */
            <div className="bg-white dark:bg-[#111827] p-8 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 text-center flex flex-col items-center justify-center min-h-[380px]">
              <div className="p-4 rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 mb-3">
                <FileCheck2 className="w-8 h-8" />
              </div>
              <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                Awaiting Laboratory Parameters
              </h4>
              <p className="text-xs text-slate-500 max-w-xs mt-1 leading-relaxed">
                Scan your laboratory test certificate with the <b>Camera</b>, upload a test report document, or click one of the <b>Quick Demo Reports</b> above.
              </p>
              <div className="mt-4 flex items-center justify-center gap-2">
                <button
                  onClick={() => startCamera()}
                  className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>Start Camera</span>
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3.5 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 text-xs font-semibold flex items-center gap-1.5 border border-slate-200 dark:border-slate-700"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload File</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComplianceWorkspace;
