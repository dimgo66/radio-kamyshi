import { useAuthStore } from '@/store/authStore';

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Добро пожаловать, {user?.username}!</h1>
        <p className="text-gray-500 mt-2">
          Это панель управления радиостанцией "Камыши". Здесь вы можете управлять треками,
          плейлистами и программами эфира.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Треки"
          description="Управление музыкальной библиотекой"
          icon="🎵"
          link="/tracks"
        />
        <DashboardCard
          title="Плейлисты"
          description="Создание и редактирование плейлистов"
          icon="📑"
          link="/playlists"
        />
        <DashboardCard
          title="Программы"
          description="Управление программами эфира"
          icon="📻"
          link="/programs"
        />
        <DashboardCard
          title="Расписание"
          description="Планирование эфира"
          icon="📅"
          link="/schedule"
        />
      </div>
    </div>
  );
}

interface DashboardCardProps {
  title: string;
  description: string;
  icon: string;
  link: string;
}

function DashboardCard({ title, description, icon, link }: DashboardCardProps) {
  return (
    <a
      href={link}
      className="block p-6 bg-white rounded-lg border border-gray-200 hover:shadow-lg transition-shadow"
    >
      <div className="text-4xl mb-4">{icon}</div>
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="text-gray-500 mt-2">{description}</p>
    </a>
  );
} 