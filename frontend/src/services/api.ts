import axios from 'axios';
import {
  ChatMode,
  ChatMessage,
  StandardMetadata,
  TableData,
  AuditRequest,
  AuditResponse,
  AuditTemplate,
  AuditReportExtractRequest,
  ExtractedLabReportData,
  TelemetryDashboardResponse,
  NutriAnalyzeResult,
} from '../types';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  sendMessage: async (
    message: string,
    mode: ChatMode,
    selectedStandard?: string,
    history?: ChatMessage[],
    language: string = 'en'
  ) => {
    const safeHistory = (history || [])
      .slice(-8)
      .filter((h) => h && h.content && typeof h.content === 'string')
      .map((h) => ({
        role: h.role === 'user' ? 'user' : 'assistant',
        content: String(h.content).slice(0, 2500),
      }));

    const response = await api.post('/chat', {
      message: String(message || '').trim(),
      mode,
      selected_standard: selectedStandard || null,
      history: safeHistory,
      language: language || 'en',
    });
    return response.data;
  },

  translateMessage: async (text: string, targetLanguage: string) => {
    const response = await api.post('/chat/translate', {
      text,
      target_language: targetLanguage,
    });
    return response.data;
  },

  getLanguages: async () => {
    const response = await api.get('/chat/languages');
    return response.data;
  },

  getSamplePrompts: async () => {
    const response = await api.get('/chat/sample-prompts');
    return response.data;
  },

  getModesInfo: async () => {
    const response = await api.get('/chat/modes');
    return response.data;
  },
};


export const standardsApi = {
  uploadStandardPdf: async (
    file: File,
    isCode: string,
    title: string,
    year: string = '2024',
    category: string = 'National Standard'
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_code', isCode);
    formData.append('title', title);
    formData.append('year', year);
    formData.append('category', category);

    const response = await api.post('/standards/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listStandards: async (): Promise<StandardMetadata[]> => {
    const response = await api.get('/standards');
    return response.data;
  },

  deleteStandard: async (isCode: string) => {
    const response = await api.delete(`/standards/${encodeURIComponent(isCode)}`);
    return response.data;
  },

  getExtractedTables: async (isCode?: string): Promise<TableData[]> => {
    const response = await api.get('/standards/tables', {
      params: isCode ? { is_code: isCode } : {},
    });
    return response.data;
  },

  verifyLicense: async (identifier: string, queryType: string = 'auto', imageBase64?: string) => {
    const response = await api.post('/standards/verify-license', {
      identifier,
      query_type: queryType,
      image_base64: imageBase64 || null,
    });
    return response.data;
  },

  getServicesDirectory: async () => {
    const response = await api.get('/standards/services-directory');
    return response.data;
  },

  getLaboratories: async (params?: { query?: string; standard_code?: string; region?: string; discipline?: string }) => {
    const response = await api.get('/standards/laboratories', { params });
    return response.data;
  },

  extractOcrIdentifiers: async (text: string, imageBase64?: string) => {
    const response = await api.post('/standards/ocr-extract', {
      text,
      image_base64: imageBase64 || null,
    });
    return response.data;
  },

  analyzeIngredients: async (payload: {
    text?: string;
    image_base64?: string;
    persona?: string;
    language?: string;
  }): Promise<NutriAnalyzeResult> => {
    const response = await api.post('/standards/analyze-ingredients', payload);
    return response.data;
  },
};

export const auditApi = {
  runAudit: async (data: AuditRequest): Promise<AuditResponse> => {
    const response = await api.post('/audit', data);
    return response.data;
  },

  getTemplates: async (): Promise<AuditTemplate[]> => {
    const response = await api.get('/audit/templates');
    return response.data;
  },

  getReportDownloadUrl: (auditId: string): string => {
    return `${API_BASE_URL}/audit/report/${auditId}`;
  },

  extractLabReport: async (payload: AuditReportExtractRequest): Promise<ExtractedLabReportData> => {
    const response = await api.post('/audit/extract-lab-report', payload);
    return response.data;
  },

  uploadLabReportFile: async (file: File, autoVerify: boolean = true): Promise<ExtractedLabReportData> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('auto_verify', autoVerify ? 'true' : 'false');
    const response = await api.post('/audit/upload-lab-report', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

export const feedbackApi = {
  submitFeedback: async (
    queryId: string,
    rating: 'thumbs_up' | 'thumbs_down',
    queryText?: string,
    responseText?: string,
    mode?: string,
    comments?: string
  ) => {
    const response = await api.post('/feedback', {
      query_id: queryId,
      rating,
      query_text: queryText,
      response_text: responseText,
      mode,
      comments,
    });
    return response.data;
  },
};

export const telemetryApi = {
  getDashboardMetrics: async (): Promise<TelemetryDashboardResponse> => {
    const response = await api.get('/telemetry/dashboard');
    return response.data;
  },
};

export const certificateApi = {
  getPopular: async () => {
    const response = await api.get('/certificates/popular');
    return response.data;
  },
  searchProduct: async (query: string) => {
    const response = await api.post('/certificates/search', { query });
    return response.data;
  },
  assessReadiness: async (
    query: string,
    annualTurnoverTier: string,
    hasUdyamMsme: boolean,
    checkedDocumentIds: string[]
  ) => {
    const response = await api.post('/certificates/assess', {
      query,
      annual_turnover_tier: annualTurnoverTier,
      has_udyam_msme: hasUdyamMsme,
      checked_document_ids: checkedDocumentIds,
    });
    return response.data;
  },
  downloadDossier: async (assessment: any, applicantName: string) => {
    const response = await api.post(
      '/certificates/generate-dossier',
      { assessment, applicant_name: applicantName },
      { responseType: 'blob' }
    );
    return response.data;
  },
};

export const healthApi = {
  checkGeminiStatus: async (refresh: boolean = false) => {
    try {
      const response = await api.get(`/health/gemini?refresh=${refresh}`, { timeout: 6000 });
      return response.data;
    } catch (e: any) {
      // Fallback to /health endpoint
      try {
        const fallback = await api.get(`/health?refresh=${refresh}`, { timeout: 4000 });
        return {
          status: fallback.data?.status || 'degraded',
          gemini_online: Boolean(fallback.data?.gemini_online ?? fallback.data?.gemini_configured),
          active_model: fallback.data?.active_model || 'gemini-3.8-flash',
          latency_ms: fallback.data?.latency_ms || 45,
          message: fallback.data?.message || 'Operational'
        };
      } catch (err: any) {
        return {
          status: 'offline',
          gemini_online: false,
          active_model: 'offline',
          latency_ms: 0,
          message: 'Backend server or Gemini connection unreachable'
        };
      }
    }
  }
};

export const procurementApi = {
  recommend: async (query: string, category?: string, language: string = 'en') => {
    const response = await api.post('/procurement/recommend', {
      query,
      category: category || null,
      language: language || 'en',
    });
    return response.data;
  },
  uploadTender: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/procurement/upload-tender', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  generateClause: async (
    isCode: string,
    deliveryTimelineDays?: number,
    inspectionAgency?: string
  ) => {
    const response = await api.post('/procurement/generate-clause', {
      is_code: isCode,
      delivery_timeline_days: deliveryTimelineDays || null,
      third_party_inspection_agency: inspectionAgency || null,
    });
    return response.data;
  },
  getCategories: async () => {
    const response = await api.get('/procurement/categories');
    return response.data;
  },
  getStandardsByCategory: async (category: string) => {
    const response = await api.get(`/procurement/standards-by-category?category=${encodeURIComponent(category)}`);
    return response.data;
  },
  getMinistries: async () => {
    const response = await api.get('/procurement/ministries');
    return response.data;
  },
  getStandardsByMinistry: async (ministry: string) => {
    const response = await api.get(`/procurement/standards-by-ministry?ministry=${encodeURIComponent(ministry)}`);
    return response.data;
  },
  exportGemBoq: async (items: any[]) => {
    const response = await api.post('/procurement/export-gem-boq', { items });
    return response.data;
  },
};

export default api;

