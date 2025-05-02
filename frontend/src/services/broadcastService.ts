import { api } from '../lib';

interface BroadcastStatus {
  server_status: string;
  sources: Array<{
    mount: string;
    listeners: number;
    title: string;
    artist: string;
    bitrate: number;
    is_active: boolean;
  }>;
  clients: number;
  listeners: number;
  connections: number;
  error?: string;
}

interface StreamStatus {
  status: string;
  listeners: number;
  title: string;
  artist: string;
  bitrate: number;
}

interface MetadataUpdateResponse {
  success: boolean;
  message: string;
  mount: string;
  title: string;
  artist?: string;
}

export const broadcastService = {
  /**
   * Получает общий статус вещания
   */
  getBroadcastStatus: async (): Promise<BroadcastStatus> => {
    const response = await api.get('/broadcast/status');
    return response.data as BroadcastStatus;
  },

  /**
   * Получает статус конкретного потока
   */
  getStreamStatus: async (mount: string): Promise<StreamStatus> => {
    const response = await api.get(`/broadcast/stream/${mount}`);
    return response.data as StreamStatus;
  },

  /**
   * Обновляет метаданные трека в потоке
   */
  updateMetadata: async (mount: string, title: string, artist?: string): Promise<MetadataUpdateResponse> => {
    const response = await api.post(`/broadcast/metadata/${mount}`, { title, artist });
    return response.data as MetadataUpdateResponse;
  },

  /**
   * Получает URL для прослушивания потока
   */
  getStreamUrl: (mount: string = '/stream.mp3'): string => {
    // Убираем /api/v1 из базового URL
    const baseUrl = api.defaults.baseURL?.replace('/api/v1', '') || '';
    return `${baseUrl}${mount}`;
  }
}; 