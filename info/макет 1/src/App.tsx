import React, { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { TrackQueue } from './components/TrackQueue';
import { TrackList } from './components/TrackList';
import { TabNavigation } from './components/TabNavigation';
export function App() {
  const [activeTab, setActiveTab] = useState('tracks');
  return <div className="flex flex-col h-screen w-full bg-white">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 flex overflow-hidden">
            <TrackQueue />
            <div className="flex-1 flex flex-col border-l">
              <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />
              <TrackList activeTab={activeTab} />
            </div>
          </div>
        </main>
      </div>
    </div>;
}