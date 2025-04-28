import React, { Fragment, useRef, useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import Button from './Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md'
}) => {
  const { theme } = useTheme();
  const modalRef = useRef<HTMLDivElement>(null);
  const [isClosing, setIsClosing] = useState(false);
  
  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsClosing(false);
      onClose();
    }, 200);
  };
  
  const handleOutsideClick = (e: MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      handleClose();
    }
  };

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  if (!isOpen) return null;
  
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  };
  
  const isDark = theme === 'dark';
  const bgClass = isDark ? 'bg-gray-800 text-white' : 'bg-white text-gray-900';
  const borderClass = isDark ? 'border-gray-700' : 'border-gray-200';

  return (
    <div className={`fixed inset-0 z-50 overflow-y-auto ${isClosing ? 'animate-fadeOut' : 'animate-fadeIn'}`}>
      <div className="flex min-h-screen items-center justify-center p-4 text-center">
        <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
        
        <div 
          ref={modalRef}
          className={`
            ${sizeClasses[size]} w-full transform rounded-lg shadow-xl 
            transition-all duration-300 
            ${isClosing ? 'scale-95 opacity-0' : 'scale-100 opacity-100'}
            ${bgClass}
          `}
        >
          {/* Header */}
          {title && (
            <div className={`px-6 py-4 border-b ${borderClass} flex items-center justify-between`}>
              <h3 className="text-lg font-semibold">{title}</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClose}
                className="p-1 rounded-full"
                aria-label="Close"
              >
                <X size={20} />
              </Button>
            </div>
          )}
          
          {/* Content */}
          <div className="px-6 py-4">
            {children}
          </div>
          
          {/* Footer */}
          {footer && (
            <div className={`px-6 py-4 border-t ${borderClass} bg-opacity-50 ${isDark ? 'bg-gray-750' : 'bg-gray-50'}`}>
              {footer}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Modal;