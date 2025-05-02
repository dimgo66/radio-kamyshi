import React, { useState } from 'react';
import { Home, Radio, Music, BarChart2, Settings, ShoppingBag, Globe, HelpCircle, ListMusic, Calendar, Repeat, Share2, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
export function Sidebar() {
  const [isAirControlOpen, setIsAirControlOpen] = useState(true);
  return <aside className="w-[220px] bg-gray-900 text-gray-300 flex flex-col shrink-0">
      <div className="p-4 border-b border-gray-800">
        <div className="text-white font-medium">АНТОЛОГИЯ</div>
        <div className="text-xs text-gray-400">LIVE 50 (128 кбит/с) AIR</div>
      </div>
      <nav className="flex-1 overflow-y-auto py-2">
        <NavItem icon={<Home size={18} />} label="Главный экран" active={true} />
        <div>
          <button onClick={() => setIsAirControlOpen(!isAirControlOpen)} className="w-full flex items-center px-4 py-3 text-sm hover:bg-gray-800">
            <span className="mr-3">
              <Radio size={18} />
            </span>
            <span>Управление эфиром</span>
            <span className="ml-auto">
              {isAirControlOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </span>
          </button>
          {isAirControlOpen && <div className="pl-9">
              <SubNavItem icon={<ListMusic size={16} />} label="Плейлисты" />
              <SubNavItem icon={<Calendar size={16} />} label="Планировщик эфира" />
              <SubNavItem icon={<Repeat size={16} />} label="Ротатор" />
              <SubNavItem icon={<Share2 size={16} />} label="Ретрансляторы" />
              <SubNavItem icon={<MessageSquare size={16} />} label="Заказы песен" />
            </div>}
        </div>
        <NavItem icon={<Music size={18} />} label="Пульт диджея" badge="NEW" />
        <NavItem icon={<BarChart2 size={18} />} label="Статистика" />
        <NavItem icon={<Settings size={18} />} label="Настройки" />
        <NavItem icon={<ShoppingBag size={18} />} label="Тарифы и оплата" />
        <NavItem icon={<Globe size={18} />} label="Сайт станции" />
        <NavItem icon={<HelpCircle size={18} />} label="Справочник" />
      </nav>
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-400 mb-1">
          Слушателей: <span className="text-white">0</span>
        </div>
        <div className="text-xs text-gray-400">
          Занято: <span className="text-white">4.58 ГБ / 5.00 ГБ</span>
        </div>
      </div>
    </aside>;
}
interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  badge?: string;
}
function NavItem({
  icon,
  label,
  active,
  badge
}: NavItemProps) {
  return <a href="#" className={`flex items-center px-4 py-3 text-sm hover:bg-gray-800 ${active ? 'text-white bg-gray-800' : ''}`}>
      <span className="mr-3">{icon}</span>
      <span>{label}</span>
      {badge && <span className="ml-auto text-xs bg-red-500 text-white px-1 py-0.5 rounded">
          {badge}
        </span>}
    </a>;
}
interface SubNavItemProps {
  icon: React.ReactNode;
  label: string;
}
function SubNavItem({
  icon,
  label
}: SubNavItemProps) {
  return <a href="#" className="flex items-center py-2 text-sm text-gray-400 hover:text-gray-300">
      <span className="mr-2">{icon}</span>
      <span>{label}</span>
    </a>;
}