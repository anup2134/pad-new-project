/**
 * Hook for TTS playback with word-level highlighting
 * Syncs audio playback with visual word highlighting
 */

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

export const useTTSHighlight = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentWordIndex, setCurrentWordIndex] = useState(-1);
  const [wordTimings, setWordTimings] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const audioRef = useRef(null);
  const animationFrameRef = useRef(null);

  /**
   * Generate speech with word timing data
   */
  const generateSpeech = async (text, language = 'en', speed = 1.0) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        'http://localhost:8000/api/speech/tts-with-highlight',
        {
          text,
          language,
          speed
        }
      );

      if (response.data.success) {
        setWordTimings(response.data.word_timings);
        
        // Create audio element
        const audio = new Audio(response.data.audio_url);
        audioRef.current = audio;

        // Setup audio event listeners
        audio.addEventListener('play', () => setIsPlaying(true));
        audio.addEventListener('pause', () => {
          setIsPlaying(false);
          setCurrentWordIndex(-1);
        });
        audio.addEventListener('ended', () => {
          setIsPlaying(false);
          setCurrentWordIndex(-1);
        });

        return response.data;
      } else {
        setError(response.data.error || 'Failed to generate speech');
        return null;
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      setError(errorMsg);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Play the generated speech
   */
  const play = () => {
    if (audioRef.current) {
      audioRef.current.play();
      startHighlighting();
    }
  };

  /**
   * Pause the speech
   */
  const pause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
  };

  /**
   * Stop the speech and reset highlighting
   */
  const stop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setCurrentWordIndex(-1);
    setIsPlaying(false);
  };

  /**
   * Start tracking current word based on audio playback position
   */
  const startHighlighting = () => {
    const updateHighlight = () => {
      if (!audioRef.current || !isPlaying) {
        return;
      }

      const currentTimeMs = audioRef.current.currentTime * 1000;

      // Find current word index
      for (let i = 0; i < wordTimings.length; i++) {
        const word = wordTimings[i];
        if (
          currentTimeMs >= word.start_ms &&
          currentTimeMs < word.end_ms
        ) {
          setCurrentWordIndex(i);
          break;
        }
      }

      animationFrameRef.current = requestAnimationFrame(updateHighlight);
    };

    updateHighlight();
  };

  /**
   * Stop highlighting animation
   */
  useEffect(() => {
    if (!isPlaying) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  }, [isPlaying]);

  /**
   * Get highlighted text with HTML markup
   */
  const getHighlightedHTML = () => {
    return wordTimings
      .map((word, index) => {
        const isHighlighted = index === currentWordIndex;
        const className = isHighlighted
          ? 'word highlighted'
          : 'word';
        
        return `<span class="${className}" data-index="${index}">${word.word}</span>`;
      })
      .join(' ');
  };

  /**
   * Get array of word objects with highlighting status
   */
  const getWordsWithStatus = () => {
    return wordTimings.map((word, index) => ({
      ...word,
      isHighlighted: index === currentWordIndex,
      index
    }));
  };

  return {
    // State
    isPlaying,
    isLoading,
    error,
    currentWordIndex,
    wordTimings,
    audioRef,

    // Methods
    generateSpeech,
    play,
    pause,
    stop,
    getHighlightedHTML,
    getWordsWithStatus,

    // Audio control
    setPlaybackRate: (rate) => {
      if (audioRef.current) {
        audioRef.current.playbackRate = rate;
      }
    },
    getCurrentTime: () => audioRef.current?.currentTime || 0,
    setCurrentTime: (time) => {
      if (audioRef.current) {
        audioRef.current.currentTime = time;
      }
    },
    getDuration: () => audioRef.current?.duration || 0
  };
};

export default useTTSHighlight;
