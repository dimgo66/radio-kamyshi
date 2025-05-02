import { PlaylistList } from '../../components/playlists/PlaylistList';

export const PlaylistsPage = () => {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
          Управление плейлистами
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Создавайте и управляйте плейлистами для вещания
        </p>
      </div>

      <PlaylistList />
    </div>
  );
}; 