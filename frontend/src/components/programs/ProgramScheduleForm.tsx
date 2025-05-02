import React, { useState } from 'react';
import { formatShortDay } from '../../utils';
import { RepeatType } from '../../types';
import type { ProgramSchedule as IProgramSchedule } from '../../types';

// Алиас для импортированного типа, чтобы избежать конфликта
interface ProgramScheduleFormProps {
  schedule?: IProgramSchedule;
  onSubmit: (data: Partial<IProgramSchedule>) => void;
  onCancel: () => void;
}

const initialState: Partial<IProgramSchedule> = {
  start_time: '',
  end_time: '',
  repeat_type: RepeatType.ONCE,
  repeat_days: [],
  priority: 1,
  is_active: true
};

const DAYS_OF_WEEK = [0, 1, 2, 3, 4, 5, 6];

export const ProgramScheduleForm: React.FC<ProgramScheduleFormProps> = ({
  schedule,
  onSubmit,
  onCancel
}) => {
  const [formData, setFormData] = useState<Partial<IProgramSchedule>>(
    schedule || initialState
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.start_time) {
      newErrors.start_time = 'Время начала обязательно';
    }

    if (!formData.end_time) {
      newErrors.end_time = 'Время окончания обязательно';
    }

    if (formData.repeat_type === RepeatType.WEEKLY && (!formData.repeat_days?.length)) {
      newErrors.repeat_days = 'Выберите хотя бы один день недели';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onSubmit(formData);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleDayToggle = (day: number) => {
    setFormData(prev => {
      const currentDays = prev.repeat_days || [];
      const newDays = currentDays.includes(day)
        ? currentDays.filter(d => d !== day)
        : [...currentDays, day];

      return {
        ...prev,
        repeat_days: newDays
      };
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Время начала
          </label>
          <input
            type="time"
            name="start_time"
            value={formData.start_time}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              errors.start_time ? 'border-red-500' : ''
            }`}
          />
          {errors.start_time && (
            <p className="mt-1 text-sm text-red-600">{errors.start_time}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Время окончания
          </label>
          <input
            type="time"
            name="end_time"
            value={formData.end_time}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              errors.end_time ? 'border-red-500' : ''
            }`}
          />
          {errors.end_time && (
            <p className="mt-1 text-sm text-red-600">{errors.end_time}</p>
          )}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Тип повторения
        </label>
        <select
          name="repeat_type"
          value={formData.repeat_type}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value={RepeatType.ONCE}>Один раз</option>
          <option value={RepeatType.DAILY}>Ежедневно</option>
          <option value={RepeatType.WEEKLY}>Еженедельно</option>
          <option value={RepeatType.CUSTOM}>Пользовательское</option>
        </select>
      </div>

      {formData.repeat_type === RepeatType.WEEKLY && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Дни недели
          </label>
          <div className="flex flex-wrap gap-2">
            {DAYS_OF_WEEK.map(day => (
              <button
                key={day}
                type="button"
                onClick={() => handleDayToggle(day)}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  formData.repeat_days?.includes(day)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {formatShortDay(day)}
              </button>
            ))}
          </div>
          {errors.repeat_days && (
            <p className="mt-1 text-sm text-red-600">{errors.repeat_days}</p>
          )}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Приоритет
        </label>
        <input
          type="number"
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          min={1}
          max={10}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          name="is_active"
          checked={formData.is_active}
          onChange={e => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label className="ml-2 block text-sm text-gray-700">
          Расписание активно
        </label>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Отмена
        </button>
        <button
          type="submit"
          className="rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {schedule ? 'Сохранить' : 'Создать'}
        </button>
      </div>
    </form>
  );
}; 