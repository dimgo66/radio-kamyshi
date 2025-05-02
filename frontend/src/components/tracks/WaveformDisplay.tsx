import React, { useEffect, useRef } from 'react';

interface WaveformDisplayProps {
  waveformData: string;
  color?: string;
  height?: number;
}

export const WaveformDisplay: React.FC<WaveformDisplayProps> = ({
  waveformData,
  color = '#3b82f6',
  height = 48,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !waveformData) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Парсим данные waveform из JSON строки
    const waveform = JSON.parse(waveformData);
    const width = canvas.width;
    
    // Очищаем холст
    ctx.clearRect(0, 0, width, height);
    
    // Установка цвета
    ctx.fillStyle = color;
    
    // Рисуем каждую точку волны
    const barWidth = width / waveform.length;
    const centerY = height / 2;
    
    for (let i = 0; i < waveform.length; i++) {
      const amplitude = waveform[i];
      // Масштабируем амплитуду от -1..1 до высоты канваса
      const barHeight = Math.abs(amplitude) * height;
      
      // Рисуем бар
      const x = i * barWidth;
      const y = centerY - barHeight / 2;
      
      ctx.fillRect(x, y, barWidth - 1, barHeight);
    }
  }, [waveformData, color, height]);

  return (
    <canvas 
      ref={canvasRef} 
      width="600" 
      height={height}
      className="w-full rounded"
    />
  );
}; 