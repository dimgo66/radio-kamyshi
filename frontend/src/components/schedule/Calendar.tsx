import { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { EventInput, EventApi } from '@fullcalendar/core';
import ruLocale from '@fullcalendar/core/locales/ru';

interface CalendarProps {
  events: EventInput[];
  onEventClick?: (event: EventApi) => void;
  onDateSelect?: (start: Date, end: Date) => void;
}

export const Calendar = ({ events, onEventClick, onDateSelect }: CalendarProps) => {
  const [view, setView] = useState<'timeGridWeek' | 'dayGridMonth'>('timeGridWeek');

  return (
    <div className="h-[calc(100vh-12rem)] rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView={view}
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'timeGridWeek,dayGridMonth',
        }}
        locale={ruLocale}
        events={events}
        editable={true}
        selectable={true}
        selectMirror={true}
        dayMaxEvents={true}
        weekends={true}
        allDaySlot={false}
        slotMinTime="00:00:00"
        slotMaxTime="24:00:00"
        slotDuration="00:30:00"
        eventClick={({ event }) => {
          onEventClick?.(event);
        }}
        select={({ start, end }) => {
          onDateSelect?.(start, end);
        }}
        eventContent={(eventInfo) => {
          return (
            <div className="h-full w-full p-1">
              <div className="text-sm font-medium">{eventInfo.event.title}</div>
              {eventInfo.event.extendedProps.description && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {eventInfo.event.extendedProps.description}
                </div>
              )}
            </div>
          );
        }}
        viewDidMount={(info) => {
          setView(info.view.type as 'timeGridWeek' | 'dayGridMonth');
        }}
      />
    </div>
  );
}; 