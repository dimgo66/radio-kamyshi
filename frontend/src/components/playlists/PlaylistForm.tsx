import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Playlist, playlistService } from '../../services/playlistService';
import toast from 'react-hot-toast';

interface PlaylistFormProps {
  playlist?: Playlist;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const PlaylistForm = ({ playlist, onSuccess, onCancel }: PlaylistFormProps) => {
  const [title, setTitle] = useState(playlist?.title || '');
  const [description, setDescription] = useState(playlist?.description || '');
  const queryClient = useQueryClient();

  useEffect(() => {
    if (playlist) {
      setTitle(playlist.title);
      setDescription(playlist.description || '');
    }
  }, [playlist]);

  const createMutation = useMutation({
    mutationFn: playlistService.createPlaylist,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlists'] });
      toast.success('Плейлист создан');
      onSuccess?.();
    },
    onError: () => {
      toast.error('Ошибка при создании плейлиста');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: { id: number; title: string; description?: string }) =>
      playlistService.updatePlaylist(data.id, { title: data.title, description: data.description }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlists'] });
      toast.success('Плейлист обновлен');
      onSuccess?.();
    },
    onError: () => {
      toast.error('Ошибка при обновлении плейлиста');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('Введите название плейлиста');
      return;
    }

    if (playlist) {
      updateMutation.mutate({
        id: playlist.id,
        title: title.trim(),
        description: description.trim() || undefined,
      });
    } else {
      createMutation.mutate({
        title: title.trim(),
        description: description.trim() || undefined,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Название
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
          placeholder="Введите название плейлиста"
        />
      </div>

      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Описание
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
          placeholder="Введите описание плейлиста"
        />
      </div>

      <div className="flex justify-end space-x-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          >
            Отмена
          </button>
        )}
        <button
          type="submit"
          disabled={createMutation.isPending || updateMutation.isPending}
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-primary-500"
        >
          {playlist ? 'Сохранить' : 'Создать'}
        </button>
      </div>
    </form>
  );
}; 