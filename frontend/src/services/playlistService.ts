import { api } from '../lib';
import { Track } from '../types';

const API_URL = '/playlists';

export interface Playlist {
  id: string;
  name: string;
  description?: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  track_count: number;
  total_duration: number;
}

export interface PlaylistWithTracks extends Playlist {
  tracks: Track[];
}

export interface PlaylistCreate {
  name: string;
  description?: string;
  is_public?: boolean;
  track_ids?: string[];
}

export interface PlaylistUpdate {
  name?: string;
  description?: string;
  is_public?: boolean;
}

export const playlistService = {
  // Получение всех плейлистов
  getPlaylists: async (): Promise<Playlist[]> => {
    const response = await api.get(API_URL);
    return response.data as Playlist[];
  },

  // Получение плейлиста по ID
  getPlaylist: async (id: string): Promise<PlaylistWithTracks> => {
    const response = await api.get(`${API_URL}/${id}`);
    return response.data as PlaylistWithTracks;
  },

  // Создание плейлиста
  createPlaylist: async (data: PlaylistCreate): Promise<Playlist> => {
    const response = await api.post(API_URL, data);
    return response.data as Playlist;
  },

  // Обновление плейлиста
  updatePlaylist: async (id: string, data: PlaylistUpdate): Promise<Playlist> => {
    const response = await api.put(`${API_URL}/${id}`, data);
    return response.data as Playlist;
  },

  // Удаление плейлиста
  deletePlaylist: async (id: string): Promise<void> => {
    await api.delete(`${API_URL}/${id}`);
  },

  // Добавление трека в плейлист
  addTrackToPlaylist: async (playlistId: string, trackId: string): Promise<void> => {
    await api.post(`${API_URL}/${playlistId}/tracks/${trackId}`);
  },

  // Удаление трека из плейлиста
  removeTrackFromPlaylist: async (playlistId: string, trackId: string): Promise<void> => {
    await api.delete(`${API_URL}/${playlistId}/tracks/${trackId}`);
  },

  // Обновление порядка треков в плейлисте
  updateTracksOrder: async (playlistId: string, trackIds: string[]): Promise<void> => {
    await api.put(`${API_URL}/${playlistId}/tracks/order`, { track_ids: trackIds });
  }
}; 