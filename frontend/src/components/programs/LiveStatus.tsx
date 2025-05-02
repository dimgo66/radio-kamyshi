import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { formatTime } from '../../utils';
import { ProgramWithSchedule } from '../../types';
import { programService } from '../../services';

export const LiveStatus: React.FC = () => {
  const { data: currentProgram, isLoading: isCurrentLoading } = useQuery({
    queryKey: ['currentProgram'],
    queryFn: programService.getCurrentProgram,
    refetchInterval: 30000 // Обновляем каждые 30 секунд
  });

  const { data: upcomingPrograms = [], isLoading: isUpcomingLoading } = useQuery({
    queryKey: ['upcomingPrograms'],
    queryFn: () => programService.getUpcomingPrograms(3),
    refetchInterval: 30000
  });

  if (isCurrentLoading || isUpcomingLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-24 bg-gray-200 rounded-lg mb-4"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="p-4 bg-blue-600 text-white">
        <h2 className="text-lg font-semibold">Сейчас в эфире</h2>
      </div>

      <div className="p-4">
        {currentProgram ? (
          <div className="mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <h3 className="text-xl font-medium">{currentProgram.name}</h3>
            </div>
            {currentProgram.schedules[0] && (
              <p className="mt-2 text-gray-600">
                {formatTime(currentProgram.schedules[0].start_time)} -{' '}
                {formatTime(currentProgram.schedules[0].end_time)}
              </p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              {currentProgram.description}
            </p>
          </div>
        ) : (
          <div className="mb-6 text-gray-500">
            Нет активной программы
          </div>
        )}

        {upcomingPrograms.length > 0 && (
          <>
            <h3 className="font-medium text-gray-900 mb-3">
              Далее в программе:
            </h3>
            <div className="space-y-3">
              {upcomingPrograms.map(program => (
                <div
                  key={program.id}
                  className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                >
                  <div>
                    <p className="font-medium">{program.name}</p>
                    {program.schedules[0] && (
                      <p className="text-sm text-gray-600">
                        {formatTime(program.schedules[0].start_time)}
                      </p>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {program.duration} мин
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}; 