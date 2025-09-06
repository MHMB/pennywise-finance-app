import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import toast from 'react-hot-toast';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  telegram_chat_id?: string;
}

const Register: React.FC = () => {
  const { register: registerUser } = useAuth();
  const { t } = useLanguage();
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    try {
      await registerUser(data);
      toast.success(t('auth.registerSuccess'));
    } catch (error: any) {
      toast.error(error.response?.data?.error || t('auth.registerError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {t('auth.register')}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Create your Pennywise Finance account
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="form-label">
                {t('auth.username')}
              </label>
              <input
                {...register('username', { required: t('validation.required') })}
                type="text"
                className="form-input"
                placeholder={t('auth.username')}
              />
              {errors.username && (
                <p className="form-error">{errors.username.message}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="email" className="form-label">
                {t('auth.email')}
              </label>
              <input
                {...register('email', { 
                  required: t('validation.required'),
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: t('validation.email')
                  }
                })}
                type="email"
                className="form-input"
                placeholder={t('auth.email')}
              />
              {errors.email && (
                <p className="form-error">{errors.email.message}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="password" className="form-label">
                {t('auth.password')}
              </label>
              <input
                {...register('password', { 
                  required: t('validation.required'),
                  minLength: {
                    value: 8,
                    message: t('validation.minLength').replace('{{min}}', '8')
                  }
                })}
                type="password"
                className="form-input"
                placeholder={t('auth.password')}
              />
              {errors.password && (
                <p className="form-error">{errors.password.message}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="password_confirm" className="form-label">
                {t('auth.confirmPassword')}
              </label>
              <input
                {...register('password_confirm', { 
                  required: t('validation.required'),
                  validate: value => value === password || t('auth.passwordsDoNotMatch')
                })}
                type="password"
                className="form-input"
                placeholder={t('auth.confirmPassword')}
              />
              {errors.password_confirm && (
                <p className="form-error">{errors.password_confirm.message}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="telegram_chat_id" className="form-label">
                {t('settings.telegram')} Chat ID ({t('common.optional')})
              </label>
              <input
                {...register('telegram_chat_id')}
                type="text"
                className="form-input"
                placeholder="Telegram Chat ID"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? <LoadingSpinner size="sm" /> : t('auth.register')}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                {t('auth.login')}
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;