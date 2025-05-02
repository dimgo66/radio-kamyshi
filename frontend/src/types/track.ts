export interface Track {
  id: string;
  title: string;
  artist?: string;
  album?: string;
  genre?: string;
  year?: number;
  duration: number;
  file_path: string;
  file_size: number;
  format: string;
  bitrate: number;
  waveform_data?: number[];
  created_at: string;
  updated_at: string;
}

export interface TrackCreate {
  title: string;
  artist?: string;
  album?: string;
  genre?: string;
  year?: number;
  file: File;
}

export interface TrackUpdate {
  title?: string;
  artist?: string;
  album?: string;
  genre?: string;
  year?: number;
} 