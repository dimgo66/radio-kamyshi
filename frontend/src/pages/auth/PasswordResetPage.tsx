import { PasswordResetForm } from '@/components/auth/PasswordResetForm';

export default function PasswordResetPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-center mb-6">
        Сброс пароля
      </h1>
      <PasswordResetForm />
    </div>
  );
} 