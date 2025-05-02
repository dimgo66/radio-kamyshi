import { useState, useCallback } from 'react';

interface FormState {
  [key: string]: any;
}

interface ValidationRule<T extends FormState> {
  required?: boolean;
  pattern?: RegExp;
  minLength?: number;
  maxLength?: number;
  validate?: (value: any, values?: T) => boolean | string;
}

interface ValidationRules<T extends FormState> {
  [key: string]: ValidationRule<T>;
}

interface Errors {
  [key: string]: string;
}

export function useForm<T extends FormState>(
  initialState: T,
  validationRules?: ValidationRules<T>
) {
  const [values, setValues] = useState<T>(initialState);
  const [errors, setErrors] = useState<Errors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateField = useCallback(
    (name: string, value: any): string => {
      if (!validationRules?.[name]) return '';

      const rules = validationRules[name];

      if (rules.required && !value) {
        return 'Это поле обязательно';
      }

      if (rules.pattern && !rules.pattern.test(value)) {
        return 'Неверный формат';
      }

      if (rules.minLength && value.length < rules.minLength) {
        return `Минимальная длина ${rules.minLength} символов`;
      }

      if (rules.maxLength && value.length > rules.maxLength) {
        return `Максимальная длина ${rules.maxLength} символов`;
      }

      if (rules.validate) {
        const result = rules.validate(value, values);
        if (typeof result === 'string') return result;
        if (!result) return 'Неверное значение';
      }

      return '';
    },
    [validationRules, values]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setValues((prev) => ({ ...prev, [name]: value }));
      
      if (validationRules) {
        const error = validateField(name, value);
        setErrors((prev) => ({ ...prev, [name]: error }));
      }
    },
    [validateField]
  );

  const validate = useCallback((): boolean => {
    if (!validationRules) return true;

    const newErrors: Errors = {};
    let isValid = true;

    Object.keys(validationRules).forEach((key) => {
      const error = validateField(key, values[key]);
      if (error) {
        newErrors[key] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [values, validateField]);

  const handleSubmit = useCallback(
    async (onSubmit: (values: T) => Promise<void>) => {
      if (!validate()) return;

      setIsSubmitting(true);
      try {
        await onSubmit(values);
      } catch (error) {
        console.error('Form submission error:', error);
      } finally {
        setIsSubmitting(false);
      }
    },
    [values, validate]
  );

  const reset = useCallback(() => {
    setValues(initialState);
    setErrors({});
    setIsSubmitting(false);
  }, [initialState]);

  return {
    values,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    reset,
  };
}