import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { toast } from '@/components/common/Toast';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { Alert } from '@/components/common/Alert';
import {
  PlusIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface Track {
  id: string;
  title: string;
  artist: string;
  duration: number;
}

interface PlaylistTrack extends Track {
  position: number;
}

interface PlaylistTrackListProps {
  playlistId: string;
}

export function PlaylistTrackList({ playlistId }: PlaylistTrackListProps) {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: tracks, isLoading, error } = useQuery<PlaylistTrack[]>({
    queryKey: ['playlist-tracks', playlistId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('playlist_tracks')
        .select('*, track:tracks(*)')
        .eq('playlist_id', playlistId)
        .order('position');

      if (error) throw error;

      return data.map((item) => ({
        id: item.track.id,
        title: item.track.title,
        artist: item.track.artist,
        duration: item.track.duration,
        position: item.position,
      }));
    },
  });

  const { data: availableTracks } = useQuery<Track[]>({
    queryKey: ['available-tracks', playlistId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('tracks')
        .select('*')
        .not(
          'id',
          'in',
          `(${tracks?.map((t) => t.id).join(',') || 'null'})`
        );

      if (error) throw error;
      return data;
    },
    enabled: isAddModalOpen, // Загружаем только когда модальное окно открыто
  });

  const { mutate: addTrack } = useMutation({
    mutationFn: async (trackId: string) => {
      const position = tracks?.length ? Math.max(...tracks.map(t => t.position)) + 1 : 1;
      const { error } = await supabase
        .from('playlist_tracks')
        .insert({
          playlist_id: playlistId,
          track_id: trackId,
          position,
        });

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist-tracks', playlistId] });
      toast.success('Трек добавлен в плейлист');
      setIsAddModalOpen(false);
    },
    onError: (error) => {
      console.error('Add track error:', error);
      toast.error('Ошибка при добавлении трека');
    },
  });

  const { mutate: removeTrack } = useMutation({
    mutationFn: async (trackId: string) => {
      const { error } = await supabase
        .from('playlist_tracks')
        .delete()
        .eq('playlist_id', playlistId)
        .eq('track_id', trackId);

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist-tracks', playlistId] });
      toast.success('Трек удален из плейлиста');
    },
    onError: (error) => {
      console.error('Remove track error:', error);
      toast.error('Ошибка при удалении трека');
    },
  });

  const { mutate: moveTrack } = useMutation({
    mutationFn: async ({
      trackId,
      direction,
    }: {
      trackId: string;
      direction: 'up' | 'down';
    }) => {
      const currentTrack = tracks?.find((t) => t.id === trackId);
      if (!currentTrack || !tracks) return;

      const newPosition =
        direction === 'up'
          ? currentTrack.position - 1
          : currentTrack.position + 1;

      const otherTrack = tracks.find((t) => t.position === newPosition);
      if (!otherTrack) return;

      // Обновляем позиции обоих треков
      const { error: error1 } = await supabase
        .from('playlist_tracks')
        .update({ position: newPosition })
        .eq('playlist_id', playlistId)
        .eq('track_id', trackId);

      if (error1) throw error1;

      const { error: error2 } = await supabase
        .from('playlist_tracks')
        .update({ position: currentTrack.position })
        .eq('playlist_id', playlistId)
        .eq('track_id', otherTrack.id);

      if (error2) throw error2;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist-tracks', playlistId] });
    },
    onError: (error) => {
      console.error('Move track error:', error);
      toast.error('Ошибка при перемещении трека');
    },
  });

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <Alert variant="error" title="Ошибка">
        Не удалось загрузить треки плейлиста
      </Alert>
    );
  }

  return (
    <>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold">Треки</h2>
          <Button onClick={() => setIsAddModalOpen(true)}>
            <PlusIcon className="h-5 w-5 mr-2" />
            Добавить трек
          </Button>
        </div>

        {!tracks?.length ? (
          <Alert variant="info" title="Нет треков">
            В этом плейлисте пока нет треков
          </Alert>
        ) : (
          <div className="space-y-2">
            {tracks.map((track) => (
              <div
                key={track.id}
                className="flex items-center justify-between bg-white rounded-lg shadow p-4"
              >
                <div className="flex-1">
                  <h3 className="font-medium">{track.title}</h3>
                  {track.artist && (
                    <p className="text-sm text-gray-500">{track.artist}</p>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500 mr-4">
                    {formatDuration(track.duration)}
                  </span>

                  <div className="flex items-center space-x-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() =>
                        moveTrack({ trackId: track.id, direction: 'up' })
                      }
                      disabled={track.position === 1}
                    >
                      <ArrowUpIcon className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() =>
                        moveTrack({ trackId: track.id, direction: 'down' })
                      }
                      disabled={track.position === tracks.length}
                    >
                      <ArrowDownIcon className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeTrack(track.id)}
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Добавить трек"
      >
        <div className="space-y-4">
          {!availableTracks?.length ? (
            <Alert variant="info" title="Нет доступных треков">
              Все треки уже добавлены в плейлист
            </Alert>
          ) : (
            <div className="space-y-2">
              {availableTracks.map((track) => (
                <div
                  key={track.id}
                  className="flex items-center justify-between bg-white rounded-lg p-3 hover:bg-gray-50"
                >
                  <div>
                    <h3 className="font-medium">{track.title}</h3>
                    {track.artist && (
                      <p className="text-sm text-gray-500">{track.artist}</p>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => addTrack(track.id)}
                  >
                    <PlusIcon className="h-4 w-4 mr-1" />
                    Добавить
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </Modal>
    </>
  );
} 