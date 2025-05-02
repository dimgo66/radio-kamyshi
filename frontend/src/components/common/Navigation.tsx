import { Link, useLocation } from 'react-router-dom';
import { IconType } from 'react-icons';
import { 
  HiOutlineHome,
  HiOutlineMusicalNote,
  HiOutlineQueueList,
  HiOutlineCog6Tooth,
  HiOutlineCalendar
} from 'react-icons/hi2';

interface NavItem {
  path: string;
  label: string;
  icon: IconType;
}

const navItems: NavItem[] = [
  { path: '/', label: 'Главная', icon: HiOutlineHome },
  { path: '/tracks', label: 'Треки', icon: HiOutlineMusicalNote },
  { path: '/playlists', label: 'Плейлисты', icon: HiOutlineQueueList },
  { path: '/schedule', label: 'Расписание', icon: HiOutlineCalendar },
  { path: '/settings', label: 'Настройки', icon: HiOutlineCog6Tooth },
];

export const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg dark:bg-gray-900">
      <div className="flex h-16 items-center justify-center border-b border-gray-200 dark:border-gray-800">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Радио Камыши</h1>
      </div>
      <div className="p-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`mb-2 flex items-center rounded-lg p-3 text-base font-normal transition-colors ${
                isActive
                  ? 'bg-primary-100 text-primary-900 dark:bg-primary-900 dark:text-primary-100'
                  : 'text-gray-900 hover:bg-gray-100 dark:text-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <Icon className="h-6 w-6" />
              <span className="ml-3">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}; 