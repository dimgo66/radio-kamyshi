import { ReactNode } from 'react';
import { Navigation } from '../components/common/Navigation';

interface MainLayoutProps {
  children: ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-800">
      <Navigation />
      <main className="ml-64 flex-1 p-8">
        <div className="mx-auto max-w-7xl">
          {children}
        </div>
      </main>
    </div>
  );
};

// Экспорт по умолчанию для использования в маршрутизации
export default MainLayout; 