import { api } from '../lib';
import { Program, ProgramSchedule, ProgramWithSchedule } from '../types';

const API_URL = '/programs';

export const programService = {
  // Programs
  getPrograms: async (): Promise<Program[]> => {
    const response = await api.get(API_URL);
    return response.data as Program[];
  },

  getProgram: async (id: string): Promise<ProgramWithSchedule> => {
    const response = await api.get(`${API_URL}/${id}`);
    return response.data as ProgramWithSchedule;
  },

  createProgram: async (program: Omit<Program, 'id' | 'created_at' | 'updated_at'>): Promise<Program> => {
    const response = await api.post(API_URL, program);
    return response.data as Program;
  },

  updateProgram: async (id: string, program: Partial<Program>): Promise<Program> => {
    const response = await api.put(`${API_URL}/${id}`, program);
    return response.data as Program;
  },

  deleteProgram: async (id: string): Promise<void> => {
    await api.delete(`${API_URL}/${id}`);
  },

  // Schedules
  getSchedules: async (): Promise<ProgramSchedule[]> => {
    const response = await api.get(`${API_URL}/schedules`);
    return response.data as ProgramSchedule[];
  },

  createSchedule: async (schedule: Omit<ProgramSchedule, 'id'>): Promise<ProgramSchedule> => {
    const response = await api.post(`${API_URL}/schedules`, schedule);
    return response.data as ProgramSchedule;
  },

  updateSchedule: async (id: string, schedule: Partial<ProgramSchedule>): Promise<ProgramSchedule> => {
    const response = await api.put(`${API_URL}/schedules/${id}`, schedule);
    return response.data as ProgramSchedule;
  },

  deleteSchedule: async (id: string): Promise<void> => {
    await api.delete(`${API_URL}/schedules/${id}`);
  },

  // Current status
  getCurrentProgram: async (): Promise<ProgramWithSchedule | null> => {
    const response = await api.get(`${API_URL}/current`);
    return response.data as ProgramWithSchedule | null;
  },

  getUpcomingPrograms: async (limit: number = 5): Promise<ProgramWithSchedule[]> => {
    const response = await api.get(`${API_URL}/upcoming?limit=${limit}`);
    return response.data as ProgramWithSchedule[];
  }
}; 