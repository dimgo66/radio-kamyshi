import { Program } from '../../services/programService';
import { CalendarIcon, ClockIcon, MusicalNoteIcon, TrashIcon, PencilIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

interface ProgramCardProps {
  program: Program;
  onEdit?: (program: Program) => void;
  onDelete?: (programId: number) => void;
}

export const ProgramCard = ({ program, onEdit, onDelete }: ProgramCardProps) => {
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'dd MMMM yyyy, HH:mm', { locale: ru });
  };

  const formatDuration = () => {
    const start = new Date(program.start_time);
    const end = new Date(program.end_time);
    const durationMs = end.getTime() - start.getTime();
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours > 0 ? `${hours} ч ` : ''}${minutes} мин`;
  };

  const getRepeatTypeLabel = () => {
    switch (program.repeat_type) {
      case 'daily':
        return `Ежедневно${program.repeat_interval && program.repeat_interval > 1 ? ` (каждые ${program.repeat_interval} дн.)` : ''}`;
      case 'weekly':
        return `Еженедельно${program.repeat_interval && program.repeat_interval > 1 ? ` (каждые ${program.repeat_interval} нед.)` : ''}`;
      default:
        return 'Не повторяется';
    }
  };

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <div className="p-5">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {program.title}
          </h3>
          
          <div className="flex space-x-2">
            {onEdit && (
              <button 
                onClick={() => onEdit(program)}
                className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
              >
                <PencilIcon className="h-5 w-5" />
              </button>
            )}
            
            {onDelete && (
              <button 
                onClick={() => onDelete(program.id)}
                className="rounded p-1 text-gray-400 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-900 dark:hover:text-red-400"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
        
        {program.description && (
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {program.description}
          </p>
        )}
        
        <div className="mt-4 space-y-2">
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <CalendarIcon className="mr-2 h-4 w-4" />
            <span>{formatDate(program.start_time)}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <ClockIcon className="mr-2 h-4 w-4" />
            <span>Продолжительность: {formatDuration()}</span>
          </div>
          
          {program.repeat_type && program.repeat_type !== 'none' && (
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <CalendarIcon className="mr-2 h-4 w-4" />
              <span>
                {getRepeatTypeLabel()}
                {program.repeat_end_date && ` до ${format(new Date(program.repeat_end_date), 'dd.MM.yyyy', { locale: ru })}`}
              </span>
            </div>
          )}
          
          {program.playlist && (
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <MusicalNoteIcon className="mr-2 h-4 w-4" />
              <span>Плейлист: {program.playlist.title}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 