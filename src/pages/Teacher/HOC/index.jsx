import React, { useState } from "react";
import Sidebar from "@/components/custom/Sidebar";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ErrorMessage, Field, Formik } from "formik";
import * as Yup from "yup";
import { useQuery } from "@tanstack/react-query";
import apiInstance from "@/config/api";

const HocBookingPage = () => {
  const [hocBookings, setHocBookings] = useState([
    { subject: "Mathematics", room: "Room A", time: "8:00 AM - 9:00 AM", hocBooking: true },
    { subject: "Physics", room: "Room B", time: "9:30 AM - 10:30 AM", hocBooking: false },
    { subject: "History", room: "Room C", time: "11:00 AM - 12:00 PM", hocBooking: true },
  ]);

  const {data:bookings} = useQuery({
    queryKey:["schedule_list"],
    queryFn:async()=>{
      try{
        const {data} =  await apiInstance.get("/my-class-list")
        return data.data
      }
      catch(error){
        throw new Error("Something went wrong")
      }
    }
  }) 

  // Calculate the count of normal and HoC classes
  const normalClassesCount = bookings?.filter(booking => !booking.hocBooking).length;
  const hocClassesCount = bookings?.filter(booking => booking.hocBooking).length;

  // Validation schema for the form
  const validationSchema = Yup.object().shape({
    subject: Yup.string().required("Subject is required"),
    room: Yup.string().required("Room is required"),
    time: Yup.string().required("Time is required"),
  });

  const handleSubmit = (values, { resetForm }) => {
    console.log("Form Submitted", values);
    resetForm();
    // Add booking to the state or call API
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar Component */}
      <Sidebar role="teacher" />

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-semibold text-gray-800">Class Scheudled</h1>
        </div>

        {/* Cards displaying the count of normal and HoC classes */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-8 mb-8">
          {/* Normal Classes Card */}
          <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">Normal Classes</h2>
            <p className="text-4xl font-bold text-blue-600">{normalClassesCount}</p>
          </div>

          {/* HoC Classes Card */}
          <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">HoC Classes</h2>
            <p className="text-4xl font-bold text-green-600">{hocClassesCount}</p>
          </div>
        </div>

        {/* HoC Booking Table */}
        <div className="overflow-x-auto bg-white rounded-lg shadow-lg">
          <table className="min-w-full bg-white text-left">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-3 px-6 text-sm font-medium text-gray-600">Batch</th>
                <th className="py-3 px-6 text-sm font-medium text-gray-600">Room</th>
                <th className="py-3 px-6 text-sm font-medium text-gray-600">Time</th>
                <th className="py-3 px-6 text-sm font-medium text-gray-600">Status</th>
                <th className="py-3 px-6 text-sm font-medium text-gray-600">HoC</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {bookings?.map((booking, index) => (
                <tr key={index} className="border-t border-gray-200 hover:bg-gray-50">
                  <td className="py-4 px-6 text-gray-700">{booking.batch}</td>
                  <td className="py-4 px-6 text-gray-700">{booking.room}</td>
                  <td className="py-4 px-6 text-gray-700">{booking.from} - {booking?.to}</td>
                  <td className="py-4 px-2">
                    <div className={`${booking?.booking_status === "Approved"?"bg-emerald-500": "bg-yellow-500"} text-white px-3 py-1 rounded-md text-center`}>{booking?.booking_status}</div>
                  </td>
                  <td className="py-4 px-6">
                    {booking.hocBooking ? (
                      <span className="bg-green-500 text-white px-3 py-1 rounded-md">
                        HoC
                      </span>
                    ) : (
                      <span className="bg-blue-500 text-white px-3 py-1 rounded-md">
                        Normal
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default HocBookingPage;
