export interface Program {
  id: string;
  name: string;
  description: string;
  duration: number;
  playlist_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ProgramSchedule {
  id: string;
  program_id: string;
  start_time: string;
  end_time: string;
  repeat_type?: 'once' | 'daily' | 'weekly' | 'custom';
  repeat_days?: number[];
  priority?: number;
  is_active: boolean;
}

export interface ProgramWithSchedule extends Program {
  schedules: ProgramSchedule[];
}

export interface ProgramCreate {
  name: string;
  description: string;
  duration: number;
  playlist_id?: string;
  schedule?: {
    start_time: string;
    repeat_type?: 'once' | 'daily' | 'weekly' | 'custom';
  };
}

export interface ProgramUpdate {
  id: string;
  name?: string;
  description?: string;
  duration?: number;
  playlist_id?: string;
}

export enum RepeatType {
  ONCE = 'once',
  DAILY = 'daily',
  WEEKLY = 'weekly',
  CUSTOM = 'custom'
} 