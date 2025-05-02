import React from 'react';
import { Play, SkipBack, SkipForward, Repeat, Shuffle, Headphones } from 'lucide-react';
export function Header() {
  return <header className="w-full h-16 bg-white border-b flex items-center justify-between px-4">
      <div className="flex items-center">
        <div className="flex items-center mr-6">
          <div className="h-8 w-8 bg-teal-500 rounded flex items-center justify-center mr-2">
            <span className="text-white font-bold">♫</span>
          </div>
          <span className="font-bold text-xl">AIR</span>
        </div>
        <button className="flex items-center px-3 py-1 rounded-full bg-teal-100 text-teal-600 text-sm mr-4">
          <Headphones size={16} className="mr-1" />
          <span>Слушать</span>
        </button>
      </div>
      <div className="flex items-center space-x-4">
        <button className="p-1 text-gray-600 hover:text-gray-900">
          <SkipBack size={20} />
        </button>
        <button className="p-1 text-gray-600 hover:text-gray-900">
          <Play size={20} />
        </button>
        <button className="p-1 text-gray-600 hover:text-gray-900">
          <SkipForward size={20} />
        </button>
        <button className="p-1 text-gray-600 hover:text-gray-900">
          <Shuffle size={20} />
        </button>
        <button className="p-1 text-gray-600 hover:text-gray-900">
          <Repeat size={20} />
        </button>
      </div>
      <div className="flex items-center space-x-4">
        <div className="text-gray-600">0</div>
        <div className="text-gray-600">06:24:00</div>
      </div>
    </header>;
}