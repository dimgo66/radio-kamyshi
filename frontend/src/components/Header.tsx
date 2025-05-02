import { Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Button } from './common/Button';
import { UserCircleIcon } from '@heroicons/react/24/outline';

export function Header() {
  const { user, clearAuth } = useAuthStore();

  const handleLogout = () => {
    clearAuth();
  };

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900">
              Радио Камыши
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <div className="flex items-center space-x-2">
                  <UserCircleIcon className="h-6 w-6 text-gray-400" />
                  <span className="text-sm text-gray-700">{user.username}</span>
                </div>
                <Button variant="ghost" onClick={handleLogout}>
                  Выйти
                </Button>
              </>
            ) : (
              <Link to="/auth/login">
                <Button variant="ghost">Войти</Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
} 