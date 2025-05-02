import { ReactNode } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export const Dialog = ({ isOpen, onClose, title, children }: DialogProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-end justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          onClick={onClose}
        ></div>

        {/* Trick browser into centering modal contents */}
        <span className="hidden sm:inline-block sm:h-screen sm:align-middle" aria-hidden="true">
          &#8203;
        </span>

        {/* Modal panel */}
        <div className="inline-block transform overflow-hidden rounded-lg bg-white p-5 text-left align-bottom shadow-xl transition-all dark:bg-gray-800 sm:my-8 sm:w-full sm:max-w-lg sm:align-middle">
          <div className="flex items-center justify-between pb-3">
            <h3 className="text-lg font-medium leading-6 text-gray-900 dark:text-white">
              {title}
            </h3>
            <button
              onClick={onClose}
              className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-gray-300"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <div className="mt-2">{children}</div>
        </div>
      </div>
    </div>
  );
}; 