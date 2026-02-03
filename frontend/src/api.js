import axios from 'axios';

const API_BASE = '/api';

export const api = {
    // Profile
    getProfile: () => axios.get(`${API_BASE}/profile`),
    updateProfile: (data) => axios.post(`${API_BASE}/profile`, data),

    // Documents
    uploadDocument: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return axios.post(`${API_BASE}/documents/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    simplifyText: (text, language = 'en', dyslexiaType = 'general') =>
        axios.post(`${API_BASE}/documents/simplify`, { text, language, dyslexia_type: dyslexiaType }),

    summarizeText: (text, language = 'en', dyslexiaType = 'general') =>
        axios.post(`${API_BASE}/documents/summarize`, { text, language, dyslexia_type: dyslexiaType }),

    getDyslexiaTypes: () => axios.get(`${API_BASE}/documents/dyslexia-types`),

    // Speech
    textToSpeech: (text, language = 'en', speed = 1.0) =>
        axios.post(`${API_BASE}/speech/tts`, { text, language, speed }),

    getLanguages: () => axios.get(`${API_BASE}/speech/languages`),

    // Chat Q&A
    createChatSession: () => axios.get(`${API_BASE}/chat/new-session`),

    setDocumentContext: (documentText, sessionId) =>
        axios.post(`${API_BASE}/chat/set-context`, { document_text: documentText, session_id: sessionId }),

    askQuestion: (question, sessionId, language = 'en', dyslexiaType = 'general') =>
        axios.post(`${API_BASE}/chat/ask`, { question, session_id: sessionId, language, dyslexia_type: dyslexiaType }),

    clearChatContext: (sessionId) =>
        axios.delete(`${API_BASE}/chat/clear-context/${sessionId}`)
};

export default api;
