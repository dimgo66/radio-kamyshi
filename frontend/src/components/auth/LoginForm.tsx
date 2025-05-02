import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import { Alert } from '@/components/common/Alert';
import { useForm } from '@/hooks/useForm';
import { useAuthStore } from '@/store/authStore';
import { toast } from '@/components/common/Toast';

interface LoginFormData {
  email: string;
  password: string;
}

const validationRules = {
  email: {
    required: true,
    pattern: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  },
  password: {
    required: true,
    minLength: 6,
  },
};

export function LoginForm() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const { values, errors, isSubmitting, handleChange, handleSubmit } = useForm<LoginFormData>(
    {
      email: '',
      password: '',
    },
    validationRules
  );

  const { mutate: login, error } = useMutation({
    mutationFn: async (data: LoginFormData) => {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка входа');
      }

      return response.json();
    },
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      toast.success('Вход выполнен успешно');
      navigate('/');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleFormSubmit = async (values: LoginFormData) => {
    login(values);
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(handleFormSubmit); }} className="space-y-4">
      <Input
        label="Email"
        type="email"
        name="email"
        value={values.email}
        onChange={handleChange}
        error={errors.email}
        placeholder="your@email.com"
        autoComplete="email"
      />
      <Input
        label="Пароль"
        type="password"
        name="password"
        value={values.password}
        onChange={handleChange}
        error={errors.password}
        placeholder="••••••••"
        autoComplete="current-password"
      />
      {error && <Alert variant="error">{error.message}</Alert>}
      <div className="flex items-center justify-between">
        <Button
          type="button"
          variant="link"
          onClick={() => navigate('/auth/password-reset')}
        >
          Забыли пароль?
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          Войти
        </Button>
      </div>
      <div className="text-center text-sm text-gray-500">
        Нет аккаунта?{' '}
        <Button
          type="button"
          variant="link"
          className="p-0"
          onClick={() => navigate('/auth/register')}
        >
          Зарегистрироваться
        </Button>
      </div>
    </form>
  );
} 