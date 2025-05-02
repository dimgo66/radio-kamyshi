import React from 'react';
import { PlayCircle } from 'lucide-react';
export function TrackQueue() {
  const queueItems = [{
    time: '06:16:20',
    title: 'Валерий Пак – Пускай ты вынута другим — ст. С.Есенина',
    duration: '5:24'
  }, {
    time: '06:21:39',
    title: 'Николай Крупин – Е. Чепурных. Может, грех...',
    duration: '1:02'
  }, {
    time: '06:22:35',
    title: 'Коричневый кубик стоит у дороги стихи Михаил Сипер музыка Константин Фокин',
    duration: '2:47',
    isPlaying: true
  }, {
    time: '06:25:28',
    title: 'Лидия Чинарёва – Она не была в Эмиратах (стихи Веры Бутко, музыка Сергея Ключикова)',
    duration: '2:07'
  }, {
    time: '06:27:35',
    title: 'Золотятся КОВРОВЫЕ НИВЫ ст. Сергей Ключиков муз. Ольга Соловьёва исп. Сергей Ключиков',
    duration: '1:44'
  }, {
    time: '06:29:19',
    title: 'Николай Крупин, стихи Михаила Анищенко – Любить',
    duration: '1:48'
  }, {
    time: '06:31:07',
    title: 'Юрий Визбор – В Аркашиной квартире живут другие люди (посв. А.Якушевой)',
    duration: '2:21'
  }, {
    time: '06:33:28',
    title: 'Николай Крупин – Автор неизвестен. Есть Песни...',
    duration: '2:28'
  }, {
    time: '06:35:56',
    title: '02. Осень. муз. и сл. Л.Семаков исп. А.Брунов.mp3',
    duration: '2:53'
  }, {
    time: '06:38:49',
    title: '06. Граф. муз. и ст. Ю.Визбор исп. А.Брунов.mp3',
    duration: '2:12'
  }];
  return <div className="w-[450px] flex flex-col border-r shrink-0">
      <div className="p-4 border-b font-medium">ОЧЕРЕДЬ</div>
      <div className="flex-1 overflow-y-auto">
        {queueItems.map((item, index) => <div key={index} className={`flex items-center p-3 border-b hover:bg-gray-50 ${item.isPlaying ? 'bg-green-50' : ''}`}>
            {item.isPlaying && <div className="text-green-500 mr-2">
                <PlayCircle size={16} />
              </div>}
            <div className="text-xs text-gray-500 w-14 shrink-0">
              {item.time}
            </div>
            <div className="flex-1 text-sm truncate">{item.title}</div>
            <div className="text-xs text-gray-500 w-8 text-right">
              {item.duration}
            </div>
          </div>)}
      </div>
    </div>;
}