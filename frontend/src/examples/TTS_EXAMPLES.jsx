/**
 * Example: How to Use TTS with Word Highlighting
 * Complete working examples for different use cases
 */

// ============================================
// EXAMPLE 1: Simple TTS Player Component
// ============================================

import React from 'react';
import TTSPlayer from './components/TTSPlayer';

function DocumentViewer() {
  const documentText = `
    Dyslexia is a learning difference that affects how the brain processes written language.
    It is not related to intelligence or effort, but rather to how the brain is wired.
    People with dyslexia may have difficulty with reading, spelling, and writing.
    However, with proper support and strategies, they can succeed in school and beyond.
  `;

  return (
    <div className="document-viewer">
      <h1>Document Viewer with TTS</h1>
      
      <TTSPlayer 
        text={documentText}
        language="en"
        speed={1.0}
      />
      
      <div className="document-content">
        {documentText}
      </div>
    </div>
  );
}

export default DocumentViewer;

// ============================================
// EXAMPLE 2: Custom Hook Implementation
// ============================================

import React from 'react';
import useTTSHighlight from './hooks/useTTSHighlight';

function CustomTTSComponent({ text }) {
  const tts = useTTSHighlight();
  const [language, setLanguage] = React.useState('en');
  const [speed, setSpeed] = React.useState(1.0);

  const handleGenerateAndPlay = async () => {
    const result = await tts.generateSpeech(text, language, speed);
    if (result) {
      tts.play();
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      {/* Controls */}
      <div style={{ marginBottom: '20px' }}>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
        </select>

        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.25"
          value={speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
        />
        <span>{speed}x</span>
      </div>

      {/* Buttons */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={handleGenerateAndPlay}>
          Generate & Play
        </button>
        <button onClick={tts.pause} disabled={!tts.isPlaying}>
          Pause
        </button>
        <button onClick={tts.stop}>
          Stop
        </button>
      </div>

      {/* Display error if any */}
      {tts.error && <p style={{ color: 'red' }}>{tts.error}</p>}

      {/* Show highlighted words */}
      {tts.wordTimings.length > 0 && (
        <div style={{
          padding: '15px',
          backgroundColor: '#f5f5f5',
          borderRadius: '5px',
          marginTop: '20px'
        }}>
          {tts.getWordsWithStatus().map((wordObj) => (
            <span
              key={wordObj.index}
              style={{
                padding: '5px 8px',
                margin: '3px',
                borderRadius: '3px',
                backgroundColor: wordObj.isHighlighted ? '#ffd700' : '#e0e0e0',
                fontWeight: wordObj.isHighlighted ? 'bold' : 'normal',
                fontSize: wordObj.isHighlighted ? '18px' : '16px',
                transition: 'all 0.2s'
              }}
            >
              {wordObj.word}
            </span>
          ))}
        </div>
      )}

      {/* Progress info */}
      {tts.wordTimings.length > 0 && (
        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <p>
            Playing word {tts.currentWordIndex + 1} / {tts.wordTimings.length}
          </p>
          <p>
            Time: {Math.floor(tts.getCurrentTime())}s / {Math.floor(tts.getDuration())}s
          </p>
        </div>
      )}
    </div>
  );
}

export default CustomTTSComponent;

// ============================================
// EXAMPLE 3: Inline Highlighting with React
// ============================================

import React, { useState } from 'react';
import useTTSHighlight from './hooks/useTTSHighlight';

function InlineHighlightedText({ text }) {
  const tts = useTTSHighlight();

  React.useEffect(() => {
    const generateOnLoad = async () => {
      await tts.generateSpeech(text, 'en', 1.0);
    };
    generateOnLoad();
  }, [text]);

  return (
    <div>
      {/* Main content with inline highlighting */}
      <p style={{ lineHeight: 1.8, fontSize: 18 }}>
        {tts.getWordsWithStatus().map((wordObj, idx) => (
          <span
            key={idx}
            style={{
              backgroundColor: wordObj.isHighlighted ? '#ffff00' : 'transparent',
              padding: '2px 4px',
              borderRadius: '2px',
              transition: 'background-color 0.15s'
            }}
          >
            {wordObj.word}{' '}
          </span>
        ))}
      </p>

      {/* Controls */}
      <div style={{ marginTop: 20 }}>
        <button onClick={tts.play}>Play</button>
        <button onClick={tts.pause}>Pause</button>
        <button onClick={tts.stop}>Stop</button>
      </div>
    </div>
  );
}

export default InlineHighlightedText;

// ============================================
// EXAMPLE 4: Direct API Call (No React)
// ============================================

async function generateTTS() {
  const text = "Hello, welcome to the accessibility platform!";
  
  const response = await fetch('http://localhost:8000/api/speech/tts-with-highlight', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: text,
      language: 'en',
      speed: 1.0
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Audio URL:', data.audio_url);
    console.log('Word timings:', data.word_timings);
    
    // Play the audio
    const audio = new Audio(data.audio_url);
    audio.play();

    // Track and highlight words
    audio.addEventListener('timeupdate', () => {
      const currentTimeMs = audio.currentTime * 1000;
      
      for (let word of data.word_timings) {
        if (currentTimeMs >= word.start_ms && currentTimeMs < word.end_ms) {
          // Highlight this word in your UI
          console.log('Currently speaking:', word.word);
          break;
        }
      }
    });
  } else {
    console.error('Error:', data.error);
  }
}

// ============================================
// EXAMPLE 5: Multi-Language Support
// ============================================

const languages = {
  'en': 'English',
  'es': 'Spanish',
  'fr': 'French',
  'de': 'German',
  'ja': 'Japanese'
};

async function playInLanguage(text, languageCode) {
  try {
    const response = await fetch('http://localhost:8000/api/speech/tts-with-highlight', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        language: languageCode,
        speed: 1.0
      })
    });

    const data = await response.json();
    
    if (data.success) {
      const audio = new Audio(data.audio_url);
      audio.play();
      
      return {
        audio,
        wordTimings: data.word_timings,
        language: languages[languageCode]
      };
    }
  } catch (error) {
    console.error('TTS Error:', error);
  }
}

// Usage:
// await playInLanguage("Hola, ¿cómo estás?", "es");

// ============================================
// EXAMPLE 6: Word Duration Analysis
// ============================================

function analyzeWordTiming(wordTimings) {
  return wordTimings.map((word, idx) => ({
    word: word.word,
    duration: word.duration_ms,
    startTime: word.start_ms,
    position: idx,
    avgDuration: Math.round(
      wordTimings.reduce((sum, w) => sum + w.duration_ms, 0) / wordTimings.length
    ),
    isFasterThanAverage: word.duration_ms < (
      wordTimings.reduce((sum, w) => sum + w.duration_ms, 0) / wordTimings.length
    )
  }));
}

// Usage:
// const analysis = analyzeWordTiming(wordTimings);
// console.log(analysis);

// ============================================
// EXAMPLE 7: Speed-Adjusted Timing
// ============================================

async function playWithSpeedControl(text, speed) {
  const response = await fetch('http://localhost:8000/api/speech/tts-with-highlight', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      language: 'en',
      speed: speed  // 0.5 to 2.0
    })
  });

  const data = await response.json();
  
  if (data.success) {
    console.log(`Playing at ${speed}x speed`);
    console.log(`Total duration: ${data.word_timings[data.word_timings.length - 1].end_ms}ms`);
    
    const audio = new Audio(data.audio_url);
    audio.play();
    
    return audio;
  }
}

// Usage:
// await playWithSpeedControl("Hello world", 1.5);  // 1.5x faster

// ============================================
// EXAMPLE 8: Complete App Component
// ============================================

function DyslexiaFriendlyReader() {
  const [selectedText, setSelectedText] = React.useState('');
  const [language, setLanguage] = React.useState('en');
  const tts = useTTSHighlight();

  const generateAndPlay = async () => {
    await tts.generateSpeech(selectedText, language, 1.0);
    tts.play();
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 20 }}>
      <h1>Dyslexia-Friendly Text Reader</h1>
      
      {/* Text Input */}
      <textarea
        value={selectedText}
        onChange={(e) => setSelectedText(e.target.value)}
        placeholder="Paste your text here..."
        style={{
          width: '100%',
          height: 200,
          fontSize: 18,
          padding: 10,
          marginBottom: 20
        }}
      />

      {/* Language Select */}
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        style={{ fontSize: 16, padding: 10, marginRight: 10 }}
      >
        <option value="en">English</option>
        <option value="es">Spanish</option>
        <option value="fr">French</option>
        <option value="de">German</option>
      </select>

      {/* Controls */}
      <button
        onClick={generateAndPlay}
        disabled={!selectedText || tts.isLoading}
        style={{
          padding: '10px 20px',
          fontSize: 16,
          cursor: 'pointer'
        }}
      >
        {tts.isLoading ? 'Generating...' : 'Read Aloud'}
      </button>

      {/* Display highlighted text */}
      {tts.wordTimings.length > 0 && (
        <div style={{
          marginTop: 30,
          padding: 20,
          backgroundColor: '#f0f0f0',
          borderRadius: 8
        }}>
          <p style={{ fontSize: 18, lineHeight: 2 }}>
            {tts.getWordsWithStatus().map((word, idx) => (
              <span
                key={idx}
                style={{
                  backgroundColor: word.isHighlighted ? '#ffff00' : 'transparent',
                  padding: '2px 4px',
                  fontWeight: word.isHighlighted ? 'bold' : 'normal'
                }}
              >
                {word.word}{' '}
              </span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
}

export default DyslexiaFriendlyReader;

// ============================================
// Export all examples
// ============================================

export {
  DocumentViewer,
  CustomTTSComponent,
  InlineHighlightedText,
  generateTTS,
  playInLanguage,
  analyzeWordTiming,
  playWithSpeedControl,
  DyslexiaFriendlyReader
};
