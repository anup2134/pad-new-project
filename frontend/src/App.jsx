import { useState, useEffect, useRef } from 'react'
import api from './api'

function App() {
    // Assessment state
    const [showAssessment, setShowAssessment] = useState(true);
    const [dyslexiaTypes, setDyslexiaTypes] = useState([]);

    // Settings state
    const [settings, setSettings] = useState({
        fontSize: 18,
        bgColor: '#FDF6E3',
        speechSpeed: 1.0,
        language: 'en',
        dyslexiaType: 'general',
        focusMode: false
    });

    // Content state
    const [text, setText] = useState('');
    const [processedText, setProcessedText] = useState('');
    const [inputMode, setInputMode] = useState('upload'); // 'upload' or 'type'

    // Audio state
    const [isPlaying, setIsPlaying] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [wordTimings, setWordTimings] = useState([]);
    const [currentWordIndex, setCurrentWordIndex] = useState(-1);
    const [audioUrl, setAudioUrl] = useState('');
    const [progress, setProgress] = useState(0);

    // Loading states
    const [loading, setLoading] = useState({
        upload: false,
        simplify: false,
        summarize: false,
        tts: false
    });

    // Languages
    const [languages, setLanguages] = useState([
        { code: 'en', name: 'English' },
        { code: 'es', name: 'Spanish' },
        { code: 'fr', name: 'French' },
        { code: 'de', name: 'German' },
        { code: 'it', name: 'Italian' },
        { code: 'pt', name: 'Portuguese' },
        { code: 'hi', name: 'Hindi' },
        { code: 'ar', name: 'Arabic' },
        { code: 'zh', name: 'Chinese' },
        { code: 'ja', name: 'Japanese' },
        { code: 'ko', name: 'Korean' },
        { code: 'ru', name: 'Russian' }
    ]);

    // Chat state
    const [chatSessionId, setChatSessionId] = useState(null);
    const [chatHistory, setChatHistory] = useState([]);
    const [chatQuestion, setChatQuestion] = useState('');
    const [showChat, setShowChat] = useState(false);
    const [chatLoading, setChatLoading] = useState(false);
    const chatEndRef = useRef(null);

    const audioRef = useRef(null);
    const fileInputRef = useRef(null);
    const recognitionRef = useRef(null);

    // Initialize Speech Recognition
    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = settings.language;

            recognition.onresult = (event) => {
                let finalTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    }
                }
                if (finalTranscript) {
                    setText(prev => prev + (prev.length > 0 ? ' ' : '') + finalTranscript);
                }
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsListening(false);
            };

            recognition.onend = () => {
                setIsListening(false);
            };

            recognitionRef.current = recognition;
        }
    }, [settings.language]);

    // Apply dynamic styles
    useEffect(() => {
        document.documentElement.style.setProperty('--font-size-base', `${settings.fontSize}px`);
        document.documentElement.style.setProperty('--bg-color', settings.bgColor);
    }, [settings.fontSize, settings.bgColor]);

    // Fetch languages and dyslexia types on mount
    useEffect(() => {
        // Set fallback dyslexia types immediately
        const fallbackTypes = [
            { code: 'phonological', name: 'Phonological Dyslexia', description: 'Difficulty connecting sounds to letters' },
            { code: 'surface', name: 'Surface Dyslexia', description: 'Difficulty recognizing whole word shapes' },
            { code: 'visual', name: 'Visual Dyslexia', description: 'Difficulty processing visual text' },
            { code: 'auditory', name: 'Auditory Dyslexia', description: 'Difficulty processing spoken language' },
            { code: 'mixed', name: 'Mixed/Deep Dyslexia', description: 'Combination of multiple difficulties' },
            { code: 'general', name: 'Not Sure / General', description: 'General reading support' }
        ];
        setDyslexiaTypes(fallbackTypes);

        // Try to fetch from API (with timeout)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout

        Promise.all([
            api.getLanguages().catch(() => { }),
            api.getDyslexiaTypes()
                .then(res => setDyslexiaTypes(res.data.types))
                .catch(() => { }) // Keep fallback if API fails
        ]).finally(() => clearTimeout(timeoutId));

        return () => {
            controller.abort();
            clearTimeout(timeoutId);
        };
    }, []);

    // Audio time update for word highlighting
    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        const handleTimeUpdate = () => {
            const currentTime = audio.currentTime * 1000; // Convert to ms
            setProgress((audio.currentTime / audio.duration) * 100 || 0);

            // Find current word based on timing (backend provides start_ms, end_ms)
            if (wordTimings.length > 0) {
                const activeWordIndex = wordTimings.findIndex(w =>
                    currentTime >= w.start_ms && currentTime < w.end_ms
                );

                if (activeWordIndex !== -1) {
                    setCurrentWordIndex(activeWordIndex);
                }
            }
        };

        const handleEnded = () => {
            setIsPlaying(false);
            setCurrentWordIndex(-1);
            setProgress(0);
        };

        audio.addEventListener('timeupdate', handleTimeUpdate);
        audio.addEventListener('ended', handleEnded);

        return () => {
            audio.removeEventListener('timeupdate', handleTimeUpdate);
            audio.removeEventListener('ended', handleEnded);
        };
    }, [wordTimings]);

    // Select dyslexia type and continue
    const handleSelectDyslexiaType = (type) => {
        setSettings(s => ({ ...s, dyslexiaType: type }));
        setShowAssessment(false);
    };

    // Toggle Speech Recognition
    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
        } else {
            if (!recognitionRef.current) {
                alert('Speech recognition is not supported in this browser.');
                return;
            }
            recognitionRef.current.start();
            setIsListening(true);
        }
    };

    // File upload handler
    const handleFileUpload = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setLoading(l => ({ ...l, upload: true }));
        try {
            const res = await api.uploadDocument(file);
            if (res.data.success) {
                setText(res.data.text);
                setProcessedText('');

                // Initialize chat session for Q&A
                try {
                    const sessionRes = await api.createChatSession();
                    const newSessionId = sessionRes.data.session_id;
                    setChatSessionId(newSessionId);

                    // Store document context for chat
                    await api.setDocumentContext(res.data.text, newSessionId);
                    setChatHistory([]);
                    setShowChat(true);
                } catch (chatErr) {
                    console.error('Failed to initialize chat:', chatErr);
                }
            } else {
                alert(res.data.error || 'Upload failed');
            }
        } catch (err) {
            alert('Failed to upload file');
        }
        setLoading(l => ({ ...l, upload: false }));
    };

    // Simplify text
    const handleSimplify = async () => {
        const content = text || processedText;
        if (!content) return;

        setLoading(l => ({ ...l, simplify: true }));
        try {
            const res = await api.simplifyText(content, settings.language, settings.dyslexiaType);
            setProcessedText(res.data.simplified_text);
        } catch (err) {
            alert('Failed to simplify text');
        }
        setLoading(l => ({ ...l, simplify: false }));
    };

    // Summarize text
    const handleSummarize = async () => {
        const content = text || processedText;
        if (!content) return;

        setLoading(l => ({ ...l, summarize: true }));
        try {
            const res = await api.summarizeText(content, settings.language, settings.dyslexiaType);
            setProcessedText(res.data.summary);
        } catch (err) {
            alert('Failed to summarize text');
        }
        setLoading(l => ({ ...l, summarize: false }));
    };

    // Generate TTS with highlighting using Backend API
    const handleSpeak = async () => {
        const content = processedText || text;
        if (!content) return;

        // Stop any current speech
        const audio = audioRef.current;
        if (isPlaying) {
            audio.pause();
            setIsPlaying(false);
            return;
        }

        setLoading(l => ({ ...l, tts: true }));

        try {
            // Call backend TTS API
            const res = await api.textToSpeech(content, settings.language, settings.speechSpeed);

            if (res.data.success) {
                // Set audio source
                const url = `https://pad-new-project.onrender.com${res.data.audio_url}`;
                setAudioUrl(url);
                setWordTimings(res.data.word_timings);

                // Play audio
                audio.src = url;
                audio.playbackRate = settings.speechSpeed;

                // Play with user interaction handling
                try {
                    await audio.play();
                    setIsPlaying(true);
                } catch (playErr) {
                    console.error("Playback failed:", playErr);
                    alert("Click play to start audio");
                }
            } else {
                alert(res.data.error || 'TTS generation failed');
            }
        } catch (err) {
            console.error(err);
            alert('Failed to generate speech');
        }
        setLoading(l => ({ ...l, tts: false }));
    };

    // Chat Q&A handler
    const handleAskQuestion = async () => {
        if (!chatQuestion.trim() || !chatSessionId) return;

        setChatLoading(true);
        try {
            const res = await api.askQuestion(chatQuestion, chatSessionId, settings.language, settings.dyslexiaType);

            if (res.data.success) {
                setChatHistory(prev => [
                    ...prev,
                    { question: chatQuestion, answer: res.data.answer }
                ]);
                setChatQuestion('');

                // Scroll to latest message
                setTimeout(() => {
                    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            } else {
                alert(res.data.error || 'Failed to get answer');
            }
        } catch (err) {
            alert('Error asking question');
            console.error(err);
        }
        setChatLoading(false);
    };

    // Toggle play/pause
    const togglePlayPause = () => {
        const audio = audioRef.current;
        if (!audio) return;

        if (isPlaying) {
            audio.pause();
            setIsPlaying(false);
        } else {
            if (audio.src) {
                audio.play();
                setIsPlaying(true);
            } else {
                handleSpeak();
            }
        }
    };

    // Render text with word highlighting
    const renderHighlightedText = () => {
        const content = processedText || text;
        if (!content) return null;

        // Always apply bionic reading if focusMode is enabled
        // Use word timings if available, otherwise just split by space

        // Prepare content class based on language
        const contentClass = `text-display lang-${settings.language}`;

        if (wordTimings.length === 0) {
            if (settings.focusMode) {
                // Split content into words and apply bionicRead
                const words = content.split(/(\s+)/);
                return (
                    <div className={contentClass}>
                        {words.map((word, i) => {
                            if (/^\s+$/.test(word)) {
                                return <span key={i}>{word}</span>;
                            }
                            return <span key={i}>{bionicRead(word)}</span>;
                        })}
                    </div>
                );
            } else {
                return <div className={contentClass}>{content}</div>;
            }
        }

        // Split content into words for highlighting (TTS active)
        // We use the word timings from backend to map regular words

        // If we have precise timings, we can just highlight based on index
        // But we need to render the full text including spaces
        const words = content.split(/(\s+)/);
        let wordCount = 0;

        return (
            <div className={contentClass}>
                {words.map((word, i) => {
                    if (/^\s+$/.test(word)) {
                        return <span key={i}>{word}</span>;
                    }

                    const currentIndex = wordCount++;
                    const isActive = currentIndex === currentWordIndex;

                    return (
                        <span
                            key={i}
                            className={`word ${isActive ? 'active' : ''}`}
                        >
                            {settings.focusMode ? bionicRead(word) : word}
                        </span>
                    );
                })}
            </div>
        );
    };

    // Bionic Reading Helper
    const bionicRead = (word) => {
        if (word.length < 2) return word;
        const boldLength = Math.ceil(word.length / 2);
        return (
            <>
                <strong>{word.substring(0, boldLength)}</strong>
                {word.substring(boldLength)}
            </>
        );
    };

    // Get current dyslexia type info
    const getCurrentTypeInfo = () => {
        const type = dyslexiaTypes.find(t => t.code === settings.dyslexiaType);
        return type || { name: 'General', description: 'General reading support' };
    };

    const displayText = processedText || text;

    // Assessment Screen
    if (showAssessment) {
        return (
            <div className="app">
                <header className="header" style={{
                    background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 50%, rgba(240, 147, 251, 0.08) 100%)',
                    borderBottom: '2px solid rgba(102, 126, 234, 0.2)',
                    backdropFilter: 'blur(10px)',
                    boxShadow: '0 8px 32px rgba(102, 126, 234, 0.1)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', justifyContent: 'center' }}>
                        <img src="/logo.png" alt="DyslexiFlow Logo" className="app-logo" style={{
                            filter: 'drop-shadow(0 8px 16px rgba(102, 126, 234, 0.3))',
                            transition: 'transform 0.3s ease'
                        }} />
                        <div>
                            <h1 style={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
                                backgroundClip: 'text',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                fontSize: '2.2rem',
                                fontWeight: '900',
                                margin: '0',
                                letterSpacing: '0.5px',
                                textShadow: 'none'
                            }}>
                                DyslexiFlow
                            </h1>
                            <p style={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                backgroundClip: 'text',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                fontWeight: '700',
                                letterSpacing: '1px',
                                fontSize: '0.95rem',
                                margin: '4px 0 0 0'
                            }}>
                                Read Without Barriers
                            </p>
                        </div>
                    </div>
                </header>

                <div className="container">
                    <div className="card">
                        <h2 style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            marginBottom: '10px'
                        }}>
                            <span style={{ fontSize: '2.2rem' }}>📋</span>
                            <span style={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
                                backgroundClip: 'text',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                fontSize: '2rem',
                                fontWeight: '800',
                                letterSpacing: '0.5px'
                            }}>
                                Tell Us About Your Reading
                            </span>
                        </h2>
                        <p style={{ marginBottom: '20px', lineHeight: '1.8' }}>
                            Select the type that best matches your experience from your <strong>medical report</strong> or diagnosis.
                            This helps us make text easier for YOU specifically.
                        </p>
                        <p style={{ marginBottom: '25px', color: '#666' }}>
                            Not sure? Select "Not Sure / General" and we'll use settings that work for most people.
                        </p>

                        <div className="dyslexia-options">
                            {dyslexiaTypes.map((type, idx) => {
                                const gradients = [
                                    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                                    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                                    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                                    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                                    'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
                                ];
                                const gradient = gradients[idx % gradients.length];

                                return (
                                    <button
                                        key={type.code}
                                        onClick={() => handleSelectDyslexiaType(type.code)}
                                        style={{
                                            background: gradient,
                                            color: 'white',
                                            border: 'none',
                                            padding: '24px 28px',
                                            borderRadius: '20px',
                                            cursor: 'pointer',
                                            transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                                            boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)',
                                            textAlign: 'left',
                                            display: 'block',
                                            width: '100%',
                                            marginBottom: '14px'
                                        }}
                                        onMouseEnter={e => {
                                            e.target.style.transform = 'translateY(-4px)';
                                            e.target.style.boxShadow = '0 12px 35px rgba(102, 126, 234, 0.5)';
                                        }}
                                        onMouseLeave={e => {
                                            e.target.style.transform = 'translateY(0)';
                                            e.target.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.3)';
                                        }}
                                    >
                                        <strong style={{ fontSize: '1.1rem', display: 'block', marginBottom: '6px' }}>
                                            {type.name}
                                        </strong>
                                        <span style={{ fontSize: '0.9rem', opacity: 0.95 }}>
                                            {type.description}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Main Reader Screen
    return (
        <div className="app">
            {/* Header */}
            <header className="header" style={{
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 50%, rgba(240, 147, 251, 0.08) 100%)',
                borderBottom: '2px solid rgba(102, 126, 234, 0.2)',
                backdropFilter: 'blur(10px)',
                boxShadow: '0 8px 32px rgba(102, 126, 234, 0.1)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', justifyContent: 'center' }}>
                    <img src="/logo.png" alt="DyslexiFlow Logo" className="app-logo" style={{
                        filter: 'drop-shadow(0 8px 16px rgba(102, 126, 234, 0.3))',
                        transition: 'transform 0.3s ease'
                    }} />
                    <div>
                        <h1 style={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            fontSize: '2.2rem',
                            fontWeight: '900',
                            margin: '0',
                            letterSpacing: '0.5px',
                            textShadow: 'none'
                        }}>
                            DyslexiFlow
                        </h1>
                        <p className="tagline" style={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            fontWeight: '700',
                            letterSpacing: '1px',
                            fontSize: '0.95rem',
                            margin: '4px 0 0 0'
                        }}>
                            Read Without Barriers
                        </p>
                    </div>
                </div>
            </header>

            <div className="container">
                {/* Current Profile Badge */}
                <div className="profile-badge">
                    <span>📊 Your Profile: <strong>{getCurrentTypeInfo().name}</strong></span>
                    <button
                        onClick={() => setShowAssessment(true)}
                        style={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
                            color: 'white',
                            border: 'none',
                            padding: '10px 24px',
                            borderRadius: '24px',
                            fontSize: '0.95rem',
                            fontWeight: '700',
                            cursor: 'pointer',
                            transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                            boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                            letterSpacing: '0.5px',
                            textTransform: 'uppercase'
                        }}
                        onMouseEnter={e => {
                            e.target.style.transform = 'translateY(-3px)';
                            e.target.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.6)';
                        }}
                        onMouseLeave={e => {
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
                        }}
                    >
                        🔄 Change Profile
                    </button>
                </div>

                {/* Input Section */}
                <div className="card">
                    <h2>📄 Add Your Text</h2>

                    <div className="tabs">
                        <button
                            className={`tab ${inputMode === 'upload' ? 'active' : ''}`}
                            onClick={() => setInputMode('upload')}
                        >
                            Upload File
                        </button>
                        <button
                            className={`tab ${inputMode === 'type' ? 'active' : ''}`}
                            onClick={() => setInputMode('type')}
                        >
                            Type Text
                        </button>
                    </div>

                    {inputMode === 'upload' ? (
                        <div
                            className="upload-zone"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <div className="upload-icon">📁</div>
                            <p><strong>Click to upload</strong></p>
                            <p>PDF, DOCX, or TXT files</p>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf,.docx,.txt"
                                onChange={handleFileUpload}
                            />
                            {loading.upload && <div className="loading" style={{ marginTop: '15px' }}></div>}
                        </div>
                    ) : (
                        <div className="type-container">
                            <div style={{ position: 'relative', width: '100%' }}>
                                <textarea
                                    className="modern-text-input"
                                    placeholder="Paste or type your text here..."
                                    value={text}
                                    onChange={(e) => {
                                        setText(e.target.value);
                                        setProcessedText('');
                                    }}
                                    style={{
                                        width: '100%',
                                        minHeight: '140px',
                                        padding: '24px',
                                        fontSize: settings.fontSize,
                                        borderRadius: '24px',
                                        border: '2px solid rgba(59,130,246,0.2)',
                                        background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(239,246,255,0.4) 100%)',
                                        boxShadow: '0 8px 32px rgba(59,130,246,0.12)',
                                        outline: 'none',
                                        transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                                        fontFamily: 'inherit',
                                        color: 'var(--text-primary)',
                                        marginBottom: '10px',
                                        resize: 'vertical',
                                        letterSpacing: '0.3px',
                                        lineHeight: '1.7'
                                    }}
                                    onFocus={e => {
                                        e.target.style.borderColor = '#3b82f6';
                                        e.target.style.boxShadow = '0 12px 40px rgba(59,130,246,0.25)';
                                        e.target.style.transform = 'translateY(-2px)';
                                    }}
                                    onBlur={e => {
                                        e.target.style.borderColor = 'rgba(59,130,246,0.2)';
                                        e.target.style.boxShadow = '0 8px 32px rgba(59,130,246,0.12)';
                                        e.target.style.transform = 'translateY(0)';
                                    }}
                                />
                                <img src="/logo.png" alt="Logo" style={{ position: 'absolute', top: 16, right: 16, width: 32, height: 32, opacity: 0.12 }} />
                            </div>
                            <button
                                className={`mic-btn ${isListening ? 'listening' : ''}`}
                                onClick={toggleListening}
                                title={isListening ? 'Stop Listening' : 'Start Voice Input'}
                            >
                                {isListening ? '🛑' : '🎤'}
                                <span>{isListening ? 'Listening...' : 'Dictate'}</span>
                            </button>
                        </div>
                    )}
                </div>

                {/* Chat Q&A Section */}
                {showChat && chatSessionId && (
                    <div className="card">
                        <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <img src="/logo.png" alt="Logo" style={{ width: 32, height: 32, borderRadius: 8 }} />
                            💬 Ask About Document
                        </h2>

                        {/* Chat history */}
                        <div className="chat-history" style={{
                            maxHeight: '300px',
                            overflowY: 'auto',
                            background: 'rgba(59,130,246,0.03)',
                            borderRadius: '16px',
                            padding: '16px',
                            marginBottom: '16px',
                            border: '1px solid rgba(59,130,246,0.1)'
                        }}>
                            {chatHistory.length === 0 ? (
                                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '30px' }}>
                                    Ask questions about the uploaded document...
                                </p>
                            ) : (
                                chatHistory.map((item, idx) => (
                                    <div key={idx} style={{ marginBottom: '20px', animation: 'slideIn 0.4s ease' }}>
                                        <div
                                            className={`lang-${settings.language}`}
                                            style={{
                                                background: 'linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(99,102,241,0.1) 100%)',
                                                padding: '14px 16px',
                                                borderRadius: '16px',
                                                marginBottom: '10px',
                                                fontSize: settings.fontSize,
                                                fontWeight: '600',
                                                border: '1px solid rgba(59,130,246,0.2)',
                                                boxShadow: '0 4px 12px rgba(59,130,246,0.08)',
                                                color: '#1e3a8a'
                                            }}>
                                            ❓ {item.question}
                                        </div>
                                        <div
                                            className={`lang-${settings.language}`}
                                            style={{
                                                background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(239,246,255,0.6) 100%)',
                                                padding: '14px 16px',
                                                borderRadius: '16px',
                                                fontSize: settings.fontSize,
                                                lineHeight: '1.8',
                                                border: '1px solid rgba(59,130,246,0.15)',
                                                boxShadow: '0 4px 12px rgba(59,130,246,0.06)',
                                                color: '#1f2937'
                                            }}>
                                            💡 {item.answer}
                                        </div>
                                    </div>
                                ))
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        {/* Chat input */}
                        <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                            <input
                                type="text"
                                placeholder="Ask a question about the document..."
                                value={chatQuestion}
                                onChange={(e) => setChatQuestion(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                                style={{
                                    flex: 1,
                                    padding: '14px 20px',
                                    borderRadius: '24px',
                                    border: '2px solid rgba(59,130,246,0.2)',
                                    fontSize: settings.fontSize,
                                    fontFamily: 'inherit',
                                    outline: 'none',
                                    transition: 'all 0.3s ease',
                                    background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(239,246,255,0.5) 100%)',
                                    boxShadow: '0 4px 15px rgba(59,130,246,0.1)',
                                    color: '#1f2937',
                                    letterSpacing: '0.3px'
                                }}
                                onFocus={e => {
                                    e.target.style.borderColor = '#3b82f6';
                                    e.target.style.boxShadow = '0 8px 25px rgba(59,130,246,0.2)';
                                }}
                                onBlur={e => {
                                    e.target.style.borderColor = 'rgba(59,130,246,0.2)';
                                    e.target.style.boxShadow = '0 4px 15px rgba(59,130,246,0.1)';
                                }}
                            />
                            <button
                                className="btn btn-primary"
                                onClick={handleAskQuestion}
                                disabled={chatLoading || !chatQuestion.trim()}
                                style={{ minWidth: '120px' }}
                            >
                                {chatLoading ? '⏳' : '🔍'} Ask
                            </button>
                        </div>
                    </div>
                )}

                {/* Action Buttons */}
                {displayText && (
                    <div className="card">
                        <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <img src="/logo.png" alt="Logo" style={{ width: 32, height: 32, borderRadius: 8 }} />
                            ✨ Make It Easier
                        </h2>
                        <div className="btn-group">
                            <button
                                className="btn btn-primary"
                                onClick={handleSimplify}
                                disabled={loading.simplify}
                            >
                                {loading.simplify ? <span className="loading"></span> : '📖'}
                                Simplify Text
                            </button>
                            <button
                                className="btn btn-secondary"
                                onClick={handleSummarize}
                                disabled={loading.summarize}
                            >
                                {loading.summarize ? <span className="loading"></span> : '📋'}
                                Summarize
                            </button>
                            <button
                                className="btn btn-accent"
                                onClick={handleSpeak}
                                disabled={loading.tts}
                            >
                                {loading.tts ? <span className="loading"></span> : '🔊'}
                                Read Aloud
                            </button>
                            <button
                                className={`btn ${settings.focusMode ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setSettings(s => ({ ...s, focusMode: !s.focusMode }))}
                            >
                                {settings.focusMode ? '⚡ON' : '⚡'} Focus Mode
                            </button>
                        </div>
                    </div>
                )}

                {/* Text Display with Highlighting */}
                {displayText && (
                    <div className="card">
                        <h2>📖 Your Text</h2>
                        {renderHighlightedText()}

                        {/* Reading Controls */}
                        {isPlaying && (
                            <div className="audio-controls">
                                <button
                                    className="btn btn-primary play-btn"
                                    onClick={togglePlayPause}
                                >
                                    {window.speechSynthesis.paused ? '▶️' : '⏸️'}
                                </button>
                                <div className="progress-bar">
                                    <div
                                        className="progress-fill"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => window.speechSynthesis.cancel()}
                                    style={{ padding: '10px', minWidth: 'auto', borderRadius: '50%' }}
                                >
                                    🛑
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Settings Panel */}
                <div className="card">
                    <h2>⚙️ Settings</h2>
                    <div className="settings-panel">
                        {/* Font Size */}
                        <div className="setting-item">
                            <label>Text Size: {settings.fontSize}px</label>
                            <input
                                type="range"
                                min="14"
                                max="32"
                                value={settings.fontSize}
                                onChange={(e) => setSettings(s => ({ ...s, fontSize: parseInt(e.target.value) }))}
                            />
                        </div>

                        {/* Background Color */}
                        <div className="setting-item">
                            <label>Background Color</label>
                            <div className="color-options">
                                {[
                                    { color: '#FDF6E3', className: 'color-cream' },
                                    { color: '#E8F4FC', className: 'color-blue' },
                                    { color: '#E8F5E9', className: 'color-green' },
                                    { color: '#FFFDE7', className: 'color-yellow' }
                                ].map(({ color, className }) => (
                                    <button
                                        key={color}
                                        className={`color-btn ${className} ${settings.bgColor === color ? 'active' : ''}`}
                                        onClick={() => setSettings(s => ({ ...s, bgColor: color }))}
                                        aria-label={`Set background to ${className.replace('color-', '')}`}
                                    />
                                ))}
                            </div>
                        </div>

                        {/* Speech Speed */}
                        <div className="setting-item">
                            <label>Speech Speed: {settings.speechSpeed}x</label>
                            <input
                                type="range"
                                min="0.5"
                                max="1.5"
                                step="0.1"
                                value={settings.speechSpeed}
                                onChange={(e) => setSettings(s => ({ ...s, speechSpeed: parseFloat(e.target.value) }))}
                            />
                        </div>

                        {/* Language */}
                        <div className="setting-item">
                            <label>Language</label>
                            <select
                                value={settings.language}
                                onChange={(e) => setSettings(s => ({ ...s, language: e.target.value }))}
                            >
                                {languages.map(lang => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <footer className="footer">
                    <div className="footer-content">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <img src="/logo.png" alt="DyslexiFlow" style={{ width: '28px', height: '28px', borderRadius: '4px' }} />
                            <span style={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
                                backgroundClip: 'text',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                fontSize: '1.3rem',
                                fontWeight: '800',
                                letterSpacing: '0.5px',
                                textShadow: 'none'
                            }}>
                                DyslexiFlow
                            </span>
                        </div>
                        <p>Made with ❤️ for everyone who reads differently</p>
                        <span className="footer-copyright">© 2026 DyslexiFlow - Read Without Barriers</span>
                    </div>
                </footer>
            </div>
            {/* Hidden Audio Element for Backend TTS */}
            <audio ref={audioRef} style={{ display: 'none' }} />
        </div>
    );
}

export default App;
