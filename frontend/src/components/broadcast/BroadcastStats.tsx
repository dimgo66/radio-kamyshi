import { useState, useEffect } from 'react';
import { broadcastService } from '../../services';
import { ChartBarIcon, SignalIcon, UsersIcon } from '@heroicons/react/24/outline';

interface BroadcastStatsProps {
  mount?: string;
  refreshInterval?: number;
}

export const BroadcastStats = ({ 
  mount = '/stream.mp3', 
  refreshInterval = 10000 
}: BroadcastStatsProps) => {
  const [stats, setStats] = useState({
    status: 'offline',
    listeners: 0,
    title: '',
    artist: '',
    bitrate: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await broadcastService.getStreamStatus(mount);
        setStats(data);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить статистику вещания');
        console.error('Error fetching broadcast stats:', err);
      } finally {
        setLoading(false);
      }
    };

    // Сразу загружаем статистику
    fetchStats();

    // Настраиваем интервал обновления
    const interval = setInterval(fetchStats, refreshInterval);

    // Очищаем интервал при размонтировании
    return () => clearInterval(interval);
  }, [mount, refreshInterval]);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <h3 className="mb-4 text-lg font-medium text-gray-900 dark:text-white">
        Статистика вещания
      </h3>

      {loading ? (
        <div className="flex h-32 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-b-2 border-t-2 border-primary-600"></div>
        </div>
      ) : error ? (
        <div className="flex h-32 items-center justify-center">
          <p className="text-center text-red-500">{error}</p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center space-x-2">
            <div className={`h-3 w-3 rounded-full ${stats.status === 'online' ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="font-medium text-gray-700 dark:text-gray-300">
              {stats.status === 'online' ? 'В эфире' : 'Не в эфире'}
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="flex items-center space-x-2">
              <UsersIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Слушателей</p>
                <p className="text-xl font-semibold text-gray-900 dark:text-white">{stats.listeners}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <SignalIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Битрейт</p>
                <p className="text-xl font-semibold text-gray-900 dark:text-white">{stats.bitrate} kbps</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Формат</p>
                <p className="text-xl font-semibold text-gray-900 dark:text-white">MP3</p>
              </div>
            </div>
          </div>

          {(stats.title || stats.artist) && (
            <div className="border-t border-gray-200 pt-4 dark:border-gray-700">
              <h4 className="mb-2 text-sm font-medium text-gray-500 dark:text-gray-400">Сейчас играет:</h4>
              {stats.title && (
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{stats.title}</p>
              )}
              {stats.artist && (
                <p className="text-md text-gray-600 dark:text-gray-300">{stats.artist}</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 