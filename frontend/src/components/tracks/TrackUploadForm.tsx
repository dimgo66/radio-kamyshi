import React, { useState, useRef } from 'react';
import { Track } from '../../types';

interface TrackCreate extends Omit<Track, 'id' | 'duration' | 'file_path' | 'file_size' | 'format' | 'bitrate' | 'waveform_data' | 'created_at' | 'updated_at'> {
  file: File;
}

interface TrackUploadFormProps {
  onSubmit: (data: TrackCreate) => void;
  onCancel: () => void;
}

export const TrackUploadForm: React.FC<TrackUploadFormProps> = ({
  onSubmit,
  onCancel
}) => {
  const [formData, setFormData] = useState<Partial<TrackCreate>>({
    title: '',
    artist: '',
    album: '',
    genre: '',
    year: undefined
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title?.trim()) {
      newErrors.title = 'Название трека обязательно';
    }

    if (!selectedFile) {
      newErrors.file = 'Выберите аудиофайл';
    }

    if (formData.year && (formData.year < 1900 || formData.year > new Date().getFullYear())) {
      newErrors.year = 'Укажите корректный год';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate() && selectedFile) {
      onSubmit({
        ...formData as Omit<TrackCreate, 'file'>,
        file: selectedFile
      });
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      // Если название не задано, используем имя файла
      if (!formData.title) {
        const fileName = e.target.files[0].name.replace(/\.[^/.]+$/, '');
        setFormData(prev => ({
          ...prev,
          title: fileName
        }));
      }
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      if (!formData.title) {
        const fileName = e.dataTransfer.files[0].name.replace(/\.[^/.]+$/, '');
        setFormData(prev => ({
          ...prev,
          title: fileName
        }));
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer ${
          selectedFile ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-blue-500'
        }`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="audio/*"
          className="hidden"
        />
        {selectedFile ? (
          <div>
            <p className="text-green-600">✓ {selectedFile.name}</p>
            <p className="text-sm text-gray-500">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} МБ
            </p>
          </div>
        ) : (
          <div>
            <p className="text-gray-600">
              Перетащите аудиофайл сюда или кликните для выбора
            </p>
            <p className="text-sm text-gray-500">
              MP3, WAV, FLAC, OGG или M4A
            </p>
          </div>
        )}
        {errors.file && (
          <p className="mt-1 text-sm text-red-600">{errors.file}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Название трека
        </label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
            errors.title ? 'border-red-500' : ''
          }`}
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Исполнитель
        </label>
        <input
          type="text"
          name="artist"
          value={formData.artist}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Альбом
        </label>
        <input
          type="text"
          name="album"
          value={formData.album}
          onChange={handleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Жанр
          </label>
          <input
            type="text"
            name="genre"
            value={formData.genre}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Год
          </label>
          <input
            type="number"
            name="year"
            value={formData.year || ''}
            onChange={handleChange}
            className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 ${
              errors.year ? 'border-red-500' : ''
            }`}
            min={1900}
            max={new Date().getFullYear()}
          />
          {errors.year && (
            <p className="mt-1 text-sm text-red-600">{errors.year}</p>
          )}
        </div>
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
          Загрузить
        </button>
      </div>
    </form>
  );
}; 