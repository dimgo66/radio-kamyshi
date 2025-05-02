import React from 'react';
import { Music, ArrowDownAZ, User, Calendar, ArrowUpDown } from 'lucide-react';
interface TrackListProps {
  activeTab: string;
}
export function TrackList({
  activeTab
}: TrackListProps) {
  const tracks = [{
    id: 1,
    title: 'Белов',
    plays: 14,
    duration: '47:08'
  }, {
    id: 2,
    title: 'Визбору',
    plays: 4,
    duration: '2:16:42'
  }, {
    id: 3,
    title: 'Грибова',
    plays: 105,
    duration: '11:17:11'
  }, {
    id: 4,
    title: 'Есенин',
    plays: 48,
    duration: '1:59:32'
  }, {
    id: 5,
    title: 'Ирина Алексеева',
    plays: 57,
    duration: '3:13:12'
  }, {
    id: 6,
    title: 'Песни разные',
    plays: 85,
    duration: '4:22:57'
  }, {
    id: 7,
    title: 'Репрессии',
    plays: 67,
    duration: '3:30:21'
  }, {
    id: 8,
    title: 'Цветаева-Грибова',
    plays: 7,
    duration: '9:57'
  }, {
    id: 9,
    title: 'Чинарёва',
    plays: 5,
    duration: '14:41'
  }, {
    id: 10,
    title: 'Эдуард Филь',
    plays: 63,
    duration: '3:32:41'
  }, {
    id: 11,
    title: 'Юбилеи',
    plays: 239,
    duration: '19:07:42'
  }];
  const jingles = [{
    id: 1,
    title: 'По одёжке – автор стихов Валерий Фокин, автор музыки Константин Фокин',
    duration: '3:33'
  }, {
    id: 2,
    title: 'ВЕНГРЖНОВСКИЙ – Слово о друге. Королев BB-kissyk.com',
    duration: '33:07'
  }, {
    id: 3,
    title: 'Дмитрий Аникин.mp3',
    duration: '31:57'
  }, {
    id: 4,
    title: 'Матова.mp3',
    duration: '23:17'
  }];
  const ads = [{
    id: 1,
    title: 'Реклама 1',
    duration: '0:30'
  }, {
    id: 2,
    title: 'Реклама 2',
    duration: '0:15'
  }, {
    id: 3,
    title: 'Реклама 3',
    duration: '0:20'
  }];
  let content = [];
  if (activeTab === 'tracks') {
    content = tracks;
  } else if (activeTab === 'jingles') {
    content = jingles;
  } else if (activeTab === 'ads') {
    content = ads;
  }
  return <div className="flex-1 flex flex-col overflow-hidden">
      <div className="p-4 border-b">
        <div className="flex items-center mb-2">
          <Music size={16} className="text-gray-400 mr-2" />
          <span className="text-gray-600">music</span>
        </div>
        <div className="flex items-center text-xs text-gray-500">
          <span className="mr-1">Сортировать по:</span>
          <button className="flex items-center font-medium mx-1">
            Названию <ArrowDownAZ size={14} className="ml-1" />
          </button>
          <button className="flex items-center mx-1">
            Исполнителю <User size={14} className="ml-1" />
          </button>
          <button className="flex items-center mx-1">
            Дате добавления <Calendar size={14} className="ml-1" />
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {content.map(item => <div key={item.id} className="flex items-center p-3 border-b hover:bg-gray-50">
            <div className="w-8 h-8 bg-gray-100 flex items-center justify-center rounded mr-3">
              <Music size={16} className="text-gray-500" />
            </div>
            <div className="flex-1">
              <div className="text-sm">{item.title}</div>
            </div>
            {'plays' in item && <div className="flex items-center text-xs text-gray-500 mr-3">
                <ArrowUpDown size={12} className="mr-1" />
                <span>{item.plays}</span>
              </div>}
            <div className="text-xs text-gray-500">{item.duration}</div>
          </div>)}
      </div>
    </div>;
}