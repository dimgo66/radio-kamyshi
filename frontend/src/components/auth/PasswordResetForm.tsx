import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Input } from '@/components/common/Input';
import { Button } from '@/components/common/Button';
import { Alert } from '@/components/common/Alert';
import { useForm } from '@/hooks/useForm';
import { toast } from '@/components/common/Toast';

interface PasswordResetFormData {
  email: string;
}

const validationRules = {
  email: {
    required: true,
    pattern: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  },
};

export function PasswordResetForm() {
  const navigate = useNavigate();

  const { values, errors, isSubmitting, handleChange, handleSubmit } = useForm<PasswordResetFormData>(
    {
      email: '',
    },
    validationRules
  );

  const { mutate: resetPassword, error } = useMutation({
    mutationFn: async (data: PasswordResetFormData) => {
      const response = await fetch('/api/v1/auth/password-reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка сброса пароля');
      }

      return response.json();
    },
    onSuccess: () => {
      toast.success('Инструкции по сбросу пароля отправлены на ваш email');
      navigate('/auth/login');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleFormSubmit = async (values: PasswordResetFormData) => {
    resetPassword(values);
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(handleFormSubmit); }} className="space-y-4">
      <div className="text-center mb-4">
        <h2 className="text-2xl font-bold">Сброс пароля</h2>
        <p className="text-gray-500">
          Введите email, указанный при регистрации, и мы отправим вам инструкции по сбросу пароля.
        </p>
      </div>
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
      {error && <Alert variant="error">{error.message}</Alert>}
      <div className="flex items-center justify-between">
        <Button
          type="button"
          variant="link"
          onClick={() => navigate('/auth/login')}
        >
          Вернуться к входу
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          Сбросить пароль
        </Button>
      </div>
    </form>
  );
} 