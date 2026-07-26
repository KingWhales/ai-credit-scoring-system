import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export const submitApplication = (data) => api.post("/applications", data);
export const getApplications = () => api.get("/applications");
export const getApplication = (id) => api.get(`/applications/${id}`);
export const submitReview = (id, data) =>
  api.post(`/applications/${id}/review`, data);

export default api;
