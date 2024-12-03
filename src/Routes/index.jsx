import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';  // Make sure to import your context
import PrivateRoute from './Private';  // Assuming this component is in the same folder
import Login from '../pages/Auth/Login';
import Register from '@/pages/Auth/Register';
import Dashboard from '@/pages/Dashboard';
import HocBookingPage from '@/pages/Teacher/HOC';
import AddBookingForm from '@/pages/Teacher/AddBooking';

const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Private route - only accessible if logged in */}
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />

        <Route 
        path="/class-scheudle"
        element={<PrivateRoute><HocBookingPage/></PrivateRoute>}
        />

        <Route path="/add-booking" element={<PrivateRoute><AddBookingForm/></PrivateRoute>}/>

        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
};

export default Router;