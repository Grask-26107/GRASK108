export interface SupportedLanguage {
  code: string;
  name: string;
  native: string;
  flag: string;
  voice: string;
}

export const SUPPORTED_LANGUAGES: SupportedLanguage[] = [
  { code: 'en', name: 'English', native: 'English', flag: '🇬🇧', voice: 'en-IN' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳', voice: 'hi-IN' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳', voice: 'te-IN' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳', voice: 'ta-IN' },
  { code: 'mr', name: 'Marathi', native: 'मराठी', flag: '🇮🇳', voice: 'mr-IN' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা', flag: '🇮🇳', voice: 'bn-IN' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳', voice: 'kn-IN' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી', flag: '🇮🇳', voice: 'gu-IN' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳', voice: 'ml-IN' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ', flag: '🇮🇳', voice: 'pa-IN' },
  { code: 'ur', name: 'Urdu', native: 'اردو', flag: '🇮🇳', voice: 'ur-IN' },
];
