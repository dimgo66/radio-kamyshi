import axios from 'axios';
import { Program } from './programService';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface ScheduleEvent {
  id: number;
  title: string;
  description?: string;
  start: string;
  end: string;
  program_id?: number;
  program?: Program;
  playlist_id?: number;
  is_recurring: boolean;
  recurrence_rule?: string;
}

export interface CreateScheduleEventDto {
  title: string;
  description?: string;
  start: string;
  end: string;
  program_id?: number;
  playlist_id?: number;
  is_recurring?: boolean;
  recurrence_rule?: string;
}

export interface UpdateScheduleEventDto {
  title?: string;
  description?: string;
  start?: string;
  end?: string;
  program_id?: number;
  playlist_id?: number;
  is_recurring?: boolean;
  recurrence_rule?: string;
}

class ScheduleService {
  async getEvents(start?: string, end?: string): Promise<ScheduleEvent[]> {
    const params = start && end ? { start, end } : {};
    const response = await axios.get<ScheduleEvent[]>(`${API_URL}/schedule/events`, {
      params,
    });
    return response.data;
  }

  async getEvent(id: number): Promise<ScheduleEvent> {
    const response = await axios.get<ScheduleEvent>(`${API_URL}/schedule/events/${id}`);
    return response.data;
  }

  async createEvent(data: CreateScheduleEventDto): Promise<ScheduleEvent> {
    const response = await axios.post<ScheduleEvent>(`${API_URL}/schedule/events`, data);
    return response.data;
  }

  async updateEvent(id: number, data: UpdateScheduleEventDto): Promise<ScheduleEvent> {
    const response = await axios.patch<ScheduleEvent>(
      `${API_URL}/schedule/events/${id}`,
      data
    );
    return response.data;
  }

  async deleteEvent(id: number): Promise<void> {
    await axios.delete(`${API_URL}/schedule/events/${id}`);
  }

  async getCurrentOnAir(): Promise<ScheduleEvent | null> {
    try {
      const response = await axios.get<ScheduleEvent>(`${API_URL}/schedule/current`);
      return response.data;
    } catch (error) {
      return null;
    }
  }

  async getUpcoming(limit: number = 5): Promise<ScheduleEvent[]> {
    const response = await axios.get<ScheduleEvent[]>(`${API_URL}/schedule/upcoming`, {
      params: { limit },
    });
    return response.data;
  }
}

export const scheduleService = new ScheduleService(); 