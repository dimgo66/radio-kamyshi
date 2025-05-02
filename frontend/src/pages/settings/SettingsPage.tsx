import { useState } from 'react';
import { HiCheck } from 'react-icons/hi2';

interface SettingsSection {
  title: string;
  description: string;
  fields: {
    id: string;
    label: string;
    type: 'text' | 'number' | 'select';
    value: string;
    options?: { value: string; label: string }[];
  }[];
}

const settingsSections: SettingsSection[] = [
  {
    title: 'Основные настройки',
    description: 'Настройки сервера и вещания',
    fields: [
      {
        id: 'serverUrl',
        label: 'URL сервера',
        type: 'text',
        value: 'http://localhost:8000'
      },
      {
        id: 'streamQuality',
        label: 'Качество потока',
        type: 'select',
        value: 'high',
        options: [
          { value: 'low', label: 'Низкое (96kbps)' },
          { value: 'medium', label: 'Среднее (128kbps)' },
          { value: 'high', label: 'Высокое (192kbps)' }
        ]
      }
    ]
  },
  {
    title: 'Расписание',
    description: 'Настройки планировщика',
    fields: [
      {
        id: 'timezone',
        label: 'Часовой пояс',
        type: 'select',
        value: 'UTC+3',
        options: [
          { value: 'UTC+2', label: 'UTC+2' },
          { value: 'UTC+3', label: 'UTC+3' },
          { value: 'UTC+4', label: 'UTC+4' }
        ]
      },
      {
        id: 'defaultDuration',
        label: 'Длительность по умолчанию (минуты)',
        type: 'number',
        value: '60'
      }
    ]
  }
];

export const SettingsPage = () => {
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
            Настройки
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Управление настройками системы
          </p>
        </div>
        <button
          onClick={handleSave}
          className="inline-flex items-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:hover:bg-primary-500"
        >
          {isSaved ? (
            <>
              <HiCheck className="mr-2 h-5 w-5" />
              Сохранено
            </>
          ) : (
            'Сохранить'
          )}
        </button>
      </div>

      <div className="space-y-6">
        {settingsSections.map((section) => (
          <div
            key={section.title}
            className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800"
          >
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">
              {section.title}
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {section.description}
            </p>
            <div className="mt-6 space-y-4">
              {section.fields.map((field) => (
                <div key={field.id}>
                  <label
                    htmlFor={field.id}
                    className="block text-sm font-medium text-gray-700 dark:text-gray-200"
                  >
                    {field.label}
                  </label>
                  {field.type === 'select' ? (
                    <select
                      id={field.id}
                      className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-primary-400"
                      defaultValue={field.value}
                    >
                      {field.options?.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={field.type}
                      id={field.id}
                      className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-primary-400"
                      defaultValue={field.value}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 