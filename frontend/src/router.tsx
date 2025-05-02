import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';
import LoadingSpinner from './components/common/LoadingSpinner';
import { useAuthStore } from './store/authStore';

// Ленивая загрузка страниц
const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'));
const PasswordResetPage = lazy(() => import('./pages/auth/PasswordResetPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const TracksPage = lazy(() => import('./pages/tracks/TracksPage'));
const PlaylistsPage = lazy(() => import('./pages/playlists/PlaylistsPage'));
const PlaylistPage = lazy(() => import('./pages/playlists/PlaylistPage'));
const ProgramsPage = lazy(() => import('./pages/programs/ProgramsPage'));
const SchedulePage = lazy(() => import('./pages/schedule/SchedulePage'));

// Компонент для защищенных маршрутов
function ProtectedRoute() {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return <Outlet />;
}

// Компонент для публичных маршрутов
function PublicRoute() {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export const router = createBrowserRouter([
  {
    element: <Suspense fallback={<LoadingSpinner />}><Outlet /></Suspense>,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          {
            element: <MainLayout />,
            children: [
              {
                path: '/',
                element: <DashboardPage />,
              },
              {
                path: '/tracks',
                element: <TracksPage />,
              },
              {
                path: '/playlists',
                element: <PlaylistsPage />,
              },
              {
                path: '/playlists/:id',
                element: <PlaylistPage />,
              },
              {
                path: '/programs',
                element: <ProgramsPage />,
              },
              {
                path: '/schedule',
                element: <SchedulePage />,
              },
            ],
          },
        ],
      },
      {
        element: <PublicRoute />,
        children: [
          {
            element: <AuthLayout />,
            children: [
              {
                path: '/auth/login',
                element: <LoginPage />,
              },
              {
                path: '/auth/register',
                element: <RegisterPage />,
              },
              {
                path: '/auth/password-reset',
                element: <PasswordResetPage />,
              },
            ],
          },
        ],
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
]); 