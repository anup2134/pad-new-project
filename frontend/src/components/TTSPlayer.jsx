import React, { useState } from 'react';
import useTTSHighlight from '../hooks/useTTSHighlight';
import './TTSPlayer.css';

/**
 * Text-to-Speech Player Component with Word Highlighting
 * Features:
 * - Multi-language support
 * - Word-level highlighting during playback
 * - Speed control
 * - Dyslexia-friendly interface
 */
const TTSPlayer = ({ text, language = 'en', speed = 1.0 }) => {
  const tts = useTTSHighlight();
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [selectedSpeed, setSelectedSpeed] = useState(speed);
  const [showTranscript, setShowTranscript] = useState(true);

  const handleGenerateSpeech = async () => {
    await tts.generateSpeech(text, selectedLanguage, selectedSpeed);
  };

  const handleLanguageChange = (e) => {
    setSelectedLanguage(e.target.value);
  };

  const handleSpeedChange = (e) => {
    const newSpeed = parseFloat(e.target.value);
    setSelectedSpeed(newSpeed);
    tts.setPlaybackRate(newSpeed);
  };

  const getSpeedLabel = (speed) => {
    if (speed === 1.0) return 'Normal';
    if (speed === 1.5) return 'Slow';
    if (speed === 0.75) return 'Fast';
    return `${(speed * 100).toFixed(0)}%`;
  };

  return (
    <div className="tts-player">
      {/* Header */}
      <div className="tts-header">
        <h3>Text to Speech</h3>
      </div>

      {/* Controls */}
      <div className="tts-controls">
        {/* Language Select */}
        <div className="control-group">
          <label htmlFor="language">Language:</label>
          <select
            id="language"
            value={selectedLanguage}
            onChange={handleLanguageChange}
            disabled={tts.isLoading}
          >
            <option value="en">English (US)</option>
            <option value="en-GB">English (British)</option>
            <option value="es">Spanish</option>
            <option value="es-MX">Spanish (Mexico)</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
            <option value="pt">Portuguese (Brazil)</option>
            <option value="pt-PT">Portuguese (Portugal)</option>
            <option value="hi">Hindi</option>
            <option value="ar">Arabic</option>
            <option value="zh">Chinese (Simplified)</option>
            <option value="zh-TW">Chinese (Traditional)</option>
            <option value="ja">Japanese</option>
            <option value="ko">Korean</option>
            <option value="ru">Russian</option>
          </select>
        </div>

        {/* Speed Control */}
        <div className="control-group">
          <label htmlFor="speed">Speed: {getSpeedLabel(selectedSpeed)}</label>
          <input
            id="speed"
            type="range"
            min="0.5"
            max="2.0"
            step="0.25"
            value={selectedSpeed}
            onChange={handleSpeedChange}
            disabled={tts.isLoading}
          />
        </div>
      </div>

      {/* Playback Buttons */}
      <div className="tts-buttons">
        <button
          onClick={handleGenerateSpeech}
          disabled={tts.isLoading}
          className="btn-generate"
        >
          {tts.isLoading ? 'Generating...' : 'Generate Speech'}
        </button>

        {tts.wordTimings.length > 0 && (
          <>
            <button
              onClick={tts.play}
              disabled={!tts.wordTimings.length}
              className="btn-play"
            >
              ▶ Play
            </button>
            <button
              onClick={tts.pause}
              disabled={!tts.isPlaying}
              className="btn-pause"
            >
              ⏸ Pause
            </button>
            <button
              onClick={tts.stop}
              disabled={!tts.wordTimings.length}
              className="btn-stop"
            >
              ⏹ Stop
            </button>
          </>
        )}
      </div>

      {/* Error Message */}
      {tts.error && (
        <div className="tts-error">
          <p>Error: {tts.error}</p>
        </div>
      )}

      {/* Word Highlighting Transcript */}
      {tts.wordTimings.length > 0 && showTranscript && (
        <div className="tts-transcript">
          <div className="words-container">
            {tts.getWordsWithStatus().map((wordObj) => (
              <span
                key={wordObj.index}
                className={`word ${wordObj.isHighlighted ? 'highlighted' : ''}`}
              >
                {wordObj.word}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Playback Progress */}
      {tts.wordTimings.length > 0 && (
        <div className="tts-progress">
          <div className="progress-info">
            <span>
              {Math.floor(tts.getCurrentTime())}s / {Math.floor(tts.getDuration())}s
            </span>
            <span>Word {tts.currentWordIndex + 1} / {tts.wordTimings.length}</span>
          </div>
          <input
            type="range"
            min="0"
            max={tts.getDuration() || 0}
            value={tts.getCurrentTime()}
            onChange={(e) => tts.setCurrentTime(parseFloat(e.target.value))}
            className="progress-bar"
          />
        </div>
      )}

      {/* Toggle Transcript */}
      {tts.wordTimings.length > 0 && (
        <div className="tts-options">
          <label>
            <input
              type="checkbox"
              checked={showTranscript}
              onChange={(e) => setShowTranscript(e.target.checked)}
            />
            Show Word Highlighting
          </label>
        </div>
      )}
    </div>
  );
};

export default TTSPlayer;
