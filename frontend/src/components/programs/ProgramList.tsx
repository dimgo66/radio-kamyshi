import { useState } from 'react';
import { Program } from '../../services/programService';
import { ProgramCard } from './ProgramCard';
import { PlusCircleIcon } from '@heroicons/react/24/outline';
import { Dialog } from '../common/Dialog';
import { ProgramForm } from './ProgramForm';

interface ProgramListProps {
  programs: Program[];
  isLoading?: boolean;
  onProgramCreate?: (program: Program) => void;
  onProgramUpdate?: (program: Program) => void;
  onProgramDelete?: (programId: number) => void;
}

export const ProgramList = ({
  programs,
  isLoading = false,
  onProgramCreate,
  onProgramUpdate,
  onProgramDelete,
}: ProgramListProps) => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [programToEdit, setProgramToEdit] = useState<Program | null>(null);

  const handleCreate = (program: Program) => {
    onProgramCreate?.(program);
    setIsCreateModalOpen(false);
  };

  const handleEdit = (program: Program) => {
    setProgramToEdit(program);
    setIsEditModalOpen(true);
  };

  const handleUpdate = (program: Program) => {
    onProgramUpdate?.(program);
    setIsEditModalOpen(false);
  };

  const handleAddProgram = () => {
    setIsCreateModalOpen(true);
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Программы</h2>
        {onProgramCreate && (
          <button
            onClick={handleAddProgram}
            className="inline-flex items-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:hover:bg-primary-500"
          >
            <PlusCircleIcon className="mr-2 h-5 w-5" />
            Добавить программу
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-48 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700"></div>
          ))}
        </div>
      ) : programs.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {programs.map((program) => (
            <ProgramCard
              key={program.id}
              program={program}
              onEdit={onProgramUpdate ? handleEdit : undefined}
              onDelete={onProgramDelete}
            />
          ))}
        </div>
      ) : (
        <div className="flex h-40 flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
          <p className="text-sm text-gray-500 dark:text-gray-400">Программы не найдены</p>
          {onProgramCreate && (
            <button
              onClick={handleAddProgram}
              className="mt-2 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-500"
            >
              Создать программу
            </button>
          )}
        </div>
      )}

      {/* Модальное окно для создания программы */}
      <Dialog
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Создать программу"
      >
        <ProgramForm onSubmit={handleCreate} onCancel={() => setIsCreateModalOpen(false)} />
      </Dialog>

      {/* Модальное окно для редактирования программы */}
      <Dialog
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Редактировать программу"
      >
        {programToEdit && (
          <ProgramForm
            program={programToEdit}
            onSubmit={handleUpdate}
            onCancel={() => setIsEditModalOpen(false)}
          />
        )}
      </Dialog>
    </div>
  );
}; 