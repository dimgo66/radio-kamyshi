import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Calendar } from '../../components/schedule/Calendar';
import { EventForm } from '../../components/schedule/EventForm';
import { Dialog } from '../../components/common/Dialog';
import { scheduleService, ScheduleEvent, CreateScheduleEventDto, UpdateScheduleEventDto } from '../../services/scheduleService';
import { toast } from 'react-hot-toast';
import { EventApi, EventInput } from '@fullcalendar/core';

export const SchedulePage = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<ScheduleEvent | null>(null);
  const [selectedDates, setSelectedDates] = useState<{ start: Date; end: Date } | null>(null);
  
  const queryClient = useQueryClient();

  const { data: events = [], isLoading } = useQuery({
    queryKey: ['schedule-events'],
    queryFn: () => scheduleService.getEvents(),
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateScheduleEventDto) => scheduleService.createEvent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedule-events'] });
      toast.success('Событие успешно создано');
      setIsCreateModalOpen(false);
    },
    onError: (error) => {
      console.error('Ошибка при создании события:', error);
      toast.error('Ошибка при создании события');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateScheduleEventDto }) => 
      scheduleService.updateEvent(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedule-events'] });
      toast.success('Событие успешно обновлено');
      setIsEditModalOpen(false);
    },
    onError: (error) => {
      console.error('Ошибка при обновлении события:', error);
      toast.error('Ошибка при обновлении события');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => scheduleService.deleteEvent(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedule-events'] });
      toast.success('Событие успешно удалено');
    },
    onError: (error) => {
      console.error('Ошибка при удалении события:', error);
      toast.error('Ошибка при удалении события');
    },
  });

  const handleEventClick = (event: EventApi) => {
    const id = parseInt(event.id);
    
    // Получаем полные данные события из API
    scheduleService.getEvent(id).then((eventData) => {
      setSelectedEvent(eventData);
      setIsEditModalOpen(true);
    }).catch((error) => {
      console.error('Ошибка при получении данных события:', error);
      toast.error('Ошибка при получении данных события');
    });
  };

  const handleDateSelect = (start: Date, end: Date) => {
    setSelectedDates({ start, end });
    setIsCreateModalOpen(true);
  };

  const handleCreateEvent = (eventData: EventInput) => {
    const createData: CreateScheduleEventDto = {
      title: eventData.title as string,
      description: eventData.extendedProps?.description as string | undefined,
      start: typeof eventData.start === 'string' 
        ? eventData.start 
        : eventData.start instanceof Date 
          ? eventData.start.toISOString() 
          : new Date().toISOString(),
      end: typeof eventData.end === 'string' 
        ? eventData.end 
        : eventData.end instanceof Date 
          ? eventData.end.toISOString() 
          : new Date().toISOString(),
      playlist_id: eventData.extendedProps?.playlistId as number | undefined,
      is_recurring: !!eventData.extendedProps?.repeat && eventData.extendedProps.repeat.type !== 'none',
    };

    if (createData.is_recurring && eventData.extendedProps?.repeat) {
      const { type, interval, endDate } = eventData.extendedProps.repeat;
      createData.recurrence_rule = `FREQ=${type === 'daily' ? 'DAILY' : 'WEEKLY'};INTERVAL=${interval}${
        endDate ? `;UNTIL=${new Date(endDate).toISOString().split('T')[0].replace(/-/g, '')}` : ''
      }`;
    }

    createMutation.mutate(createData);
  };

  const handleUpdateEvent = (eventData: EventInput) => {
    if (!selectedEvent) return;

    const updateData: UpdateScheduleEventDto = {
      title: eventData.title as string,
      description: eventData.extendedProps?.description as string | undefined,
      start: typeof eventData.start === 'string' 
        ? eventData.start 
        : eventData.start instanceof Date 
          ? eventData.start.toISOString() 
          : undefined,
      end: typeof eventData.end === 'string' 
        ? eventData.end 
        : eventData.end instanceof Date 
          ? eventData.end.toISOString() 
          : undefined,
      playlist_id: eventData.extendedProps?.playlistId as number | undefined,
      is_recurring: !!eventData.extendedProps?.repeat && eventData.extendedProps.repeat.type !== 'none',
    };

    if (updateData.is_recurring && eventData.extendedProps?.repeat) {
      const { type, interval, endDate } = eventData.extendedProps.repeat;
      updateData.recurrence_rule = `FREQ=${type === 'daily' ? 'DAILY' : 'WEEKLY'};INTERVAL=${interval}${
        endDate ? `;UNTIL=${new Date(endDate).toISOString().split('T')[0].replace(/-/g, '')}` : ''
      }`;
    }

    updateMutation.mutate({ id: selectedEvent.id, data: updateData });
  };

  const handleDeleteEvent = () => {
    if (!selectedEvent) return;
    
    if (window.confirm('Вы уверены, что хотите удалить это событие?')) {
      deleteMutation.mutate(selectedEvent.id);
      setIsEditModalOpen(false);
    }
  };

  // Преобразование данных для календаря
  const calendarEvents = (events as ScheduleEvent[]).map((event) => ({
    id: event.id.toString(),
    title: event.title,
    start: event.start,
    end: event.end,
    extendedProps: {
      description: event.description,
      playlistId: event.playlist_id,
    },
  }));

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Расписание эфира
        </h1>
        <p className="mt-1 text-gray-600 dark:text-gray-400">
          Планируйте и управляйте расписанием радиоэфира
        </p>
      </div>

      <Calendar
        events={calendarEvents}
        onEventClick={handleEventClick}
        onDateSelect={handleDateSelect}
      />

      {/* Модальное окно для создания события */}
      <Dialog
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Создать событие в расписании"
      >
        <EventForm
          startDate={selectedDates?.start}
          endDate={selectedDates?.end}
          onSubmit={handleCreateEvent}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      </Dialog>

      {/* Модальное окно для редактирования события */}
      <Dialog
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Редактировать событие в расписании"
      >
        {selectedEvent && (
          <div>
            <EventForm
              event={{
                id: selectedEvent.id.toString(),
                title: selectedEvent.title,
                start: new Date(selectedEvent.start),
                end: new Date(selectedEvent.end),
                extendedProps: {
                  description: selectedEvent.description,
                  playlistId: selectedEvent.playlist_id,
                },
              }}
              onSubmit={handleUpdateEvent}
              onCancel={() => setIsEditModalOpen(false)}
            />
            <div className="mt-4 flex justify-center">
              <button
                onClick={handleDeleteEvent}
                className="text-sm font-medium text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
              >
                Удалить событие
              </button>
            </div>
          </div>
        )}
      </Dialog>
    </div>
  );
}; 