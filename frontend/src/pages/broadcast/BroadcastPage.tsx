import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { scheduleService } from '../../services/scheduleService';
import { MusicalNoteIcon, PlayIcon, PauseIcon, SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { BroadcastStats } from '../../components/broadcast/BroadcastStats';

export const BroadcastPage = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(50);
  const [isMuted, setIsMuted] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);

  // URL потока вещания
  const streamUrl = process.env.REACT_APP_STREAM_URL || 'http://localhost:8000/stream';

  // Получение текущего вещания
  const { data: currentOnAir, isLoading } = useQuery({
    queryKey: ['current-on-air'],
    queryFn: () => scheduleService.getCurrentOnAir(),
    refetchInterval: 60000, // Обновление каждую минуту
  });

  // Получение ближайших событий в расписании
  const { data: upcomingEvents = [] } = useQuery({
    queryKey: ['upcoming-events'],
    queryFn: () => scheduleService.getUpcoming(5),
    refetchInterval: 300000, // Обновление каждые 5 минут
  });

  // Инициализация аудио элемента
  useEffect(() => {
    const audio = new Audio(streamUrl);
    audio.volume = volume / 100;
    setAudioElement(audio);

    return () => {
      audio.pause();
      audio.src = '';
    };
  }, [streamUrl]);

  // Управление воспроизведением
  useEffect(() => {
    if (!audioElement) return;

    if (isPlaying) {
      audioElement.play().catch((error) => {
        console.error('Ошибка воспроизведения:', error);
        setIsPlaying(false);
      });
    } else {
      audioElement.pause();
    }
  }, [isPlaying, audioElement]);

  // Управление громкостью
  useEffect(() => {
    if (!audioElement) return;
    
    audioElement.volume = isMuted ? 0 : volume / 100;
  }, [volume, isMuted, audioElement]);

  const togglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  const toggleMute = () => {
    setIsMuted((prev) => !prev);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseInt(e.target.value, 10);
    setVolume(newVolume);
    if (newVolume > 0 && isMuted) {
      setIsMuted(false);
    }
  };

  const formatTime = (dateString: string) => {
    return format(new Date(dateString), 'HH:mm', { locale: ru });
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'dd MMMM, EEEE', { locale: ru });
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Эфир радио "Камыши"
        </h1>
        <p className="mt-1 text-gray-600 dark:text-gray-400">
          Слушайте прямой эфир и управляйте вещанием
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        <div className="col-span-2">
          {/* Плеер */}
          <div className="overflow-hidden rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Сейчас в эфире
                </h2>
                {isLoading ? (
                  <div className="mt-2 h-6 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
                ) : currentOnAir ? (
                  <div className="mt-2">
                    <p className="text-lg font-medium text-primary-600 dark:text-primary-400">
                      {currentOnAir.title}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {currentOnAir.description}
                    </p>
                    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                      {formatTime(currentOnAir.start)} - {formatTime(currentOnAir.end)}
                    </p>
                  </div>
                ) : (
                  <p className="mt-2 text-gray-500 dark:text-gray-400">
                    Нет текущих трансляций
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-4">
                <button
                  onClick={togglePlay}
                  className="rounded-full bg-primary-600 p-4 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:bg-primary-500 dark:hover:bg-primary-400"
                >
                  {isPlaying ? (
                    <PauseIcon className="h-8 w-8" />
                  ) : (
                    <PlayIcon className="h-8 w-8" />
                  )}
                </button>
              </div>
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between">
                <button
                  onClick={toggleMute}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                >
                  {isMuted || volume === 0 ? (
                    <SpeakerXMarkIcon className="h-6 w-6" />
                  ) : (
                    <SpeakerWaveIcon className="h-6 w-6" />
                  )}
                </button>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={volume}
                  onChange={handleVolumeChange}
                  className="mx-4 h-2 w-full cursor-pointer appearance-none rounded-lg bg-gray-200 accent-primary-600 dark:bg-gray-700"
                />
                <span className="w-12 text-right text-sm text-gray-500 dark:text-gray-400">
                  {volume}%
                </span>
              </div>
            </div>
          </div>

          {/* Информация о текущем дне */}
          <div className="mt-8 overflow-hidden rounded-lg bg-white p-6 shadow dark:bg-gray-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Сегодня в эфире
            </h2>
            <p className="text-md mt-1 font-medium text-gray-600 dark:text-gray-400">
              {formatDate(new Date().toISOString())}
            </p>

            <div className="mt-4 divide-y divide-gray-200 dark:divide-gray-700">
              {upcomingEvents.length > 0 ? (
                upcomingEvents.map((event) => (
                  <div key={event.id} className="py-3">
                    <div className="flex items-center">
                      <MusicalNoteIcon className="mr-3 h-5 w-5 text-primary-500" />
                      <div>
                        <p className="font-medium text-gray-800 dark:text-gray-200">
                          {formatTime(event.start)} - {formatTime(event.end)}
                        </p>
                        <p className="text-gray-600 dark:text-gray-400">{event.title}</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="py-4 text-gray-500 dark:text-gray-400">
                  Нет запланированных передач
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Боковая панель */}
        <div className="space-y-8">
          {/* Статистика вещания */}
          <BroadcastStats streamUrl={streamUrl} />

          {/* О радиостанции */}
          <div className="overflow-hidden rounded-lg bg-white p-6 shadow dark:bg-gray-800">
            <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
              О радиостанции
            </h2>
            
            <p className="text-gray-600 dark:text-gray-400">
              Радио "Камыши" — место, где музыка встречается с природой. Наши программы создают атмосферу уюта и спокойствия, которая идеально сочетается с шелестом камышей на берегу.
            </p>
            
            <div className="mt-6">
              <h3 className="font-medium text-gray-900 dark:text-white">Слушайте нас</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Онлайн-трансляция доступна 24/7 на нашем сайте и в мобильном приложении.
              </p>
              
              <div className="mt-4">
                <a
                  href={streamUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center rounded-md bg-primary-50 px-3 py-2 text-sm font-medium text-primary-600 hover:bg-primary-100 dark:bg-primary-900/20 dark:text-primary-400 dark:hover:bg-primary-900/30"
                >
                  Открыть поток напрямую
                </a>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="font-medium text-gray-900 dark:text-white">Контакты</h3>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Связаться с нами можно по телефону: +7 (123) 456-78-90<br />
                Email: info@radio-kamyshi.ru
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 