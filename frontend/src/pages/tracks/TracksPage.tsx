import { TrackList } from '../../components/tracks/TrackList';

export const TracksPage = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
          Управление треками
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Загружайте и управляйте музыкальными треками для вещания
        </p>
      </div>

      <TrackList />
    </div>
  );
}; 