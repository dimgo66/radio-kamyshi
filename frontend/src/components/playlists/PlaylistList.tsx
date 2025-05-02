import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Playlist, playlistService } from '../../services/playlistService';
import { PlaylistCard } from './PlaylistCard';
import { PlaylistForm } from './PlaylistForm';
import toast from 'react-hot-toast';

export const PlaylistList = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingPlaylist, setEditingPlaylist] = useState<Playlist | null>(null);
  const queryClient = useQueryClient();

  const { data: playlists, isLoading } = useQuery({
    queryKey: ['playlists'],
    queryFn: playlistService.getPlaylists,
  });

  const deleteMutation = useMutation({
    mutationFn: playlistService.deletePlaylist,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlists'] });
      toast.success('Плейлист удален');
    },
    onError: () => {
      toast.error('Ошибка при удалении плейлиста');
    },
  });

  const handleDelete = (id: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этот плейлист?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleEdit = (playlist: Playlist) => {
    setEditingPlaylist(playlist);
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
          Плейлисты ({playlists?.length || 0})
        </h2>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:hover:bg-primary-500"
        >
          Создать плейлист
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {playlists?.map((playlist) => (
          <PlaylistCard
            key={playlist.id}
            playlist={playlist}
            onDelete={handleDelete}
            onEdit={handleEdit}
          />
        ))}
      </div>

      {(isCreateModalOpen || editingPlaylist) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {editingPlaylist ? 'Редактирование плейлиста' : 'Создание плейлиста'}
              </h3>
              <button
                onClick={() => {
                  setIsCreateModalOpen(false);
                  setEditingPlaylist(null);
                }}
                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
              >
                ×
              </button>
            </div>
            <PlaylistForm
              playlist={editingPlaylist}
              onSuccess={() => {
                setIsCreateModalOpen(false);
                setEditingPlaylist(null);
              }}
              onCancel={() => {
                setIsCreateModalOpen(false);
                setEditingPlaylist(null);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}; 