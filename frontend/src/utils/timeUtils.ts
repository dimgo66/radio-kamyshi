/**
 * Форматирует длительность из секунд в формат "минуты:секунды"
 * @param seconds - длительность в секундах
 * @returns строка в формате MM:SS
 */
export const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

/**
 * Форматирует дату в локализованный формат
 * @param dateString - строка с датой
 * @returns отформатированная дата
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Форматирует дату и время в локализованный формат
 * @param dateString - строка с датой и временем
 * @returns отформатированные дата и время
 */
export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Форматирует время из строки даты в формат "ЧЧ:ММ"
 * @param dateString - строка с датой и временем
 * @returns отформатированное время
 */
export const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Возвращает сокращенное название дня недели
 * @param day - номер дня недели (0 - воскресенье, 6 - суббота)
 * @returns сокращенное название дня недели
 */
export const formatShortDay = (day: number): string => {
  const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
  return days[day] || '';
}; 