import React from 'react';
interface TabNavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}
export function TabNavigation({
  activeTab,
  setActiveTab
}: TabNavigationProps) {
  return <div className="flex border-b">
      <button className={`px-6 py-4 text-sm font-medium ${activeTab === 'tracks' ? 'text-teal-500 border-b-2 border-teal-500' : 'text-gray-600'}`} onClick={() => setActiveTab('tracks')}>
        Треки
      </button>
      <button className={`px-6 py-4 text-sm font-medium ${activeTab === 'jingles' ? 'text-teal-500 border-b-2 border-teal-500' : 'text-gray-600'}`} onClick={() => setActiveTab('jingles')}>
        Джинглы
      </button>
      <button className={`px-6 py-4 text-sm font-medium ${activeTab === 'ads' ? 'text-teal-500 border-b-2 border-teal-500' : 'text-gray-600'}`} onClick={() => setActiveTab('ads')}>
        Реклама
      </button>
    </div>;
}