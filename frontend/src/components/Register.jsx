/**
 * Componente de Registro - TecnoCursos AI
 */

import React, { useState } from 'react';
import {
  FiMail,
  FiLock,
  FiUser,
  FiAlertCircle,
  FiLoader,
} from 'react-icons/fi';

const Register = ({ onRegister, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });

  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Validar formulário
   */
  const validateForm = () => {
    const newErrors = {};

    if (!formData.fullName) {
      newErrors.fullName = 'Nome completo é obrigatório';
    }

    if (!formData.email) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (!formData.password) {
      newErrors.password = 'Senha é obrigatória';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Senha deve ter pelo menos 6 caracteres';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Confirmação de senha é obrigatória';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Senhas não coincidem';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Atualizar campo do formulário
   */
  const handleChange = e => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    // Limpar erro do campo ao digitar
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  /**
   * Submeter formulário
   */
  const handleSubmit = async e => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      setIsLoading(true);
      await onRegister(formData);
    } catch (error) {
      console.error('Erro no registro:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 sm:px-6 lg:px-8'>
      <div className='max-w-md w-full space-y-8'>
        {/* Logo e Título */}
        <div className='text-center'>
          <div className='mx-auto h-20 w-20 bg-indigo-600 rounded-full flex items-center justify-center'>
            <span className='text-white text-3xl font-bold'>TC</span>
          </div>
          <h2 className='mt-6 text-3xl font-extrabold text-gray-900'>
            Criar conta
          </h2>
          <p className='mt-2 text-sm text-gray-600'>
            Ou{' '}
            <button
              onClick={onSwitchToLogin}
              className='font-medium text-indigo-600 hover:text-indigo-500'
            >
              faça login se já tem uma conta
            </button>
          </p>
        </div>

        {/* Formulário */}
        <form className='mt-8 space-y-6' onSubmit={handleSubmit}>
          <div className='bg-white py-8 px-4 shadow-xl rounded-lg sm:px-10'>
            {/* Erro geral */}
            {errors.general && (
              <div className='mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md flex items-center'>
                <FiAlertCircle className='mr-2' />
                {errors.general}
              </div>
            )}

            <div className='space-y-6'>
              {/* Campo Nome Completo */}
              <div>
                <label
                  htmlFor='fullName'
                  className='block text-sm font-medium text-gray-700'
                >
                  Nome Completo
                </label>
                <div className='mt-1 relative'>
                  <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
                    <FiUser className='h-5 w-5 text-gray-400' />
                  </div>
                  <input
                    id='fullName'
                    name='fullName'
                    type='text'
                    autoComplete='name'
                    value={formData.fullName}
                    onChange={handleChange}
                    className={`appearance-none block w-full pl-10 pr-3 py-2 border ${
                      errors.fullName ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                    placeholder='Seu nome completo'
                  />
                </div>
                {errors.fullName && (
                  <p className='mt-2 text-sm text-red-600'>{errors.fullName}</p>
                )}
              </div>

              {/* Campo Email */}
              <div>
                <label
                  htmlFor='email'
                  className='block text-sm font-medium text-gray-700'
                >
                  Email
                </label>
                <div className='mt-1 relative'>
                  <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
                    <FiMail className='h-5 w-5 text-gray-400' />
                  </div>
                  <input
                    id='email'
                    name='email'
                    type='email'
                    autoComplete='email'
                    value={formData.email}
                    onChange={handleChange}
                    className={`appearance-none block w-full pl-10 pr-3 py-2 border ${
                      errors.email ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                    placeholder='seu@email.com'
                  />
                </div>
                {errors.email && (
                  <p className='mt-2 text-sm text-red-600'>{errors.email}</p>
                )}
              </div>

              {/* Campo Senha */}
              <div>
                <label
                  htmlFor='password'
                  className='block text-sm font-medium text-gray-700'
                >
                  Senha
                </label>
                <div className='mt-1 relative'>
                  <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
                    <FiLock className='h-5 w-5 text-gray-400' />
                  </div>
                  <input
                    id='password'
                    name='password'
                    type={showPassword ? 'text' : 'password'}
                    autoComplete='new-password'
                    value={formData.password}
                    onChange={handleChange}
                    className={`appearance-none block w-full pl-10 pr-10 py-2 border ${
                      errors.password ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                    placeholder='••••••••'
                  />
                  <button
                    type='button'
                    className='absolute inset-y-0 right-0 pr-3 flex items-center'
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    <span className='text-gray-400 text-sm'>
                      {showPassword ? 'Ocultar' : 'Mostrar'}
                    </span>
                  </button>
                </div>
                {errors.password && (
                  <p className='mt-2 text-sm text-red-600'>{errors.password}</p>
                )}
              </div>

              {/* Campo Confirmar Senha */}
              <div>
                <label
                  htmlFor='confirmPassword'
                  className='block text-sm font-medium text-gray-700'
                >
                  Confirmar Senha
                </label>
                <div className='mt-1 relative'>
                  <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
                    <FiLock className='h-5 w-5 text-gray-400' />
                  </div>
                  <input
                    id='confirmPassword'
                    name='confirmPassword'
                    type={showConfirmPassword ? 'text' : 'password'}
                    autoComplete='new-password'
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className={`appearance-none block w-full pl-10 pr-10 py-2 border ${
                      errors.confirmPassword
                        ? 'border-red-300'
                        : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                    placeholder='••••••••'
                  />
                  <button
                    type='button'
                    className='absolute inset-y-0 right-0 pr-3 flex items-center'
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    <span className='text-gray-400 text-sm'>
                      {showConfirmPassword ? 'Ocultar' : 'Mostrar'}
                    </span>
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className='mt-2 text-sm text-red-600'>
                    {errors.confirmPassword}
                  </p>
                )}
              </div>

              {/* Botão de Registro */}
              <div>
                <button
                  type='submit'
                  disabled={isLoading}
                  className='w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed'
                >
                  {isLoading ? (
                    <>
                      <FiLoader className='animate-spin h-5 w-5 mr-2' />
                      Criando conta...
                    </>
                  ) : (
                    'Criar conta'
                  )}
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
