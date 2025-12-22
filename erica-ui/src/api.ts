import axios from "axios";

export const API_BASE =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function askErica(question: string) {
  const res = await axios.post(`${API_BASE}/ask`, { question });
  return res.data;
}
