import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  Award,
  FlaskConical,
  ShieldCheck,
  Building2,
  X,
  ExternalLink,
  BookOpen,
  DollarSign,
  Calendar,
  Users,
  CheckCircle2,
  PhoneCall,
  Sparkles,
  Layers
} from 'lucide-react';
import { standardsApi } from '../services/api';
import { BisServicesDirectoryData } from '../types';
import {
  DEFAULT_OFFLINE_BIS_SERVICES_DIRECTORY,
  OFFLINE_17_TECHNICAL_DEPARTMENTS,
  OFFLINE_TESTING_LABORATORIES
} from '../constants/bisOfflineData';

interface BisServicesModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultSection?: 'standards_clubs' | 'nits_training' | 'lab_recognition' | 'consumer_protection' | 'departments';
  onAskAi?: (query: string) => void;
}

export const BisServicesModal: React.FC<BisServicesModalProps> = ({
  isOpen,
  onClose,
  defaultSection = 'standards_clubs',
  onAskAi,
}) => {
  const [activeSection, setActiveSection] = useState<
    'standards_clubs' | 'nits_training' | 'lab_recognition' | 'consumer_protection' | 'departments'
  >(defaultSection);
  const [data, setData] = useState<BisServicesDirectoryData>(DEFAULT_OFFLINE_BIS_SERVICES_DIRECTORY);
  const [loading, setLoading] = useState(false);
  const [labSearch, setLabSearch] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [deptSearch, setDeptSearch] = useState('');

  useEffect(() => {
    setActiveSection(defaultSection);
  }, [defaultSection]);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      standardsApi
        .getServicesDirectory()
        .then((res) => {
          if (res && res.departments_17 && res.departments_17.length > 0) {
            setData(res);
          }
        })
        .catch((err) => console.debug('Using verified offline BIS Services Directory:', err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  const recognizedLabs = data?.lab_recognition?.recognized_laboratories?.length
    ? data.lab_recognition.recognized_laboratories
    : OFFLINE_TESTING_LABORATORIES;

  const filteredLabs = recognizedLabs.filter((lab) => {
    const matchesRegion = selectedRegion === 'all' || lab.region.toLowerCase() === selectedRegion.toLowerCase();
    if (!matchesRegion) return false;
    if (!labSearch.trim()) return true;
    const query = labSearch.toLowerCase();
    const matchesName = lab.name.toLowerCase().includes(query);
    const matchesCity = lab.city.toLowerCase().includes(query);
    const matchesState = lab.state.toLowerCase().includes(query);
    const matchesStandard = lab.standards_supported.some((s) => s.toLowerCase().includes(query));
    const matchesDiscipline = lab.disciplines.some((d) => d.toLowerCase().includes(query));
    return matchesName || matchesCity || matchesState || matchesStandard || matchesDiscipline;
  });

  const departmentsList = data?.departments_17?.length
    ? data.departments_17
    : OFFLINE_17_TECHNICAL_DEPARTMENTS;

  const filteredDepts = departmentsList.filter((dept) => {
    if (!deptSearch.trim()) return true;
    const q = deptSearch.toLowerCase();
    return (
      dept.code.toLowerCase().includes(q) ||
      dept.name.toLowerCase().includes(q) ||
      dept.scope.toLowerCase().includes(q)
    );
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative bg-white dark:bg-slate-900 w-full max-w-4xl rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[90vh]">
        {/* National Tricolor Top Accent */}
        <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600" />

        {/* Modal Header */}
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-700/50 flex items-center justify-center text-amber-600 dark:text-amber-400">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  Bureau of Indian Standards (BIS) Official Services Hub
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
                  SIH26107
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Official statutory initiatives mandated by the Ministry of Consumer Affairs, Food & Public Distribution
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Section Navigation Pills */}
        <div className="px-6 pt-3 pb-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex flex-wrap gap-2">
          <button
            onClick={() => setActiveSection('standards_clubs')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              activeSection === 'standards_clubs'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Standards Clubs (Schools & Colleges)</span>
          </button>

          <button
            onClick={() => setActiveSection('nits_training')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              activeSection === 'nits_training'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>NITS Training Programs</span>
          </button>

          <button
            onClick={() => setActiveSection('lab_recognition')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              activeSection === 'lab_recognition'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5" />
            <span>Laboratory Recognition (LRS)</span>
          </button>

          <button
            onClick={() => setActiveSection('consumer_protection')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              activeSection === 'consumer_protection'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Consumer Protection & BIS Care</span>
          </button>

          <button
            onClick={() => setActiveSection('departments')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              activeSection === 'departments'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>17 Technical Departments</span>
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* SECTION 1: STANDARDS CLUBS */}
          {activeSection === 'standards_clubs' && (
            <div className="space-y-5">
              <div className="bg-blue-50/80 dark:bg-blue-950/30 p-4 rounded-xl border border-blue-200 dark:border-blue-800/50">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-700 dark:text-blue-300 block mb-1">
                  Youth & Educational Standardization Flagship
                </span>
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  {data?.standards_clubs.title || 'BIS Standards Clubs in Educational Institutions'}
                </h4>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                  {data?.standards_clubs.overview ||
                    'Standards Clubs are established by BIS in schools and engineering colleges to cultivate quality consciousness, safety awareness, and scientific temper among youth through hands-on activities.'}
                </p>
              </div>

              {/* Financial Grants */}
              <div>
                <h5 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-2 flex items-center space-x-1">
                  <DollarSign className="w-4 h-4 text-emerald-600" />
                  <span>Statutory BIS Financial Grants & Assistance:</span>
                </h5>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold text-base block">₹10,000 / Year</span>
                    <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block mt-1">Activity Grant</span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 block mt-1">
                      For organizing competitions, quizzes, standards writing workshops, and debates.
                    </span>
                  </div>

                  <div className="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold text-base block">Up to ₹20,000</span>
                    <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block mt-1">Lab Science Upgrade</span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 block mt-1">
                      For upgrading school science laboratories under 'Learning Science via Standards' initiative.
                    </span>
                  </div>

                  <div className="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="text-blue-600 dark:text-blue-400 font-bold text-base block">100% Sponsored</span>
                    <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block mt-1">Exposure Visits</span>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 block mt-1">
                      Fully sponsored educational trips for students to NABL laboratories & factories.
                    </span>
                  </div>
                </div>
              </div>

              {/* Core Student Activities */}
              <div>
                <h5 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-2 flex items-center space-x-1">
                  <CheckCircle2 className="w-4 h-4 text-blue-600" />
                  <span>Key Activities for Students & Mentors:</span>
                </h5>
                <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 dark:text-blue-400 font-bold">•</span>
                    <span><strong>Learning Science via Standards:</strong> Curriculum-aligned experiment modules connecting classroom chemistry and physics to IS codes.</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 dark:text-blue-400 font-bold">•</span>
                    <span><strong>Standards Writing Competitions:</strong> Students draft mini-standards for common household products (e.g., school bags, reusable bottles).</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 dark:text-blue-400 font-bold">•</span>
                    <span><strong>Consumer Outreach Rallies:</strong> Sensitizing local communities on checking authentic ISI marks and 6-digit HUID Gold Hallmarks.</span>
                  </li>
                </ul>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                <div>
                  <span className="font-semibold text-slate-800 dark:text-slate-200 block">How Educational Institutions Can Enroll:</span>
                  <span className="text-slate-500 dark:text-slate-400 text-[11px]">
                    School Principals can apply via the nearest BIS Branch Office (BO) or the Standards Promotion Portal.
                  </span>
                </div>
                <a
                  href="https://www.bis.gov.in"
                  target="_blank"
                  rel="noreferrer"
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold shrink-0 transition-colors inline-flex items-center space-x-1"
                >
                  <span>Official BIS Portal</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          )}

          {/* SECTION 2: NITS TRAINING */}
          {activeSection === 'nits_training' && (
            <div className="space-y-5">
              <div className="bg-amber-50/80 dark:bg-amber-950/30 p-4 rounded-xl border border-amber-200 dark:border-amber-800/50">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300 block mb-1">
                  Apex Standardization & Quality Training Institute
                </span>
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  National Institute of Training for Standardization (NITS)
                </h4>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                  Located in Sector 62, Noida, NITS provides professional training programs for industry engineers, quality managers, testing laboratories, faculty, and international delegates under ITEC/SCAAP.
                </p>
              </div>

              {/* Core Programs */}
              <div>
                <h5 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-2 flex items-center space-x-1">
                  <Calendar className="w-4 h-4 text-amber-600" />
                  <span>Flagship NITS Professional Programs:</span>
                </h5>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="font-bold text-slate-900 dark:text-white block">
                      ISO/IEC 17025 Laboratory QMS (4 Days)
                    </span>
                    <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-1">
                      For testing laboratory managers: measurement uncertainty, method validation, equipment calibration, and NABL compliance.
                    </p>
                  </div>

                  <div className="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="font-bold text-slate-900 dark:text-white block">
                      Lead Auditor Certifications (5 Days)
                    </span>
                    <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-1">
                      IRCA/NABCB recognized Lead Auditor training for ISO 9001 (QMS), ISO 14001 (EMS), ISO 22000 (FSMS), and ISO 27001 (ISMS).
                    </p>
                  </div>

                  <div className="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="font-bold text-slate-900 dark:text-white block">
                      Statistical Quality Control & Sampling (3 Days)
                    </span>
                    <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-1">
                      For factory production teams: IS 2500 sampling tables, control charts, and Scheme of Inspection and Testing (SIT).
                    </p>
                  </div>

                  <div className="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700">
                    <span className="font-bold text-slate-900 dark:text-white block">
                      Conformity Assessment for MSMEs (2 Days)
                    </span>
                    <p className="text-slate-500 dark:text-slate-400 text-[11px] mt-1">
                      For startups and MSMEs: How to obtain ISI certification under the Simplified Procedure within 30 days.
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 flex justify-between items-center text-xs">
                <span className="text-slate-600 dark:text-slate-400">
                  Direct Enrollment: <strong>nits@bis.gov.in</strong> or via Manakonline portal
                </span>
                <a
                  href="https://www.bis.gov.in/nits/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-amber-600 dark:text-amber-400 hover:underline font-semibold flex items-center space-x-1"
                >
                  <span>View Training Calendar</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          )}

          {/* SECTION 3: LAB RECOGNITION (LRS) & TESTING LABORATORIES DIRECTORY */}
          {activeSection === 'lab_recognition' && (
            <div className="space-y-6">
              <div className="bg-emerald-50/80 dark:bg-emerald-950/30 p-4 rounded-xl border border-emerald-200 dark:border-emerald-800/50">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">
                    Section 13(4) of the BIS Act, 2016
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300">
                    NABL ISO/IEC 17025
                  </span>
                </div>
                <h4 className="text-base font-bold text-slate-900 dark:text-white mt-1">
                  {data?.lab_recognition?.title || 'Laboratory Recognition Scheme (LRS) 2020 & Testing Facilities'}
                </h4>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                  {data?.lab_recognition?.overview ||
                    'BIS operates an apex Central Laboratory in Sahibabad, four Regional Laboratories, and recognizes hundreds of independent commercial, academic, and government laboratories across India for conformity assessment and market surveillance sample testing.'}
                </p>
              </div>

              {/* Mandatory Prerequisites */}
              <div>
                <h5 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Mandatory Prerequisites for Recognition:</span>
                </h5>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                  <div className="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                    <strong className="text-slate-900 dark:text-white block mb-1">1. NABL Accreditation</strong>
                    <span className="text-slate-600 dark:text-slate-400 text-[11px]">
                      Valid ISO/IEC 17025 accreditation strictly covering test parameters of target Indian Standards.
                    </span>
                  </div>
                  <div className="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                    <strong className="text-slate-900 dark:text-white block mb-1">2. Metrological Traceability</strong>
                    <span className="text-slate-600 dark:text-slate-400 text-[11px]">
                      All apparatus must possess unbroken calibration certificates traceable directly to CSIR-NPL.
                    </span>
                  </div>
                  <div className="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                    <strong className="text-slate-900 dark:text-white block mb-1">3. PT & ILC Records</strong>
                    <span className="text-slate-600 dark:text-slate-400 text-[11px]">
                      Documented satisfactory z-scores in Proficiency Testing and Inter-Laboratory Comparisons.
                    </span>
                  </div>
                </div>
              </div>

              {/* Interactive Testing Laboratories Directory */}
              <div className="space-y-3 pt-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
                  <div>
                    <h5 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
                      <FlaskConical className="w-4 h-4 text-blue-600" />
                      <span>Recognized Testing Laboratories Directory</span>
                    </h5>
                    <p className="text-[11px] text-slate-500">
                      Apex Central, Regional, Branch & NABL Partner Laboratories for IS sample testing
                    </p>
                  </div>
                  <div className="text-xs text-blue-600 dark:text-blue-400 font-semibold">
                    {data?.lab_recognition?.recognized_laboratories?.length || 12} Registered Apex Facilities
                  </div>
                </div>

                {/* Search & Region Filter */}
                <div className="flex flex-col sm:flex-row gap-2">
                  <div className="relative flex-1">
                    <input
                      type="text"
                      placeholder="Search by IS code (e.g. IS 14543, IS 1786), lab name, city..."
                      value={labSearch}
                      onChange={(e) => setLabSearch(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="absolute left-3 top-2.5 text-slate-400">
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1 overflow-x-auto pb-1 sm:pb-0">
                    {['all', 'North', 'South', 'East', 'West'].map((region) => (
                      <button
                        key={region}
                        type="button"
                        onClick={() => setSelectedRegion(region)}
                        className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                          selectedRegion === region
                            ? 'bg-blue-600 text-white shadow-xs'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                        }`}
                      >
                        {region === 'all' ? 'All Regions' : region}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Laboratory Cards Grid */}
                <div className="space-y-3 max-h-[50vh] overflow-y-auto pr-1">
                  {filteredLabs.length === 0 ? (
                    <div className="text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                      No recognized laboratories match your search criteria. Try searching for "IS 14543", "Water", or "Delhi".
                    </div>
                  ) : (
                    filteredLabs.map((lab) => (
                      <div
                        key={lab.id}
                        className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xs hover:border-blue-400 transition-colors"
                      >
                        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="font-bold text-slate-900 dark:text-white text-sm">
                                {lab.name}
                              </span>
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700/50">
                                {lab.type}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                              {lab.address}, {lab.city}, {lab.state} • Region: <strong>{lab.region}</strong>
                            </p>
                          </div>

                          <div className="flex items-center space-x-1.5 self-start shrink-0">
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700/40">
                              {lab.nabl_accreditation}
                            </span>
                          </div>
                        </div>

                        {/* Disciplines & Standards Chips */}
                        <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-700/60 flex flex-wrap items-center gap-1.5 text-[11px]">
                          <span className="font-semibold text-slate-600 dark:text-slate-400 mr-1">
                            Testing Disciplines:
                          </span>
                          {lab.disciplines.map((d, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700/70 text-slate-700 dark:text-slate-200 rounded text-[10px] font-medium"
                            >
                              {d}
                            </span>
                          ))}
                        </div>

                        <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
                          <span className="font-semibold text-slate-600 dark:text-slate-400 mr-1">
                            Supported Standards:
                          </span>
                          {lab.standards_supported.map((std, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-0.5 bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 border border-amber-200/60 dark:border-amber-700/40 rounded text-[10px] font-bold"
                            >
                              {std}
                            </span>
                          ))}
                        </div>

                        {/* Contact details */}
                        <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-700/60 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-600 dark:text-slate-400">
                          <div className="flex items-center space-x-4">
                            <span>📞 <strong>{lab.phone}</strong></span>
                            <span>✉️ <strong>{lab.email}</strong></span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              type="button"
                              onClick={() => {
                                onClose();
                                onAskAi?.(`What are the testing facilities, NABL scope, and accredited IS standards at ${lab.name}?`);
                              }}
                              className="px-2.5 py-1 bg-blue-50 dark:bg-blue-900/40 hover:bg-blue-100 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-300 font-semibold rounded text-[11px] transition-colors flex items-center space-x-1"
                            >
                              <Sparkles className="w-3 h-3 text-blue-500" />
                              <span>Ask in Chat</span>
                            </button>
                            <a
                              href={`mailto:${lab.email}?subject=Inquiry regarding sample testing for BIS Certification`}
                              className="px-2.5 py-1 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 font-semibold rounded text-[11px] transition-colors"
                            >
                              Protocol
                            </a>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* SECTION 4: CONSUMER PROTECTION & GRIEVANCES */}
          {activeSection === 'consumer_protection' && (
            <div className="space-y-5">
              <div className="bg-indigo-50/80 dark:bg-indigo-950/30 p-4 rounded-xl border border-indigo-200 dark:border-indigo-800/50">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-300 block mb-1">
                  Citizen Empowerment & Enforcement
                </span>
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  BIS Care Mobile App & Consumer Grievance Redressal
                </h4>
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                  The Bureau of Indian Standards protects Indian citizens through active market surveillance and direct grievance filing under the BIS Act, 2016.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2">
                  <span className="font-bold text-slate-900 dark:text-white flex items-center space-x-1.5">
                    <PhoneCall className="w-4 h-4 text-amber-500" />
                    <span>National Consumer Helpline (NCH)</span>
                  </span>
                  <p className="text-slate-600 dark:text-slate-300">
                    Dial toll-free <strong>1915</strong> (24x7) for immediate lodging of grievances regarding sub-standard products, overcharging, or fake marks.
                  </p>
                </div>

                <div className="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2">
                  <span className="font-bold text-slate-900 dark:text-white flex items-center space-x-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-500" />
                    <span>Statutory Penalties (Section 29)</span>
                  </span>
                  <p className="text-slate-600 dark:text-slate-300">
                    Misuse of ISI mark or sale of unhallmarked gold in notified areas carries imprisonment up to <strong>2 years</strong> or fine not less than <strong>₹2 Lakhs</strong>.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 5: 17 TECHNICAL DEPARTMENTS */}
          {activeSection === 'departments' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
                <div>
                  <h5 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
                    <Layers className="w-4 h-4 text-purple-600" />
                    <span>BIS 17 Division Councils (Technical Departments)</span>
                  </h5>
                  <p className="text-[11px] text-slate-500">
                    Formulating 24,084+ active Indian Standards across all national industries and emerging technologies
                  </p>
                </div>
                <div className="text-xs text-purple-600 dark:text-purple-400 font-semibold">
                  {filteredDepts.length} of {departmentsList.length} Division Councils
                </div>
              </div>

              {/* Search Bar for Departments */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search by code (e.g. CED, ETD, AYD), title, or domain (e.g. Cement, Cables, AI, Food)..."
                  value={deptSearch}
                  onChange={(e) => setDeptSearch(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <div className="absolute left-3 top-2.5 text-slate-400">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>

              {/* Grid of Department Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-[50vh] overflow-y-auto pr-1">
                {filteredDepts.length === 0 ? (
                  <div className="col-span-full text-center py-8 text-xs text-slate-400 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                    No Division Councils match "{deptSearch}". Try searching for "Steel", "Water", "ETD", or "AYD".
                  </div>
                ) : (
                  filteredDepts.map((dept) => (
                    <div
                      key={dept.code}
                      className="p-3.5 bg-white dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700/60 text-xs flex flex-col justify-between hover:border-purple-400 transition-colors shadow-2xs"
                    >
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-purple-600 dark:text-purple-400 font-mono text-sm">
                            {dept.code}
                          </span>
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-semibold border border-purple-200/50 dark:border-purple-700/40">
                            {dept.standards_count} Standards
                          </span>
                        </div>
                        <span className="font-semibold text-slate-800 dark:text-slate-200 block mt-1">
                          {dept.name}
                        </span>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-3 leading-relaxed">
                          {dept.scope}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() => {
                          onClose();
                          onAskAi?.(`Tell me about BIS ${dept.code} (${dept.name}) standards, scope, and key mandatory products.`);
                        }}
                        className="mt-3 w-full py-1.5 px-2 bg-purple-50 hover:bg-purple-100 dark:bg-purple-950/40 dark:hover:bg-purple-900/50 text-purple-700 dark:text-purple-300 font-semibold rounded-lg text-[11px] flex items-center justify-center space-x-1.5 transition-colors border border-purple-200/60 dark:border-purple-800/50"
                      >
                        <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                        <span>Ask AI in Chat</span>
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 flex justify-between items-center text-xs text-slate-500">
          <span>Bureau of Indian Standards | Government of India</span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-semibold rounded-xl transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
