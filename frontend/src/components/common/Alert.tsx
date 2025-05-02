import { cva, type VariantProps } from 'class-variance-authority';
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

const alertVariants = cva(
  'relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground',
  {
    variants: {
      variant: {
        default: 'bg-background text-foreground',
        success: 'border-green-500/50 text-green-700 dark:text-green-400 [&>svg]:text-green-500',
        warning: 'border-yellow-500/50 text-yellow-700 dark:text-yellow-400 [&>svg]:text-yellow-500',
        error: 'border-red-500/50 text-red-700 dark:text-red-400 [&>svg]:text-red-500',
        info: 'border-blue-500/50 text-blue-700 dark:text-blue-400 [&>svg]:text-blue-500',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

const icons = {
  default: InformationCircleIcon,
  info: InformationCircleIcon,
  success: CheckCircleIcon,
  warning: ExclamationCircleIcon,
  error: XCircleIcon,
};

interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  title?: string;
}

export function Alert({ className, variant = 'default', title, children, ...props }: AlertProps) {
  const Icon = icons[variant || 'default'];

  return (
    <div className={cn(alertVariants({ variant }), className)} {...props} role="alert">
      <Icon className="h-5 w-5" />
      <div className="flex flex-col gap-1">
        {title && <h5 className="font-medium leading-none tracking-tight">{title}</h5>}
        {children && <div className="text-sm [&_p]:leading-relaxed">{children}</div>}
      </div>
    </div>
  );
} 