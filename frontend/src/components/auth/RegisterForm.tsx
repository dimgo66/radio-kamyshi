import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import { Alert } from '@/components/common/Alert';
import { useForm } from '@/hooks/useForm';
import { toast } from '@/components/common/Toast';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

const validationRules = {
  username: {
    required: true,
    minLength: 3,
    pattern: /^[a-zA-Z0-9_]+$/,
  },
  email: {
    required: true,
    pattern: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  },
  password: {
    required: true,
    minLength: 6,
  },
  confirmPassword: {
    required: true,
    validate: (value: string, values?: RegisterFormData) =>
      value === values?.password || 'Пароли не совпадают',
  },
} as const;

export function RegisterForm() {
  const navigate = useNavigate();

  const { values, errors, isSubmitting, handleChange, handleSubmit } = useForm<RegisterFormData>(
    {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    },
    validationRules
  );

  const { mutate: register, error } = useMutation({
    mutationFn: async (data: Omit<RegisterFormData, 'confirmPassword'>) => {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка регистрации');
      }

      return response.json();
    },
    onSuccess: () => {
      toast.success('Регистрация успешна. Пожалуйста, войдите в систему.');
      navigate('/auth/login');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleFormSubmit = async (values: RegisterFormData) => {
    const { confirmPassword, ...data } = values;
    register(data);
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(handleFormSubmit); }} className="space-y-4">
      <Input
        label="Имя пользователя"
        type="text"
        name="username"
        value={values.username}
        onChange={handleChange}
        error={errors.username}
        placeholder="username"
        autoComplete="username"
      />
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
        autoComplete="new-password"
      />
      <Input
        label="Подтверждение пароля"
        type="password"
        name="confirmPassword"
        value={values.confirmPassword}
        onChange={handleChange}
        error={errors.confirmPassword}
        placeholder="••••••••"
        autoComplete="new-password"
      />
      {error && <Alert variant="error">{error.message}</Alert>}
      <div className="flex items-center justify-between">
        <Button type="submit" isLoading={isSubmitting}>
          Зарегистрироваться
        </Button>
      </div>
      <div className="text-center text-sm text-gray-500">
        Уже есть аккаунт?{' '}
        <Button
          type="button"
          variant="link"
          className="p-0"
          onClick={() => navigate('/auth/login')}
        >
          Войти
        </Button>
      </div>
    </form>
  );
} 