import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  MusicalNoteIcon,
  QueueListIcon,
  RadioIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Главная', href: '/', icon: HomeIcon },
  { name: 'Треки', href: '/tracks', icon: MusicalNoteIcon },
  { name: 'Плейлисты', href: '/playlists', icon: QueueListIcon },
  { name: 'Программы', href: '/programs', icon: RadioIcon },
  { name: 'Расписание', href: '/schedule', icon: CalendarIcon },
];

export function Sidebar() {
  return (
    <div className="hidden md:flex md:flex-shrink-0">
      <div className="flex flex-col w-64">
        <div className="flex flex-col flex-grow border-r border-gray-200 pt-5 pb-4 bg-white overflow-y-auto">
          <div className="flex-grow flex flex-col">
            <nav className="flex-1 px-2 space-y-1">
              {navigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                      isActive
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  <item.icon
                    className="mr-3 flex-shrink-0 h-6 w-6"
                    aria-hidden="true"
                  />
                  {item.name}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
} 