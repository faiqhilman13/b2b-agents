import React, { ReactNode } from 'react';
import { useTheme } from '../../context/ThemeContext';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
  footer?: ReactNode;
  isHoverable?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  className = '',
  noPadding = false,
  footer,
  isHoverable = false,
  onClick
}) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  return (
    <div 
      className={`
        rounded-lg border shadow-sm
        ${isDark 
          ? 'bg-gray-800 border-gray-700 text-white' 
          : 'bg-white border-gray-200 text-gray-900'
        }
        ${isHoverable 
          ? 'transition-all duration-200 hover:shadow-md ' + 
            (isDark ? 'hover:bg-gray-750' : 'hover:bg-gray-50')
          : ''
        }
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      onClick={onClick}
    >
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-inherit">
          {title && <h3 className="text-lg font-semibold">{title}</h3>}
          {subtitle && <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{subtitle}</p>}
        </div>
      )}
      
      <div className={noPadding ? '' : 'p-6'}>
        {children}
      </div>
      
      {footer && (
        <div className={`
          px-6 py-3 rounded-b-lg border-t 
          ${isDark ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'}
        `}>
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;