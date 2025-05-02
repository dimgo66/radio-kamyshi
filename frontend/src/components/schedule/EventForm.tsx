import { useState, useEffect } from 'react';
import { EventInput } from '@fullcalendar/core';
import { Playlist } from '../../services/playlistService';
import { useQuery } from '@tanstack/react-query';
import { playlistService } from '../../services/playlistService';

interface EventFormProps {
  event?: EventInput;
  startDate?: Date;
  endDate?: Date;
  onSubmit: (event: EventInput) => void;
  onCancel: () => void;
}

interface RepeatOptions {
  type: 'none' | 'daily' | 'weekly';
  interval: number;
  endDate?: Date;
}

export const EventForm = ({
  event,
  startDate,
  endDate,
  onSubmit,
  onCancel,
}: EventFormProps) => {
  const [title, setTitle] = useState(event?.title || '');
  const [description, setDescription] = useState(
    (event?.extendedProps?.description as string) || ''
  );
  const [selectedPlaylist, setSelectedPlaylist] = useState<number | null>(
    (event?.extendedProps?.playlistId as number) || null
  );
  const [start, setStart] = useState<Date>(
    event?.start ? new Date(event.start) : startDate || new Date()
  );
  const [end, setEnd] = useState<Date>(
    event?.end ? new Date(event.end) : endDate || new Date()
  );
  const [repeatOptions, setRepeatOptions] = useState<RepeatOptions>({
    type: 'none',
    interval: 1,
  });

  const { data: playlists } = useQuery({
    queryKey: ['playlists'],
    queryFn: playlistService.getPlaylists,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newEvent: EventInput = {
      title,
      start,
      end,
      extendedProps: {
        description,
        playlistId: selectedPlaylist,
        repeat: repeatOptions.type !== 'none' ? repeatOptions : undefined,
      },
    };

    onSubmit(newEvent);
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
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
          required
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
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
        />
      </div>

      <div>
        <label
          htmlFor="playlist"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Плейлист
        </label>
        <select
          id="playlist"
          value={selectedPlaylist || ''}
          onChange={(e) => setSelectedPlaylist(Number(e.target.value) || null)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
          required
        >
          <option value="">Выберите плейлист</option>
          {playlists?.map((playlist) => (
            <option key={playlist.id} value={playlist.id}>
              {playlist.title}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="start"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Начало
          </label>
          <input
            type="datetime-local"
            id="start"
            value={start.toISOString().slice(0, 16)}
            onChange={(e) => setStart(new Date(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
            required
          />
        </div>

        <div>
          <label
            htmlFor="end"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Окончание
          </label>
          <input
            type="datetime-local"
            id="end"
            value={end.toISOString().slice(0, 16)}
            onChange={(e) => setEnd(new Date(e.target.value))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
            required
          />
        </div>
      </div>

      <div>
        <label
          htmlFor="repeat"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Повторение
        </label>
        <select
          id="repeat"
          value={repeatOptions.type}
          onChange={(e) =>
            setRepeatOptions({
              ...repeatOptions,
              type: e.target.value as RepeatOptions['type'],
            })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
        >
          <option value="none">Не повторять</option>
          <option value="daily">Ежедневно</option>
          <option value="weekly">Еженедельно</option>
        </select>

        {repeatOptions.type !== 'none' && (
          <div className="mt-4 space-y-4">
            <div>
              <label
                htmlFor="interval"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Интервал
              </label>
              <input
                type="number"
                id="interval"
                min="1"
                value={repeatOptions.interval}
                onChange={(e) =>
                  setRepeatOptions({
                    ...repeatOptions,
                    interval: Number(e.target.value),
                  })
                }
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
              />
            </div>

            <div>
              <label
                htmlFor="repeatEnd"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Дата окончания повторений
              </label>
              <input
                type="date"
                id="repeatEnd"
                value={repeatOptions.endDate?.toISOString().slice(0, 10) || ''}
                onChange={(e) =>
                  setRepeatOptions({
                    ...repeatOptions,
                    endDate: e.target.value ? new Date(e.target.value) : undefined,
                  })
                }
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
              />
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Отмена
        </button>
        <button
          type="submit"
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:hover:bg-primary-500"
        >
          {event ? 'Сохранить' : 'Создать'}
        </button>
      </div>
    </form>
  );
}; 