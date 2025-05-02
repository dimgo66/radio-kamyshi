import { useState, useEffect } from 'react';
import { PlayIcon, PauseIcon, SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/react/24/solid';
import { Button } from './Button';
import { icecast } from '@/lib/icecast';

interface PlayerStats {
  listeners: number;
  streamTitle: string;
  streamArtist: string;
}

export function Player() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const [stats, setStats] = useState<PlayerStats>({
    listeners: 0,
    streamTitle: '',
    streamArtist: '',
  });

  useEffect(() => {
    const fetchStats = async () => {
      const newStats = await icecast.getStats();
      setStats(newStats);
    };

    // Обновляем статистику каждые 30 секунд
    fetchStats();
    const interval = setInterval(fetchStats, 30000);

    return () => {
      clearInterval(interval);
      icecast.cleanup();
    };
  }, []);

  const handlePlayPause = () => {
    if (isPlaying) {
      icecast.pause();
    } else {
      icecast.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleMute = () => {
    if (isMuted) {
      icecast.setVolume(volume);
    } else {
      icecast.setVolume(0);
    }
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    icecast.setVolume(newVolume);
    if (newVolume > 0) {
      setIsMuted(false);
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={handlePlayPause}
            aria-label={isPlaying ? 'Пауза' : 'Воспроизвести'}
          >
            {isPlaying ? (
              <PauseIcon className="h-6 w-6" />
            ) : (
              <PlayIcon className="h-6 w-6" />
            )}
          </Button>

          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleMute}
              aria-label={isMuted ? 'Включить звук' : 'Выключить звук'}
            >
              {isMuted ? (
                <SpeakerXMarkIcon className="h-6 w-6" />
              ) : (
                <SpeakerWaveIcon className="h-6 w-6" />
              )}
            </Button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={handleVolumeChange}
              className="w-24"
            />
          </div>
        </div>

        <div className="flex flex-col items-end">
          <div className="text-sm font-medium">
            {stats.streamTitle || 'Радио Камыши'}
          </div>
          {stats.streamArtist && (
            <div className="text-sm text-gray-500">{stats.streamArtist}</div>
          )}
          <div className="text-xs text-gray-400">
            Слушателей: {stats.listeners}
          </div>
        </div>
      </div>
    </div>
  );
} 