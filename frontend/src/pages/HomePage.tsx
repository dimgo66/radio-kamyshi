import { HiOutlineMusicalNote, HiOutlineQueueList, HiOutlineCalendar } from 'react-icons/hi2';
import { Link } from 'react-router-dom';

const features = [
  {
    title: 'Управление треками',
    description: 'Загружайте и управляйте музыкальными треками',
    icon: HiOutlineMusicalNote,
    path: '/tracks'
  },
  {
    title: 'Плейлисты',
    description: 'Создавайте и редактируйте плейлисты',
    icon: HiOutlineQueueList,
    path: '/playlists'
  },
  {
    title: 'Расписание',
    description: 'Настройка расписания вещания',
    icon: HiOutlineCalendar,
    path: '/schedule'
  }
];

export const HomePage = () => {
  return (
    <div className="py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl">
          Радио Камыши
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600 dark:text-gray-300">
          Система управления интернет-радиовещанием
        </p>
      </div>

      <div className="mt-16">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.title}
                to={feature.path}
                className="relative flex flex-col items-center rounded-2xl border border-gray-200 p-8 transition-all hover:border-primary-500 hover:shadow-lg dark:border-gray-700 dark:hover:border-primary-400"
              >
                <div className="mb-4 rounded-full bg-primary-100 p-3 text-primary-600 dark:bg-primary-900 dark:text-primary-100">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="mt-2 text-center text-gray-500 dark:text-gray-400">
                  {feature.description}
                </p>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}; 