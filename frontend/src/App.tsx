import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { HomePage } from './pages/HomePage';
import { TracksPage } from './pages/tracks/TracksPage';
import { PlaylistsPage } from './pages/playlists/PlaylistsPage';
import { SchedulePage } from './pages/schedule/SchedulePage';
import { SettingsPage } from './pages/settings/SettingsPage';

const App = () => {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/tracks" element={<TracksPage />} />
          <Route path="/playlists" element={<PlaylistsPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </MainLayout>
    </Router>
  );
};

export default App; 