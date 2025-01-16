import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const RegisterForm: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    display_name: '',
  });
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateField = (field: string, value: string): string | undefined => {
    switch (field) {
      case 'username':
        if (value.length < 3) return 'Username must be at least 3 characters';
        if (value.length > 20) return 'Username must be less than 20 characters';
        if (!/^[a-zA-Z0-9_-]+$/.test(value)) return 'Username can only contain letters, numbers, underscores, and hyphens';
        return '';
      case 'email':
        if (!value.includes('@')) return 'Email must contain @';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Please enter a valid email address';
        return '';
      case 'password':
        if (!value) {
          return 'Password is required';
        }
        if (value.length < 8) {
          return 'Password must be at least 8 characters long';
        }
        return '';
      case 'display_name':
        if (value.length < 2) return 'Display name must be at least 2 characters';
        if (value.length > 30) return 'Display name must be less than 30 characters';
        return '';
      default:
        return '';
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const error = validateField(name, value);
    if (error) {
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields
    const newErrors: {[key: string]: string} = {};
    Object.keys(formData).forEach(key => {
      const error = validateField(key, formData[key as keyof typeof formData]);
      if (error) newErrors[key] = error;
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);

    try {
      await register(
        formData.username,
        formData.email,
        formData.password,
        formData.display_name
      );
      navigate('/chat');
    } catch (err) {
      if (err instanceof Error) {
        // Parse the error message if it's JSON
        try {
          const errorData = JSON.parse(err.message);
          if (typeof errorData === 'object' && errorData !== null) {
            // Handle validation errors from backend
            if (errorData.detail) {
              if (typeof errorData.detail === 'object') {
                // Handle field-specific errors
                Object.entries(errorData.detail).forEach(([field, message]) => {
                  setErrors(prev => ({ ...prev, [field]: String(message) }));
                });
              } else {
                // Handle general error message
                setErrors(prev => ({ ...prev, submit: String(errorData.detail) }));
              }
            } else if (errorData.message) {
              // Handle general error message
              setErrors(prev => ({ ...prev, submit: String(errorData.message) }));
            }
          } else {
            setErrors(prev => ({ ...prev, submit: 'Registration failed. Please try again.' }));
          }
        } catch {
          // If error message isn't JSON, use it directly
          if (err.message.toLowerCase().includes('username')) {
            setErrors(prev => ({ ...prev, username: err.message }));
          } else if (err.message.toLowerCase().includes('email')) {
            setErrors(prev => ({ ...prev, email: err.message }));
          } else {
            setErrors(prev => ({ ...prev, submit: err.message }));
          }
        }
      } else {
        setErrors(prev => ({ ...prev, submit: 'Registration failed. Please try again.' }));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg shadow-xl border border-gray-700">
      <h2 className="text-2xl font-bold mb-6 text-center text-white">Register</h2>
      
      {errors.submit && (
        <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
          {errors.submit}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-200">
            Username
          </label>
          <input
            id="username"
            name="username"
            type="text"
            value={formData.username}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:ring-blue-500 ${
              errors.username ? 'border-red-500 focus:border-red-500' : 'focus:border-blue-500'
            }`}
            required
          />
          {errors.username && (
            <p className="mt-1 text-sm text-red-400">{errors.username}</p>
          )}
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-200">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:ring-blue-500 ${
              errors.email ? 'border-red-500 focus:border-red-500' : 'focus:border-blue-500'
            }`}
            required
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-400">{errors.email}</p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-200">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:ring-blue-500 ${
              errors.password ? 'border-red-500 focus:border-red-500' : 'focus:border-blue-500'
            }`}
            required
          />
          {errors.password && (
            <p className="mt-1 text-sm text-red-400">{errors.password}</p>
          )}
        </div>

        <div>
          <label htmlFor="display_name" className="block text-sm font-medium text-gray-200">
            Display Name
          </label>
          <input
            id="display_name"
            name="display_name"
            type="text"
            value={formData.display_name}
            onChange={handleChange}
            onBlur={handleBlur}
            className={`mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:ring-blue-500 ${
              errors.display_name ? 'border-red-500 focus:border-red-500' : 'focus:border-blue-500'
            }`}
            required
          />
          {errors.display_name && (
            <p className="mt-1 text-sm text-red-400">{errors.display_name}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 focus:ring-offset-gray-800"
        >
          {isLoading ? 'Creating Account...' : 'Register'}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-gray-400">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-400 hover:text-blue-300">
          Login here
        </Link>
      </p>
    </div>
  );
};

export default RegisterForm; 