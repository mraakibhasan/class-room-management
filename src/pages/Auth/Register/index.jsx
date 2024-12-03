import React from 'react'
import { Formik, Field, ErrorMessage } from 'formik'
import RegisterSchema from './RegisterSchema'// Make sure to create a separate schema for registration
import registerImage from '@/assets/image/register.svg' // Update with your registration image
import { useMutation } from '@tanstack/react-query'
import apiInstance from '@/config/api'
import { useNavigate } from 'react-router-dom'

const Register = () => {
  // Mutation for registration
  const navigate =  useNavigate()
  const { mutateAsync } = useMutation({
    mutationFn: async (values) => {
      try {
        const response = await apiInstance.post('/register', values)
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.message || 'Registration error')
      }
    },
    onSuccess:(res)=>{
        navigate("/login")
    }
  })

  return (
    <div className="w-full h-screen flex items-center justify-center bg-gray-100">
      {/* Left section: Image and title */}
      <div className="hidden md:block w-1/2 p-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-7">Register for the Class Management System</h1>
        <img src={registerImage} alt="Register Illustration" className="w-full max-w-lg mx-auto transform transition-transform" />
      </div>

      {/* Right section: Register form */}
      <div className="w-full max-w-md p-10 bg-white shadow-lg rounded-lg border border-gray-300">
        <h2 className="text-3xl font-semibold text-center text-gray-800 mb-8">Create an Account</h2>

        <Formik
          initialValues={{ username: '', email: '', password: '', role: '' }}
          onSubmit={async (values, { setSubmitting }) => {
            try {
              await mutateAsync(values)
              // Handle success logic (e.g., redirect or store token)
            } catch (error) {
              // Handle error, display feedback to the user
            } finally {
              setSubmitting(false)
            }
          }}
          validationSchema={RegisterSchema}
        >
          {({ handleSubmit, isSubmitting, touched, errors }) => (
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

              {/* Email field */}
              <div className="mb-6">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
                <Field
                  id="email"
                  name="email"
                  type="email"
                  className="mt-2 block w-full px-5 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <ErrorMessage name="email" component="div" className="text-red-500 text-sm mt-2" />
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

              {/* Role dropdown */}
              <div className="mb-6">
                <label htmlFor="role" className="block text-sm font-medium text-gray-700">Select Role</label>
                <Field as="select" id="role" name="role" className="mt-2 block w-full px-5 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                  <option value="">Select Role</option>
                  <option value="Faculty">Faculty</option>
                  <option value="student">Student</option>
                </Field>
                <ErrorMessage name="role" component="div" className="text-red-500 text-sm mt-2" />
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
                  {isSubmitting ? 'Registering...' : 'Register'}
                </button>
              </div>
            </form>
          )}
        </Formik>
      </div>
    </div>
  )
}

export default Register
