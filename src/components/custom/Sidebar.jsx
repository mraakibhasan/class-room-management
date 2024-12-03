import React, { useState } from "react";
import { Link } from "react-router-dom";
import { FaHome, FaCog, FaClipboardList, FaCalendar , FaSignOutAlt,FaPlus } from "react-icons/fa";

const Sidebar = ({ role }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => setIsCollapsed(!isCollapsed);

  // Icon mapping
  const iconMapping = {
    Dashboard: <FaHome className="w-5 h-5" />,
    "Class Scheudle": <FaCalendar className="w-5 h-5" />,
    "Add Booking": <FaPlus className="w-5 h-5" />,
    Review: <FaClipboardList className="w-5 h-5" />,
    "Log Out": <FaSignOutAlt className="w-5 h-5" />,
    "Enroll in Classes": <FaClipboardList className="w-5 h-5" />,
    Assignments: <FaClipboardList className="w-5 h-5" />,
    Settings: <FaCog className="w-5 h-5" />,
  };

  const menuItems = {
    teacher: [
      { name: "Dashboard", path: "/" },
      { name: "Class Scheudle", path: "/class-scheudle" },
      { name: "Add Booking", path: "/add-booking" },
      { name: "Feedback", path: "/feedback" },
      { name: "Log Out", path: "/login" },
    ],
    student: [
      { name: "Dashboard", path: "/dashboard" },
      { name: "Enroll in Classes", path: "/enroll" },
      { name: "Assignments", path: "/assignments" },
      { name: "Settings", path: "/settings" },
    ],
  };

  const itemsToRender = role === "teacher" ? menuItems.teacher : menuItems.student;

  return (
    <div
      className={`flex flex-col bg-gray-800 text-white shadow-lg transition-all ${
        isCollapsed ? "w-20" : "w-64"
      } min-h-screen sticky top-0`}
    >
      {/* Sidebar Branding */}
      <div className="flex items-center justify-between p-6 bg-gray-900">
        <h2 className={`text-2xl font-bold transition-all ${isCollapsed ? "hidden" : "block"}`}>
          Classroom Management
        </h2>
        <button onClick={toggleSidebar} className="text-white focus:outline-none md:hidden">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth="2"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
      </div>

      {/* Menu Items */}
      <div className="flex flex-col p-4 space-y-2 overflow-y-auto">
        {itemsToRender.map((item) => (
          <Link
            to={item.path}
            key={item.name}
            className={`flex items-center space-x-2 px-4 py-3 rounded-md text-lg transition-all hover:bg-blue-600 focus:outline-none ${
              item.path === window.location.pathname ? "bg-blue-700" : "hover:bg-blue-500"
            }`}
          >
            {iconMapping[item.name]}
            <span className={`${isCollapsed ? "hidden" : "block"}`}>{item.name}</span>
          </Link>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-auto p-4 text-center text-sm text-gray-400">
        <p>© 2024 Class Management System</p>
      </div>
    </div>
  );
};

export default Sidebar;
