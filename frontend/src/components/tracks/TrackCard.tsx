import React from 'react';
import { Track } from '../../types';
import { formatDuration } from '../../utils';
import { WaveformDisplay } from './WaveformDisplay';

interface TrackCardProps {
  track: Track;
  onPlay?: (track: Track) => void;
  onEdit?: (track: Track) => void;
  onDelete?: (track: Track) => void;
}

export const TrackCard: React.FC<TrackCardProps> = ({
  track,
  onPlay,
  onEdit,
  onDelete
}) => {
  const handlePlay = (e: React.MouseEvent) => {
    e.stopPropagation();
    onPlay?.(track);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(track);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(track);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{track.title}</h3>
          {track.artist && (
            <p className="text-sm text-gray-600">{track.artist}</p>
          )}
          <div className="mt-2 flex items-center text-sm text-gray-500 space-x-4">
            <span>{formatDuration(track.duration)}</span>
            <span>{Math.round(track.bitrate)}kbps</span>
            <span className="uppercase">{track.format}</span>
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handlePlay}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-full"
            title="Воспроизвести"
          >
            ▶️
          </button>
          {onEdit && (
            <button
              onClick={handleEdit}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-full"
              title="Редактировать"
            >
              ✏️
            </button>
          )}
          {onDelete && (
            <button
              onClick={handleDelete}
              className="p-2 text-red-600 hover:bg-red-50 rounded-full"
              title="Удалить"
            >
              🗑️
            </button>
          )}
        </div>
      </div>
      {track.album && (
        <div className="mt-2 text-sm text-gray-500">
          Альбом: {track.album}
          {track.year && ` (${track.year})`}
        </div>
      )}
      {track.genre && (
        <div className="mt-1 text-sm text-gray-500">
          Жанр: {track.genre}
        </div>
      )}
      {track.waveform_data && (
        <div className="mt-3">
          <WaveformDisplay waveformData={JSON.stringify(track.waveform_data)} />
        </div>
      )}
    </div>
  );
}; 