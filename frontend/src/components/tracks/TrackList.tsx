import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Track, trackService } from '../../services/trackService';
import { TrackCard } from './TrackCard';
import { TrackUpload } from './TrackUpload';
import toast from 'react-hot-toast';

export const TrackList = () => {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [editingTrack, setEditingTrack] = useState<Track | null>(null);
  const queryClient = useQueryClient();

  const { data: tracks, isLoading } = useQuery({
    queryKey: ['tracks'],
    queryFn: trackService.getTracks,
  });

  const deleteMutation = useMutation({
    mutationFn: trackService.deleteTrack,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tracks'] });
      toast.success('Трек удален');
    },
    onError: () => {
      toast.error('Ошибка при удалении трека');
    },
  });

  const handleDelete = (id: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этот трек?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleEdit = (track: Track) => {
    setEditingTrack(track);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Треки ({tracks?.length || 0})
        </h2>
        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:hover:bg-primary-500"
        >
          Загрузить треки
        </button>
      </div>

      <div className="space-y-3">
        {tracks?.map((track) => (
          <TrackCard
            key={track.id}
            track={track}
            onDelete={handleDelete}
            onEdit={handleEdit}
          />
        ))}
      </div>

      {isUploadModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Загрузка треков
              </h3>
              <button
                onClick={() => setIsUploadModalOpen(false)}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                ×
              </button>
            </div>
            <TrackUpload
              onSuccess={() => {
                queryClient.invalidateQueries({ queryKey: ['tracks'] });
                setIsUploadModalOpen(false);
              }}
              onClose={() => setIsUploadModalOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}; 