import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { playlistService } from '../../services/playlistService';
import { trackService } from '../../services/trackService';
import { PlaylistTracks } from '../../components/playlists/PlaylistTracks';
import { PlaylistForm } from '../../components/playlists/PlaylistForm';
import { TrackCard } from '../../components/tracks/TrackCard';
import { PencilIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export const PlaylistPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddTracksModalOpen, setIsAddTracksModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: playlist, isLoading: isPlaylistLoading } = useQuery({
    queryKey: ['playlist', Number(id)],
    queryFn: () => playlistService.getPlaylist(Number(id)),
    enabled: !!id,
  });

  const { data: availableTracks, isLoading: isTracksLoading } = useQuery({
    queryKey: ['tracks'],
    queryFn: trackService.getTracks,
  });

  const addTrackMutation = useMutation({
    mutationFn: (trackId: number) =>
      playlistService.addTrackToPlaylist(Number(id), trackId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist', Number(id)] });
      toast.success('Трек добавлен в плейлист');
    },
    onError: () => {
      toast.error('Ошибка при добавлении трека');
    },
  });

  if (isPlaylistLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (!playlist) {
    return (
      <div className="rounded-lg bg-red-50 p-4 dark:bg-red-900">
        <p className="text-sm text-red-600 dark:text-red-200">
          Плейлист не найден
        </p>
      </div>
    );
  }

  const nonPlaylistTracks = availableTracks?.filter(
    (track) => !playlist.tracks.find((t) => t.id === track.id)
  );

  return (
    <div>
      <button
        onClick={() => navigate('/playlists')}
        className="mb-6 inline-flex items-center text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
      >
        <ArrowLeftIcon className="mr-1 h-4 w-4" />
        Назад к плейлистам
      </button>

      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            {playlist.title}
          </h1>
          {playlist.description && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {playlist.description}
            </p>
          )}
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setIsAddTracksModalOpen(true)}
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:hover:bg-primary-500"
          >
            Добавить треки
          </button>
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="inline-flex items-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          >
            <PencilIcon className="mr-2 h-4 w-4" />
            Редактировать
          </button>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h2 className="mb-4 text-lg font-medium text-gray-900 dark:text-white">
            Треки в плейлисте
          </h2>
          {playlist.tracks.length > 0 ? (
            <PlaylistTracks playlistId={playlist.id} tracks={playlist.tracks} />
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              В плейлисте пока нет треков
            </p>
          )}
        </div>
      </div>

      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Редактирование плейлиста
              </h3>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                ×
              </button>
            </div>
            <PlaylistForm
              playlist={playlist}
              onSuccess={() => setIsEditModalOpen(false)}
              onCancel={() => setIsEditModalOpen(false)}
            />
          </div>
        </div>
      )}

      {isAddTracksModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-4xl rounded-lg bg-white p-6 dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Добавить треки
              </h3>
              <button
                onClick={() => setIsAddTracksModalOpen(false)}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                ×
              </button>
            </div>
            {isTracksLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
              </div>
            ) : nonPlaylistTracks?.length ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {nonPlaylistTracks.map((track) => (
                  <TrackCard
                    key={track.id}
                    track={track}
                    onClick={() => {
                      addTrackMutation.mutate(track.id);
                    }}
                  />
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Нет доступных треков для добавления
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}; 