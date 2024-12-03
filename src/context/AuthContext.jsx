import React, { useState, createContext, useContext, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import apiInstance from "../config/api";

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem("is_logged_in") === "true");
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user")) || null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem("access_token") || null);
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem("refresh_token") || null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["check-auth"],
    queryFn: async () => {
      try {
        const response = await apiInstance.get("/profile");
        return response.data;
      } catch (error) {
        throw new Error(error.response?.data?.message || "Authentication error");
      }
    },
    onSuccess: (data) => {
      if (data?.user) {
        setIsLoggedIn(true);
        setUser(data.user);
        localStorage.setItem("is_logged_in", "true");
        localStorage.setItem("user", JSON.stringify(data.user));
      }
    },
    onError: () => {
      setIsLoggedIn(false);
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      localStorage.removeItem("is_logged_in");
      localStorage.removeItem("user");
    },
  });

  useEffect(() => {
    if (data?.user) {
      setIsLoggedIn(true);
      setUser(data.user);
      localStorage.setItem("is_logged_in", "true");
      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("access_token", accessToken); // Store access token
      localStorage.setItem("refresh_token", refreshToken); // Store refresh token
    }
  }, [data]);

  const login = (data) => {

    localStorage.setItem("is_logged_in", "true");
    localStorage.setItem("username", JSON.stringify(data.username));
    localStorage.setItem("access_token", data.access_token); 
    localStorage.setItem("refresh_token", data.refresh_token);
  };

  const logout = () => {
    setIsLoggedIn(false);
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem("is_logged_in");
    localStorage.removeItem("username");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  };
  const role = "Faculty"

  


  return (
    <AuthContext.Provider
      value={{
        isLoggedIn,
        user,
        login,
        logout,
        isLoading,
        isError,
        accessToken,
        refreshToken,
        role
        
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export default AuthProvider;
