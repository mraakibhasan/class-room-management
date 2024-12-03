import * as Yup from 'yup'

const RegisterSchema = Yup.object().shape({
  username: Yup.string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters'),
  email: Yup.string()
    .required('Email is required')
    .email('Invalid email format'),
  password: Yup.string()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters'),
  role: Yup.string().required('Role is required'),
})

export default RegisterSchema
