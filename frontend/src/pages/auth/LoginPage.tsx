import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-center mb-6">
        Вход в систему
      </h1>
      <LoginForm />
    </div>
  );
} 