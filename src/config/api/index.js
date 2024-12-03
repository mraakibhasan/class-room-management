import axios from 'axios';

// Function to retrieve tokens from localStorage
const getAccessToken = () => localStorage.getItem('access_token');
const getRefreshToken = () => localStorage.getItem('refresh_token');

// Function to store tokens in localStorage
const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

// Create an axios instance
const apiInstance = axios.create({
  baseURL: 'https://promptly-good-weasel.ngrok-free.app/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add the access token to the Authorization header
apiInstance.interceptors.request.use(
  (config) => {
    const accessToken = getAccessToken();
    console.log(accessToken)
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor for handling responses
apiInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Check for a 401 Unauthorized error and if the request hasn't been retried
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Prevent infinite retry loops

      try {
        // Get the refresh token from localStorage
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
          return Promise.reject(error); // No refresh token available, reject the error
        }

        // Attempt to refresh the token
        const refreshTokenResponse = await axios.post(
          'https://promptly-good-weasel.ngrok-free.app/api/v1/refresh-token',
          { refresh: refreshToken },
          { withCredentials: true }
        );

        // If refresh token is successful, update access token in localStorage and retry the original request
        if (refreshTokenResponse.status === 200 && refreshTokenResponse.data.access_token) {
          const newAccessToken = refreshTokenResponse.data.access_token;
          const newRefreshToken = refreshTokenResponse.data.refresh_token || refreshToken; // If new refresh token is provided, update it
          setTokens(newAccessToken, newRefreshToken);

          // Set the new access token in the Authorization header and retry the original request
          apiInstance.defaults.headers['Authorization'] = `Bearer ${newAccessToken}`;
          return apiInstance(originalRequest);
        } else {
          return Promise.reject(error);
        }
      } catch (e) {
        return Promise.reject(e);
      }
    } else {
      return Promise.reject(error);
    }
  }
);

export default apiInstance;
