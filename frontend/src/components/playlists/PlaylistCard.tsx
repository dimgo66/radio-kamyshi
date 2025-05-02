import { Link } from 'react-router-dom';
import { Playlist } from '../../services/playlistService';
import {
  MusicalNoteIcon,
  ClockIcon,
  TrashIcon,
  PencilIcon,
} from '@heroicons/react/24/outline';

interface PlaylistCardProps {
  playlist: Playlist;
  onDelete?: (id: number) => void;
  onEdit?: (playlist: Playlist) => void;
}

export const PlaylistCard = ({ playlist, onDelete, onEdit }: PlaylistCardProps) => {
  const formatDuration = (tracks: Playlist['tracks']): string => {
    const totalSeconds = tracks.reduce((acc, track) => acc + track.duration, 0);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    return hours > 0
      ? `${hours} ч ${minutes} мин`
      : `${minutes} мин`;
  };

  return (
    <div className="group relative overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <Link to={`/playlists/${playlist.id}`} className="block p-6">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              {playlist.title}
            </h3>
            {playlist.description && (
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {playlist.description}
              </p>
            )}
          </div>
        </div>

        <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex items-center">
            <MusicalNoteIcon className="mr-1.5 h-4 w-4" />
            {playlist.tracks.length} треков
          </div>
          <div className="flex items-center">
            <ClockIcon className="mr-1.5 h-4 w-4" />
            {formatDuration(playlist.tracks)}
          </div>
        </div>
      </Link>

      <div className="absolute right-4 top-4 flex space-x-2 opacity-0 transition-opacity group-hover:opacity-100">
        {onEdit && (
          <button
            onClick={(e) => {
              e.preventDefault();
              onEdit(playlist);
            }}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            <PencilIcon className="h-5 w-5" />
          </button>
        )}
        {onDelete && (
          <button
            onClick={(e) => {
              e.preventDefault();
              onDelete(playlist.id);
            }}
            className="rounded p-1 text-gray-400 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-900 dark:hover:text-red-400"
          >
            <TrashIcon className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
}; 