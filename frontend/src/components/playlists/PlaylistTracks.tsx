import { useState } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult, DroppableProvided, DraggableProvided, DraggableStateSnapshot } from 'react-beautiful-dnd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Track } from '../../services/trackService';
import { playlistService } from '../../services/playlistService';
import { TrashIcon, Bars3Icon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface PlaylistTracksProps {
  playlistId: number;
  tracks: Track[];
}

export const PlaylistTracks = ({ playlistId, tracks }: PlaylistTracksProps) => {
  const [items, setItems] = useState(tracks);
  const queryClient = useQueryClient();

  const reorderMutation = useMutation({
    mutationFn: (trackIds: number[]) =>
      playlistService.reorderPlaylistTracks(playlistId, trackIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist', playlistId] });
      toast.success('Порядок треков обновлен');
    },
    onError: () => {
      toast.error('Ошибка при обновлении порядка треков');
      setItems(tracks); // Восстанавливаем исходный порядок
    },
  });

  const removeTrackMutation = useMutation({
    mutationFn: (trackId: number) =>
      playlistService.removeTrackFromPlaylist(playlistId, trackId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['playlist', playlistId] });
      toast.success('Трек удален из плейлиста');
    },
    onError: () => {
      toast.error('Ошибка при удалении трека из плейлиста');
    },
  });

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return;

    const newItems = Array.from(items);
    const [reorderedItem] = newItems.splice(result.source.index, 1);
    newItems.splice(result.destination.index, 0, reorderedItem);

    setItems(newItems);
    reorderMutation.mutate(newItems.map(item => item.id));
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="tracks">
        {(provided: DroppableProvided) => (
          <div
            {...provided.droppableProps}
            ref={provided.innerRef}
            className="space-y-2"
          >
            {items.map((track, index) => (
              <Draggable
                key={track.id}
                draggableId={track.id.toString()}
                index={index}
              >
                {(provided: DraggableProvided, snapshot: DraggableStateSnapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    className={`group relative flex items-center justify-between rounded-lg border bg-white p-4 shadow-sm transition-all dark:bg-gray-800 ${
                      snapshot.isDragging
                        ? 'border-primary-500 shadow-lg'
                        : 'border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      <div
                        {...provided.dragHandleProps}
                        className="cursor-grab text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        <Bars3Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {track.title}
                        </h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {track.artist || 'Неизвестный исполнитель'} •{' '}
                          {formatDuration(track.duration)}
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => removeTrackMutation.mutate(track.id)}
                      className="rounded p-1 text-gray-400 opacity-0 hover:bg-red-100 hover:text-red-600 group-hover:opacity-100 dark:hover:bg-red-900 dark:hover:text-red-400"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </DragDropContext>
  );
}; 