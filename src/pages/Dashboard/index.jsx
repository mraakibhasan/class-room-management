import React, { useState } from "react";
import Sidebar from "@/components/custom/Sidebar";
import { useQuery } from "@tanstack/react-query";
import apiInstance from "@/config/api";
import { useNavigate } from "react-router-dom";

const TeacherDashboard = () => {
  const [activeClassroom, setActiveClassroom] = useState(null);
  const navigate = useNavigate(); // Corrected hook name

  // Query for getting bookings
  const { data: classrooms, isLoading, isError: classRoomError } = useQuery({
    queryKey: ["classroombilable"],
    queryFn: async () => {
      const { data } = await apiInstance.get("/my-bookings");
      return data.data;
    }
  });

  // Query for getting classroom list
  const { data: classListData, isLoading: classListLoading, isError } = useQuery({ // Corrected useQuery typo
    queryKey: ["classroom-list"],
    queryFn: async () => {
      const { data: response } = await apiInstance.get("/class-room-list");
      console.log('Classroom List Response:', response);
      return response.data.classrooms;
    }
  });

  // Format time for display
  const formatTime = (timeString) => {
    if (!timeString) return '';
    const time = new Date(timeString);
    return time.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar role="teacher" />
      <div className="flex-1 overflow-y-auto p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Teacher Dashboard</h1>
          <button 
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            onClick={() => navigate("/add-booking")} // Fixed navigation here
          >
            Add Classroom
          </button>
        </div>

        {/* Classroom Availability Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mb-8">
          {classListData?.map((item, index) => {
            const isAvailable = !item.current_booking;
            return (
              <div
                key={index}
                className={`bg-white p-6 rounded-lg shadow-md ${
                  isAvailable ? "border-l-4 border-green-500" : "border-l-4 border-red-500"
                }`}
                onClick={() => setActiveClassroom(item)}
              >
                <h3 className="text-xl font-semibold text-gray-700">
                  {item.classroom.name}
                </h3>
                <p className="text-gray-500">
                  Campus: {item.classroom.campus}
                </p>
                <p className="text-gray-500">
                  Capacity: {item.classroom.capacity}
                </p>
                <p className={`text-sm mt-2 ${isAvailable ? "text-green-600" : "text-red-600"}`}>
                  {item.status}
                </p>
                {item.hours_until_free && (
                  <p className="text-sm mt-1 text-gray-600">
                    Free in: {item.hours_until_free} hours
                  </p>
                )}
              </div>
            );
          })}
        </div>

        {/* Upcoming Classes Table */}
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Class Schedule</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white rounded-lg shadow-md">
              <thead>
                <tr className="bg-gray-200 text-gray-700">
                  <th className="py-3 px-4 text-left">Campus</th>
                  <th className="py-3 px-4 text-left">Room</th>
                  <th className="py-3 px-4 text-left">Current Status</th>
                  <th className="py-3 px-4 text-left">Current/Next Class</th>
                  <th className="py-3 px-4 text-left">Duration</th>
                  <th className="py-3 px-4 text-left">Equipment</th>
                </tr>
              </thead>
              <tbody>
                {classListData?.map((item, index) => (
                  <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-3 px-4">{item.classroom.campus}</td>
                    <td className="py-3 px-4">{item.classroom.name}</td>
                    <td className="py-3 px-4">
                      <span 
                        className={`px-2 py-1 rounded-full text-xs ${
                          item.current_booking ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {item.current_booking ? 'Occupied' : 'Available'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {item.current_booking ? (
                        <div>
                          <p className="font-medium">{item.current_booking.batch}</p>
                          <p className="text-sm text-gray-600">
                            {item.current_booking.formatted_time}
                          </p>
                        </div>
                      ) : item.upcoming_bookings?.[0] ? (
                        <div>
                          <p className="font-medium">{item.upcoming_bookings[0].batch}</p>
                          <p className="text-sm text-gray-600">
                            {item.upcoming_bookings[0].formatted_time}
                          </p>
                        </div>
                      ) : (
                        <span className="text-gray-500">No upcoming classes</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {item.current_booking?.total_duration_hours || 
                       item.upcoming_bookings?.[0]?.duration_hours || '-'} hours
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-2">
                        <span title="Computers" className="text-sm">💻 {item.classroom.computer_count}</span>
                        <span title="Projectors" className="text-sm">📽️ {item.classroom.projector_count}</span>
                        <span title="Whiteboards" className="text-sm">📋 {item.classroom.whiteboard_count}</span>
                        <span title="Markers" className="text-sm">✍️ {item.classroom.marker_count}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Loading and Error States */}
        {(isLoading || classListLoading) && (
          <div className="text-center py-4">Loading...</div>
        )}

        {(isError || classRoomError) && (
          <div className="text-center py-4 text-red-500">
            Error loading class data. Please try again.
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;
