import { api } from '../lib';
import { Track } from '../types';

const API_URL = '/tracks';

export interface TrackUploadResponse {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message?: string;
}

export const trackService = {
  // Получение всех треков
  getTracks: async (): Promise<Track[]> => {
    const response = await api.get(API_URL);
    return response.data as Track[];
  },

  // Получение трека по ID
  getTrack: async (id: string): Promise<Track> => {
    const response = await api.get(`${API_URL}/${id}`);
    return response.data as Track;
  },

  // Загрузка трека
  uploadTrack: async (file: File, metadata?: Partial<Track>): Promise<TrackUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (metadata) {
      Object.entries(metadata).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, String(value));
        }
      });
    }

    const response = await api.post(`${API_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data as TrackUploadResponse;
  },

  // Обновление метаданных трека
  updateTrack: async (id: string, data: Partial<Track>): Promise<Track> => {
    const response = await api.put(`${API_URL}/${id}`, data);
    return response.data as Track;
  },

  // Удаление трека
  deleteTrack: async (id: string): Promise<void> => {
    await api.delete(`${API_URL}/${id}`);
  },

  // Получение треков плейлиста
  getTracksByPlaylist: async (playlistId: string): Promise<Track[]> => {
    const response = await api.get(`/playlists/${playlistId}/tracks`);
    return response.data as Track[];
  }
}; 