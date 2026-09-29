export type ChatMode = 'industry' | 'consumer';

export type UserRole = 'citizen' | 'industry' | 'procurement' | 'admin';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  organization?: string;
  mobile?: string;
  designation?: string;
  isGuest?: boolean;
  avatarUrl?: string;
  createdAt?: string;
}

export interface Citation {
  is_code: string;
  title: string;
  clause: string;
  page_number: number;
  snippet: string;
  similarity_score: number;
  is_table?: boolean;
  table_number?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  mode?: ChatMode;
  citations?: Citation[];
  table_references?: any[];
  confidence_score?: number;
  refusal_triggered?: boolean;
  needs_clarification?: boolean;
  disambiguation_options?: Array<{ label: string; query: string; description?: string }>;
  suggested_followups?: string[];
  feedbackGiven?: 'thumbs_up' | 'thumbs_down' | null;
  procurement_recommendation?: any;
  is_tender_upload?: boolean;
  tender_items?: any[];
  tender_file_name?: string;
  language?: string;
  original_content?: string;
  is_translating?: boolean;
  timestamp: string;
}

export interface TranslateResponse {
  original_text: string;
  translated_text: string;
  target_language: string;
  language_name: string;
  native_name: string;
}

export interface LanguageItem {
  name: string;
  native: string;
  flag: string;
  voice_code: string;
}


export interface StandardMetadata {
  is_code: string;
  title: string;
  year: string;
  category: string;
  chunk_count: number;
  table_count: number;
  created_at: string;
}

export interface TableData {
  id: string;
  is_code: string;
  table_number: string;
  table_title: string;
  clause: string;
  page_number: number;
  columns: string[];
  rows: string[][];
  markdown_repr: string;
}

export type ComplianceStatus = 'PASS' | 'FAIL' | 'CONDITIONAL' | 'NOT_TESTED';
export type OverallVerdict = 'CONFORMING' | 'NON_CONFORMING' | 'CONDITIONAL_COMPLIANCE';

export interface AuditParameterInput {
  parameter_name: string;
  tested_value: string;
  unit: string;
  notes?: string;
}

export interface AuditRequest {
  standard_is_code: string;
  product_name: string;
  manufacturer_name: string;
  batch_number: string;
  testing_lab: string;
  parameters: AuditParameterInput[];
}

export interface ParameterAuditResult {
  parameter_name: string;
  tested_value: string;
  standard_limit: string;
  unit: string;
  clause_reference: string;
  status: ComplianceStatus;
  deviation?: string;
  remarks: string;
}

export interface AuditResponse {
  audit_id: string;
  standard_is_code: string;
  standard_title: string;
  product_name: string;
  manufacturer_name: string;
  batch_number: string;
  testing_lab: string;
  overall_verdict: OverallVerdict;
  passed_count: number;
  failed_count: number;
  warning_count: number;
  total_count: number;
  compliance_score_percent: number;
  summary: string;
  parameter_results: ParameterAuditResult[];
  report_download_url: string;
  created_at: string;
}

export interface AuditTemplate {
  id: string;
  name: string;
  standard_is_code: string;
  product_name: string;
  manufacturer_name: string;
  batch_number: string;
  testing_lab: string;
  parameters: AuditParameterInput[];
}

export interface AuditReportExtractRequest {
  raw_text?: string;
  image_base64?: string;
  auto_verify?: boolean;
}

export interface ExtractedLabReportData {
  status: string;
  is_relevant?: boolean;
  relevance_reason?: string;
  detected_subject?: string;
  corrected_text?: string;
  standard_is_code: string;
  product_name: string;
  manufacturer_name: string;
  batch_number: string;
  testing_lab: string;
  parameters: AuditParameterInput[];
  extracted_text: string;
  confidence_score: number;
  extraction_method: string;
  verification?: AuditResponse | null;
}

export interface TelemetryDashboardResponse {
  total_queries: number;
  industry_queries: number;
  consumer_queries: number;
  positive_feedback_count: number;
  negative_feedback_count: number;
  satisfaction_rate: number;
  total_standards_indexed: number;
  total_tables_indexed: number;
  total_audits_performed: number;
  audit_conformance_rate: number;
  top_queried_standards: Array<{
    is_code: string;
    title: string;
    query_count: number;
  }>;
  recent_audits: Array<{
    id: string;
    standard_is_code: string;
    product_name: string;
    manufacturer_name: string;
    overall_verdict: string;
    compliance_score: number;
    created_at: string;
  }>;
  recent_feedback: Array<{
    id: string;
    query_id: string;
    rating: string;
    query_text: string;
    mode: string;
    comments: string;
    created_at: string;
  }>;
}

export interface LicenseVerifyResponse {
  is_valid: boolean;
  status: string;
  is_relevant?: boolean;
  relevance_reason?: string;
  detected_subject?: string;
  corrected_text?: string;
  mark_type: string;
  identifier: string;
  standard_code: string;
  product_name: string;
  manufacturer: string;
  brand_name?: string;
  company?: string;
  company_name?: string;
  parent_company?: string;
  product_type?: string;
  flagship_products?: string;
  license_type?: string;
  license_name?: string;
  issue_year?: string;
  expiry_date?: string;
  structure_breakdown?: {
    license_type?: string;
    state_authority?: string;
    grant_year?: string;
    registration_series?: string;
    [key: string]: string | undefined;
  };
  mrp?: string;
  online_price?: string;
  net_quantity?: string;
  batch_no?: string;
  barcode?: string;
  multi_unit_facilities?: Array<{ unit: string; location: string; license_no: string }>;
  packaging_registration?: string;
  operating_unit: string;
  valid_until: string;
  details: Record<string, any>;
  guidelines: string[];
  bis_care_instructions: string;
  grievance_redressal: string;
}

export interface BisServicesDirectoryData {
  standards_clubs: {
    title: string;
    category: string;
    ministry: string;
    tagline: string;
    overview: string;
    financial_grants: Array<{
      scheme: string;
      amount: string;
      purpose: string;
    }>;
    key_activities: string[];
    mentor_role: string;
    eligibility: string;
    how_to_enroll: string;
  };
  nits_training: {
    title: string;
    category: string;
    location: string;
    overview: string;
    core_programs: Array<{
      program: string;
      duration: string;
      target_audience: string;
      coverage: string;
    }>;
    international_outreach: string;
    enrollment_portal: string;
  };
  lab_recognition: {
    title: string;
    category: string;
    statutory_basis: string;
    overview: string;
    prerequisites: string[];
    audit_process: string[];
    benefits: string[];
    recognized_laboratories?: TestingLaboratory[];
  };
  consumer_protection: {
    title: string;
    category: string;
    statutory_basis: string;
    helpline: string;
    bis_care_app: {
      name: string;
      features: string[];
    };
    penalties_for_misuse: string;
  };
  departments_17: Array<{
    code: string;
    name: string;
    standards_count: number;
    scope: string;
  }>;
}

export interface TestingLaboratory {
  id: string;
  name: string;
  type: string;
  region: string;
  city: string;
  state: string;
  address: string;
  phone: string;
  email: string;
  nabl_accreditation: string;
  disciplines: string[];
  standards_supported: string[];
  description: string;
}

export type NutriPersona = 'general' | 'diabetic' | 'gluten_free' | 'infant' | 'heart';

export interface NutriAnalyzeResult {
  product_name: string;
  status?: string;
  is_relevant?: boolean;
  relevance_reason?: string;
  detected_subject?: string;
  corrected_text?: string;
  verdict: 'HARMFUL' | 'CAUTION' | 'SECURE' | string;
  verdict_badge: string;
  nutri_score_grade: 'A' | 'B' | 'C' | 'D' | 'E' | string;
  nutri_score_points: number;
  score_breakdown?: {
    negative_points: number;
    positive_points: number;
    net_score: number;
  };
  summary_verdict: string;
  spoken_summary: string;
  spoken_language: string;
  sodium_mg?: number | null;
  sodium_level: string;
  trans_fat_g?: number | null;
  trans_fat_status: string;
  saturated_fat_g?: number | null;
  added_sugar_g?: number | null;
  added_sugar_level: string;
  has_palm_oil: boolean;
  palm_oil_details?: string | null;
  hidden_sugars: Array<{
    name: string;
    description: string;
    risk_level: string;
    category: string;
  }>;
  harmful_additives: Array<{
    code: string;
    name: string;
    type: string;
    hazard: string;
    risk: string;
  }>;
  beneficial_ingredients: string[];
  persona_alerts: Array<{
    persona: string;
    severity: string;
    message: string;
  }>;
  fssai_compliance_notes: string[];
  raw_extracted_ingredients: string[];
  nutrition_table: Record<string, any>;
  all_ingredients_analysis?: Array<{
    name: string;
    category: string;
    health_effect: 'BENEFICIAL' | 'SAFE_NEUTRAL' | 'MODERATE_CAUTION' | 'HARMFUL' | string;
    health_advantage_or_risk: string;
    harmlessness_level: string;
  }>;
  govt_limit_comparison?: Array<{
    parameter: string;
    found_value: string;
    govt_recommended_limit: string;
    status: 'SAFE_WITHIN_LIMIT' | 'EXCEEDS_RECOMMENDED_LIMIT' | 'CRITICAL_EXCESS' | string;
    exceed_percentage?: string | null;
    warning_or_guidance: string;
  }>;
  usual_items_summary?: Array<{
    item_name: string;
    everyday_use_context: string;
    harmlessness_verdict: string;
    safe_daily_limit: string;
    processed_food_risk: string;
  }>;
}


