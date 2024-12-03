import React from 'react';
import { Formik, Field, ErrorMessage } from 'formik';
import schema from './Loginschema';
import loginimage from '@/assets/image/login.svg';
import { useMutation } from '@tanstack/react-query';
import apiInstance from '@/config/api';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import { Link } from 'react-router-dom'; 
import { useAuth } from '@/context/AuthContext';

const Login = () => {
  const navigate = useNavigate();  // Initialize navigate function
  const {login} =  useAuth()
  // Mutation for loginaccess_token
  const { mutateAsync } = useMutation({
    mutationFn: async (values) => {
      try {
        const response = await apiInstance.post('/login', {remember_me:true ,  ...values});
        console.log(response.data.data)
        return response.data;

      } catch (error) {
        throw new Error(error.response?.data?.message || 'Authentication error');
      }
    },
    onSuccess: (response) => {
      console.log( "from  success", response.data)
      login(response.data)
      navigate('/');  // Use navigate to redirect
    },
  });

  return (
    <div className="w-full h-screen flex items-center justify-center bg-gray-100">
      {/* Left section: Image and title */}
      <div className="hidden md:block w-1/2 p-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">Welcome to the Class Management System</h1>
        <img src={loginimage} alt="Login Illustration" className="w-full max-w-lg mx-auto transform transition-transform" />
      </div>

      {/* Right section: Login form */}
      <div className="w-full max-w-md p-10 bg-white shadow-lg rounded-lg border border-gray-300">
        <h2 className="text-3xl font-semibold text-center text-gray-800 mb-8">Login</h2>

        <Formik
          initialValues={{ username: '', password: '' }}
          onSubmit={async (values, { setSubmitting }) => {
            try {
              await mutateAsync(values);
            } catch (error) {
              // Handle error here (e.g., set an error state or show a notification)
            } finally {
              setSubmitting(false);
            }
          }}
          validationSchema={schema}
        >
          {({ handleSubmit, isSubmitting }) => (
            <form onSubmit={handleSubmit} noValidate>
              {/* Username field */}
              <div className="mb-6">
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
                <Field
                  id="username"
                  name="username"
                  type="text"
                  className="mt-2 block w-full px-5 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <ErrorMessage name="username" component="div" className="text-red-500 text-sm mt-2" />
              </div>

              {/* Password field */}
              <div className="mb-6">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
                <Field
                  id="password"
                  name="password"
                  type="password"
                  className="mt-2 block w-full px-5 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <ErrorMessage name="password" component="div" className="text-red-500 text-sm mt-2" />
              </div>

              {/* Submit Button */}
              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`w-full py-3 px-4 text-white font-semibold rounded-lg transition-all duration-300 ${isSubmitting
                      ? 'bg-gradient-to-r from-blue-300 to-blue-200 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 focus:outline-none'
                    }`}
                >
                  {isSubmitting ? 'Logging in...' : 'Login'}
                </button>
              </div>

              {/* Registration link */}
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">
                  Don’t have an account?{' '}
                  <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                    Register here
                  </Link>
                </p>
              </div>
            </form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default Login;
