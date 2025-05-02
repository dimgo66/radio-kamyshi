import { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { programService, Program } from '../../services/programService';
import { ProgramList } from '../../components/programs/ProgramList';
import { toast } from 'react-hot-toast';

export const ProgramsPage = () => {
  const queryClient = useQueryClient();

  const {
    data: programs,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['programs'],
    queryFn: programService.getPrograms,
  });

  const createMutation = useMutation({
    mutationFn: programService.createProgram,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programs'] });
      toast.success('Программа успешно создана');
    },
    onError: (error) => {
      console.error('Ошибка при создании программы:', error);
      toast.error('Ошибка при создании программы');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (program: Program) =>
      programService.updateProgram(program.id, program),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programs'] });
      toast.success('Программа успешно обновлена');
    },
    onError: (error) => {
      console.error('Ошибка при обновлении программы:', error);
      toast.error('Ошибка при обновлении программы');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: programService.deleteProgram,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programs'] });
      toast.success('Программа успешно удалена');
    },
    onError: (error) => {
      console.error('Ошибка при удалении программы:', error);
      toast.error('Ошибка при удалении программы');
    },
  });

  const handleCreate = (program: Program) => {
    createMutation.mutate(program);
  };

  const handleUpdate = (program: Program) => {
    updateMutation.mutate(program);
  };

  const handleDelete = (programId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить эту программу?')) {
      deleteMutation.mutate(programId);
    }
  };

  if (isError) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h3 className="text-lg font-medium text-red-600 dark:text-red-400">
            Ошибка загрузки данных
          </h3>
          <p className="mt-2 text-gray-500 dark:text-gray-400">
            Пожалуйста, попробуйте обновить страницу
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Программы | Радио Камыши</title>
      </Helmet>

      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Программы
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            Создавайте и управляйте программами эфира
          </p>
        </div>

        <ProgramList
          programs={programs || []}
          isLoading={isLoading}
          onProgramCreate={handleCreate}
          onProgramUpdate={handleUpdate}
          onProgramDelete={handleDelete}
        />
      </div>
    </>
  );
}; 