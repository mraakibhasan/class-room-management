import React, { useState, useMemo } from "react";
import Sidebar from "@/components/custom/Sidebar";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiInstance from "@/config/api";

const AddBookingForm = () => {
  const [selectedClass, setSelectedClass] = useState(null);
  const [error, setError] = useState(null);
  const [bookingDetails, setBookingDetails] = useState({
    start_time: "",
    end_time: "",
    batch: "",
    is_hoc_booking: false,
  });

  const [filters, setFilters] = useState({
    class: "",
    computers: 0,
    projectors: 0,
    whiteboards: 0,
    dusters: 0,
    speakers: 0,
    markers: 0,
  });

  const queryClient = useQueryClient();

  // Query for fetching class list
  const { data: classData = [], isLoading } = useQuery({
    queryKey: ["all classes"],
    queryFn: async () => {
      const { data } = await apiInstance.get("/global-class-list");
      return data.data || [];
    },
  });

  // Filter logic
  const filteredClasses = useMemo(() => {
    if (!classData) return [];
    return classData.filter((classItem) => {
      const equipment = classItem.equipment || {};
      return (
        classItem.name.toLowerCase().includes(filters.class.toLowerCase()) &&
        Object.entries(filters).every(([key, value]) => {
          if (key === "class" || !value || value === 0) return true;
          return equipment[key] >= value;
        })
      );
    });
  }, [classData, filters]);

  // Booking mutation
  const createBooking = useMutation({
    mutationFn: async (bookingData) => {
      const response = await apiInstance.post("/create-booking", bookingData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(["all classes"]);
      setSelectedClass(null);
      setBookingDetails({
        start_time: "",
        end_time: "",
        batch: "",
        is_hoc_booking: false,
      });
      setError(null);
    },
    onError: (error) => {
      setError(error?.response?.data?.message || "Failed to create booking");
    },
  });

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    if (!selectedClass) {
      setError("Please select a classroom first");
      return;
    }

    if (!bookingDetails.start_time || !bookingDetails.end_time || !bookingDetails.batch) {
      setError("Please fill in all required fields");
      return;
    }

    const formatDateTime = (dateTimeStr) => {
      const date = new Date(dateTimeStr);
      return date.toISOString().slice(0, 19);
    };

    const bookingData = {
      classroom_id: selectedClass.id,
      start_time: formatDateTime(bookingDetails.start_time),
      end_time: formatDateTime(bookingDetails.end_time),
      batch: bookingDetails.batch,
      is_hoc_booking: bookingDetails.is_hoc_booking
    };

    try {
      await createBooking.mutateAsync(bookingData);
    } catch (error) {
      console.error("Submit error:", error);
    }
  };

  const handleClassClick = (classItem) => {
    setSelectedClass(classItem);
    if (classItem.freeTime) {
      setBookingDetails(prev => ({
        ...prev,
        start_time: classItem.freeTime
      }));
    }
  };

  const calculateTimeLeft = (freeTime) => {
    if (!freeTime) return "No time specified";
    
    const currentTime = new Date();
    const freeTimeDate = new Date(freeTime);
    const timeDifference = freeTimeDate - currentTime;

    if (timeDifference <= 0) {
      return "Already available";
    }

    const hoursLeft = Math.floor(timeDifference / (1000 * 60 * 60));
    const minutesLeft = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));

    return `${hoursLeft} hours ${minutesLeft} minutes`;
  };

  const getClassCardColor = (available) => {
    return available ? "bg-green-500" : "bg-red-500";
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: name === "class" ? value : Number(value),
    }));
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar role="teacher" />
      <div className="flex-1 p-8">
        {/* Filter Section */}
        <div className="mb-6 p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Filter Classes</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Class Name</label>
              <input
                type="text"
                name="class"
                value={filters.class}
                onChange={handleFilterChange}
                className="mt-1 p-2 w-full border border-gray-300 rounded"
                placeholder="Search by class name"
              />
            </div>
            {/* Equipment filter inputs */}
            {["computers", "projectors", "whiteboards", "dusters", "speakers", "markers"].map((equipment) => (
              <div key={equipment}>
                <label className="block text-sm font-medium text-gray-700 capitalize">
                  {equipment}
                </label>
                <input
                  type="number"
                  name={equipment}
                  value={filters[equipment]}
                  onChange={handleFilterChange}
                  min="0"
                  className="mt-1 p-2 w-full border border-gray-300 rounded"
                  placeholder={`Min. ${equipment}`}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Class Cards Section */}
        {isLoading ? (
          <div className="text-center py-4">Loading classes...</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredClasses.map((classItem) => (
              <div
                key={classItem.id}
                className={`${getClassCardColor(classItem.available)} p-6 rounded-lg shadow-lg text-white cursor-pointer`}
                onClick={() => handleClassClick(classItem)}
              >
                <h2 className="text-xl font-semibold">{classItem.name}</h2>
                <p className="mt-2">Capacity: {classItem.capacity}</p>
                <p className="mt-2">Time Left: {calculateTimeLeft(classItem.freeTime)}</p>
                <div className="mt-2 text-sm">
                  {Object.entries(classItem.equipment || {}).map(([key, value]) => (
                    <span key={key} className="mr-2">
                      {key}: {value}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Booking Form */}
        {selectedClass && (
          <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Create Booking</h3>
            <form onSubmit={handleBookingSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Start Time</label>
                  <input
                    type="datetime-local"
                    value={bookingDetails.start_time}
                    onChange={(e) => setBookingDetails(prev => ({
                      ...prev,
                      start_time: e.target.value
                    }))}
                    required
                    className="mt-1 p-2 w-full border border-gray-300 rounded"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">End Time</label>
                  <input
                    type="datetime-local"
                    value={bookingDetails.end_time}
                    onChange={(e) => setBookingDetails(prev => ({
                      ...prev,
                      end_time: e.target.value
                    }))}
                    required
                    className="mt-1 p-2 w-full border border-gray-300 rounded"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Batch</label>
                  <input
                    type="text"
                    value={bookingDetails.batch}
                    onChange={(e) => setBookingDetails(prev => ({
                      ...prev,
                      batch: e.target.value
                    }))}
                    required
                    className="mt-1 p-2 w-full border border-gray-300 rounded"
                  />
                </div>
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={bookingDetails.is_hoc_booking}
                      onChange={() => setBookingDetails(prev => ({
                        ...prev,
                        is_hoc_booking: !prev.is_hoc_booking
                      }))}
                      className="mr-2"
                    />
                    HOC Booking
                  </label>
                </div>
              </div>
              <button
                type="submit"
                className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg"
              >
                Submit Booking
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default AddBookingForm;
