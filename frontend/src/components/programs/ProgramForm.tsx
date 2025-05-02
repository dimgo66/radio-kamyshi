import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { playlistService } from '../../services/playlistService';
import { Program } from '../../services/programService';
import { format } from 'date-fns';

interface ProgramFormProps {
  program?: Program;
  onSubmit: (program: Partial<Program>) => void;
  onCancel: () => void;
}

export const ProgramForm = ({ program, onSubmit, onCancel }: ProgramFormProps) => {
  const [title, setTitle] = useState(program?.title || '');
  const [description, setDescription] = useState(program?.description || '');
  const [playlistId, setPlaylistId] = useState<number | undefined>(program?.playlist_id);
  const [startTime, setStartTime] = useState(
    program?.start_time
      ? format(new Date(program.start_time), "yyyy-MM-dd'T'HH:mm")
      : format(new Date(), "yyyy-MM-dd'T'HH:mm")
  );
  const [endTime, setEndTime] = useState(
    program?.end_time
      ? format(new Date(program.end_time), "yyyy-MM-dd'T'HH:mm")
      : format(new Date(Date.now() + 60 * 60 * 1000), "yyyy-MM-dd'T'HH:mm")
  );
  const [repeatType, setRepeatType] = useState<'none' | 'daily' | 'weekly'>(
    program?.repeat_type || 'none'
  );
  const [repeatInterval, setRepeatInterval] = useState<number>(program?.repeat_interval || 1);
  const [repeatEndDate, setRepeatEndDate] = useState<string | undefined>(
    program?.repeat_end_date
      ? format(new Date(program.repeat_end_date), 'yyyy-MM-dd')
      : undefined
  );

  const { data: playlists, isLoading: isLoadingPlaylists } = useQuery({
    queryKey: ['playlists'],
    queryFn: playlistService.getPlaylists,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const formData: Partial<Program> = {
      title,
      description: description || undefined,
      start_time: new Date(startTime).toISOString(),
      end_time: new Date(endTime).toISOString(),
      playlist_id: playlistId!,
      repeat_type: repeatType,
    };

    if (repeatType !== 'none') {
      formData.repeat_interval = repeatInterval;
      if (repeatEndDate) {
        formData.repeat_end_date = new Date(repeatEndDate).toISOString();
      }
    }

    if (program?.id) {
      formData.id = program.id;
    }

    onSubmit(formData);
  };

  const isStartTimeAfterNow = () => {
    return new Date(startTime) >= new Date();
  };

  const isEndTimeAfterStartTime = () => {
    return new Date(endTime) > new Date(startTime);
  };

  const canSubmit = () => {
    return (
      title.trim() !== '' &&
      playlistId !== undefined &&
      isEndTimeAfterStartTime() &&
      (program?.id !== undefined || isStartTimeAfterNow())
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="title"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Название *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
        />
      </div>

      <div>
        <label
          htmlFor="playlist"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Плейлист *
        </label>
        <select
          id="playlist"
          value={playlistId || ''}
          onChange={(e) => setPlaylistId(e.target.value ? Number(e.target.value) : undefined)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          required
        >
          <option value="">Выберите плейлист</option>
          {playlists?.map((playlist) => (
            <option key={playlist.id} value={playlist.id}>
              {playlist.title}
            </option>
          ))}
        </select>
        {isLoadingPlaylists && <p className="mt-1 text-sm text-gray-500">Загрузка плейлистов...</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label
            htmlFor="startTime"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Дата и время начала *
          </label>
          <input
            type="datetime-local"
            id="startTime"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            required
          />
          {!isStartTimeAfterNow() && !program?.id && (
            <p className="mt-1 text-sm text-red-500">Время начала должно быть в будущем</p>
          )}
        </div>

        <div>
          <label
            htmlFor="endTime"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Дата и время окончания *
          </label>
          <input
            type="datetime-local"
            id="endTime"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            required
          />
          {!isEndTimeAfterStartTime() && (
            <p className="mt-1 text-sm text-red-500">
              Время окончания должно быть позже времени начала
            </p>
          )}
        </div>
      </div>

      <div>
        <label
          htmlFor="repeatType"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Повторение
        </label>
        <select
          id="repeatType"
          value={repeatType}
          onChange={(e) => setRepeatType(e.target.value as 'none' | 'daily' | 'weekly')}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
        >
          <option value="none">Не повторять</option>
          <option value="daily">Ежедневно</option>
          <option value="weekly">Еженедельно</option>
        </select>
      </div>

      {repeatType !== 'none' && (
        <>
          <div>
            <label
              htmlFor="repeatInterval"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Интервал
            </label>
            <input
              type="number"
              id="repeatInterval"
              min="1"
              value={repeatInterval}
              onChange={(e) => setRepeatInterval(Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            />
            <p className="mt-1 text-sm text-gray-500">
              {repeatType === 'daily'
                ? 'Повторять каждые X дней'
                : 'Повторять каждые X недель'}
            </p>
          </div>

          <div>
            <label
              htmlFor="repeatEndDate"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Дата окончания повторений
            </label>
            <input
              type="date"
              id="repeatEndDate"
              value={repeatEndDate || ''}
              onChange={(e) => setRepeatEndDate(e.target.value || undefined)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            />
            <p className="mt-1 text-sm text-gray-500">
              Оставьте пустым для бесконечного повторения
            </p>
          </div>
        </>
      )}

      <div className="mt-6 flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Отмена
        </button>
        <button
          type="submit"
          disabled={!canSubmit()}
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-primary-500 dark:hover:bg-primary-400"
        >
          {program ? 'Сохранить' : 'Создать'}
        </button>
      </div>
    </form>
  );
}; 