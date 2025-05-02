import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ArrowUpTrayIcon } from '@heroicons/react/24/outline';
import { trackService } from '../../services/trackService';

interface TrackUploadProps {
  onSuccess?: () => void;
  onClose?: () => void;
}

export const TrackUpload = ({ onSuccess, onClose }: TrackUploadProps) => {
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  const uploadMutation = useMutation({
    mutationFn: trackService.uploadTrack,
    onSuccess: () => {
      toast.success('Трек успешно загружен');
      setUploadProgress(0);
      onSuccess?.();
      onClose?.();
    },
    onError: (error) => {
      toast.error('Ошибка при загрузке трека');
      console.error('Upload error:', error);
      setUploadProgress(0);
    }
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(file => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name.replace(/\.[^/.]+$/, '')); // Используем имя файла как название

      uploadMutation.mutate({
        title: file.name.replace(/\.[^/.]+$/, ''),
        file
      });
    });
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.ogg', '.m4a']
    },
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  return (
    <div className="p-6">
      <div
        {...getRootProps()}
        className={`relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input {...getInputProps()} />
        <ArrowUpTrayIcon className="h-12 w-12 text-gray-400" />
        <p className="mt-4 text-center text-lg font-medium text-gray-600">
          {isDragActive
            ? 'Отпустите файлы для загрузки'
            : 'Перетащите аудиофайлы сюда или кликните для выбора'}
        </p>
        <p className="mt-2 text-center text-sm text-gray-500">
          MP3, WAV, OGG или M4A до 100MB
        </p>
      </div>

      {uploadProgress > 0 && (
        <div className="mt-4">
          <div className="relative pt-1">
            <div className="mb-2 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-primary-600">
                  Загрузка
                </span>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold text-primary-600">
                  {uploadProgress}%
                </span>
              </div>
            </div>
            <div className="h-2 w-full rounded-full bg-gray-200">
              <div
                className="h-2 rounded-full bg-primary-600 transition-all"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 