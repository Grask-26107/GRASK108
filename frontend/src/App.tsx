import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { ComplianceWorkspace } from './components/ComplianceWorkspace';
import { TelemetryDashboard } from './components/TelemetryDashboard';
import { LicenseVerifyModal } from './components/LicenseVerifyModal';
import { BisServicesModal } from './components/BisServicesModal';
import { NutriScoreModal } from './components/NutriScoreModal';
import { ReadyToApplyModal } from './components/ReadyToApplyModal';
import { CitationModal } from './components/CitationModal';
import { ProcurementTenderModal } from './components/ProcurementTenderModal';
import { SchemeFinderModal } from './components/SchemeFinderModal';
import { LoginPage } from './components/LoginPage';
import { UserProfileModal } from './components/UserProfileModal';
import { PortalHome } from './components/PortalHome';
import { ToastContainer, ToastMessage } from './components/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ChatMode, ChatMessage, Citation, UserProfile } from './types';

export const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('grask_theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [currentMode, setCurrentMode] = useState<ChatMode>('industry');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [pendingExternalQuery, setPendingExternalQuery] = useState<string | null>(null);

  // Modals & Overlays for SIH26107 Tools
  const [isLicenseModalOpen, setIsLicenseModalOpen] = useState(false);
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);
  const [isTelemetryModalOpen, setIsTelemetryModalOpen] = useState(false);
  const [isBisServiceModalOpen, setIsBisServiceModalOpen] = useState(false);
  const [isNutriModalOpen, setIsNutriModalOpen] = useState(false);
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [isSchemeFinderOpen, setIsSchemeFinderOpen] = useState(false);
  const [isProcurementModalOpen, setIsProcurementModalOpen] = useState(false);
  const [applyModalInitialQuery, setApplyModalInitialQuery] = useState('');
  const [bisServiceSection, setBisServiceSection] = useState<
    'standards_clubs' | 'nits_training' | 'lab_recognition' | 'consumer_protection' | 'departments'
  >('standards_clubs');

  // Authentication & User Profile State
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('grask_user');
    if (!saved) return null;
    try {
      return JSON.parse(saved);
    } catch {
      return null;
    }
  });
  const [isProfileModalOpen, setIsProfileModalOpen] = useState<boolean>(false);
  const [currentView, setCurrentView] = useState<'portal' | 'assistant'>('portal');

  const handleNavigateToAssistant = (initialQuery?: string, targetMode?: ChatMode) => {
    if (initialQuery) {
      setPendingExternalQuery(initialQuery);
    }
    if (targetMode && targetMode !== currentMode) {
      setCurrentMode(targetMode);
    }
    setCurrentView('assistant');
  };

  const handleLogin = (loggedInUser: UserProfile) => {
    setUser(loggedInUser);
    localStorage.setItem('grask_user', JSON.stringify(loggedInUser));
    if (loggedInUser.role === 'citizen') {
      setCurrentMode('consumer');
    } else {
      setCurrentMode('industry');
    }
    setCurrentView('portal');
    addToast('success', `Welcome, ${loggedInUser.name}! Session initialized.`);
  };

  const handleUpdateProfile = (updatedUser: UserProfile) => {
    setUser(updatedUser);
    localStorage.setItem('grask_user', JSON.stringify(updatedUser));
    if (updatedUser.role === 'citizen') {
      setCurrentMode('consumer');
    } else {
      setCurrentMode('industry');
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('grask_user');
    setIsProfileModalOpen(false);
    setCurrentView('portal');
    addToast('info', 'Signed out successfully.');
  };

  // Apply dark mode class to document element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('grask_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('grask_theme', 'light');
    }
  }, [darkMode]);

  const addToast = (type: 'success' | 'error' | 'info', message: string) => {
    const newToast: ToastMessage = {
      id: `toast-${Date.now()}-${Math.random()}`,
      type,
      message,
    };
    setToasts((prev) => [...prev, newToast]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleNewChat = () => {
    setMessages([]);
    addToast('info', 'Started fresh consultation session.');
  };

  const handleModeChange = (mode: ChatMode) => {
    if (mode !== currentMode) {
      setCurrentMode(mode);
      setMessages([]);
      addToast('info', `Switched to ${mode === 'industry' ? 'Industry & Engineering' : 'Citizen & Consumer'} Mode (Chat Cleared).`);
    }
  };

  const handleOpenLicenseVerify = () => {
    setIsLicenseModalOpen(true);
  };

  const handleOpenComplianceAudit = () => {
    setIsAuditModalOpen(true);
  };

  const handleOpenNutriScore = () => {
    setIsNutriModalOpen(true);
  };

  const handleOpenApplyModal = (query?: string) => {
    setApplyModalInitialQuery(query || '');
    setIsApplyModalOpen(true);
  };

  const handleOpenBisService = (
    section: 'standards_clubs' | 'nits_training' | 'lab_recognition' | 'consumer_protection' | 'departments'
  ) => {
    setBisServiceSection(section);
    setIsBisServiceModalOpen(true);
  };

  const handleOpenTelemetry = () => {
    setIsTelemetryModalOpen(true);
  };

  // If unauthenticated, show Unified Login Page
  if (!user) {
    return (
      <div className="min-h-screen w-screen bg-slate-50 dark:bg-slate-950 font-sans antialiased">
        <LoginPage
          onLogin={handleLogin}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
        />
        <ToastContainer toasts={toasts} removeToast={removeToast} />
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 dark:bg-slate-950 font-sans antialiased">
      {/* ChatGPT-style Left Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        currentMode={currentMode}
        onModeChange={handleModeChange}
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
        onNewChat={handleNewChat}
        onOpenLicenseVerify={handleOpenLicenseVerify}
        onOpenComplianceAudit={handleOpenComplianceAudit}
        onOpenNutriScore={handleOpenNutriScore}
        onOpenApplyModal={() => handleOpenApplyModal()}
        onOpenSchemeFinder={() => setIsSchemeFinderOpen(true)}
        onOpenProcurementTender={() => setIsProcurementModalOpen(true)}
        onOpenBisService={handleOpenBisService}
        onOpenTelemetry={handleOpenTelemetry}
        user={user}
        onOpenProfile={() => setIsProfileModalOpen(true)}
        onNavigateToPortal={() => setCurrentView('portal')}
      />

      {/* Right Area: Official Government Portal Home OR Dedicated AI Assistant Workspace */}
      {currentView === 'portal' ? (
        <div className="flex-1 h-full overflow-y-auto">
          <PortalHome
            user={user}
            onOpenProfile={() => setIsProfileModalOpen(true)}
            onNavigateToAssistant={handleNavigateToAssistant}
            onOpenLicenseVerify={handleOpenLicenseVerify}
            onOpenComplianceAudit={handleOpenComplianceAudit}
            onOpenNutriScore={handleOpenNutriScore}
            onOpenApplyModal={handleOpenApplyModal}
            onOpenSchemeFinder={() => setIsSchemeFinderOpen(true)}
            onOpenProcurementTender={() => setIsProcurementModalOpen(true)}
            onOpenBisService={handleOpenBisService}
            onOpenTelemetry={handleOpenTelemetry}
            darkMode={darkMode}
            onToggleDarkMode={() => setDarkMode(!darkMode)}
            selectedLanguage={selectedLanguage}
            onLanguageChange={setSelectedLanguage}
          />
        </div>
      ) : (
        <main className="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative">
          <ErrorBoundary>
            <ChatInterface
              currentMode={currentMode}
              onModeChange={handleModeChange}
              onSelectCitation={setSelectedCitation}
              addToast={addToast}
              onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
              onOpenLicenseVerify={handleOpenLicenseVerify}
              onOpenComplianceAudit={handleOpenComplianceAudit}
              onOpenNutriScore={handleOpenNutriScore}
              onOpenApplyModal={handleOpenApplyModal}
              selectedLanguage={selectedLanguage}
              onLanguageChange={setSelectedLanguage}
              messages={messages}
              setMessages={setMessages}
              externalQuery={pendingExternalQuery}
              onClearExternalQuery={() => setPendingExternalQuery(null)}
              darkMode={darkMode}
              onToggleDarkMode={() => setDarkMode(!darkMode)}
              user={user}
              onOpenProfile={() => setIsProfileModalOpen(true)}
              onNavigateToPortal={() => setCurrentView('portal')}
            />
          </ErrorBoundary>
        </main>
      )}

      {/* MANAK-Vision License & HUID Verification Modal */}
      <LicenseVerifyModal
        isOpen={isLicenseModalOpen}
        onClose={() => setIsLicenseModalOpen(false)}
        addToast={addToast}
      />

      {/* FSSAI Nutri-Score & Hidden Ingredient Decrypter Modal */}
      <NutriScoreModal
        isOpen={isNutriModalOpen}
        onClose={() => setIsNutriModalOpen(false)}
        addToast={addToast}
      />

      {/* Ready to Apply Statutory Certificate & Dossier Modal */}
      <ReadyToApplyModal
        isOpen={isApplyModalOpen}
        onClose={() => setIsApplyModalOpen(false)}
        addToast={addToast}
        initialQuery={applyModalInitialQuery}
      />

      {/* Scheme Finder (MSME & Certification Pathways) */}
      <SchemeFinderModal
        isOpen={isSchemeFinderOpen}
        onClose={() => setIsSchemeFinderOpen(false)}
        addToast={addToast}
      />

      {/* Official BIS Services Modal (Standards Clubs, NITS, LRS, Consumer Rights) */}
      <BisServicesModal
        isOpen={isBisServiceModalOpen}
        onClose={() => setIsBisServiceModalOpen(false)}
        defaultSection={bisServiceSection}
        onAskAi={(q) => setPendingExternalQuery(q)}
      />

      {/* Compliance Audit Studio Modal Overlay */}
      {isAuditModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative bg-white dark:bg-slate-900 w-full max-w-6xl rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[92vh]">
            <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600" />
            <div className="p-6 overflow-y-auto">
              <ComplianceWorkspace
                addToast={addToast}
                onClose={() => setIsAuditModalOpen(false)}
              />
            </div>
          </div>
        </div>
      )}

      {/* Government Oversight Telemetry Modal Overlay */}
      {isTelemetryModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative bg-white dark:bg-slate-900 w-full max-w-5xl rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[92vh]">
            <div className="h-1.5 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600" />
            <div className="p-6 overflow-y-auto">
              <TelemetryDashboard
                addToast={addToast}
                onClose={() => setIsTelemetryModalOpen(false)}
              />
            </div>
          </div>
        </div>
      )}

      {/* Citation Detail Modal */}
      {selectedCitation && (
        <CitationModal
          citation={selectedCitation}
          onClose={() => setSelectedCitation(null)}
        />
      )}

      {/* AI Tender Specification Assistant Modal (SIH26108) */}
      <ProcurementTenderModal
        isOpen={isProcurementModalOpen}
        onClose={() => setIsProcurementModalOpen(false)}
        addToast={addToast}
      />

      {/* User Profile & Role Switcher Modal */}
      <UserProfileModal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
        user={user}
        onUpdateProfile={handleUpdateProfile}
        onLogout={handleLogout}
        addToast={addToast}
      />

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  );
};

export default App;
