import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  // baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const getKey = () => localStorage.getItem("kai_key") || "";
export const setKey = (k) => localStorage.setItem("kai_key", k);
export const clearKey = () => localStorage.removeItem("kai_key");

export async function verifyKey(key) {
  const endpoint = `${api.defaults.baseURL}/auth/`;
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "X-Kai-Key": key },
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Streams chat responses from the Django backend streaming endpoint.
 *
 * @param {string} prompt - The user prompt
 * @param {function} onChunk - Callback executed every time a new text chunk arrives
 * @param {object} [signal] - Optional AbortSignal to support stopping/cancelling the request
 * @returns {Promise<string>} - Resolves with the complete final response text
 */

export async function streamChatResponse(prompt, onChunk, signal) {
  const endpoint = `${api.defaults.baseURL}/send/`;

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Kai-Key": getKey() },
      body: JSON.stringify({ prompt }),
      signal,
    });
    if (response.status === 401) {
      clearKey();
      window.dispatchEvent(new Event("kai-unauthorized"));
      throw new Error("Unauthorized");
    }
    if (!response.ok) {
      throw new Error(
        `Server error: ${response.status} ${response.statusText}`,
      );
    }
    if (!response.body) {
      throw new Error("Response body is missing (streaming not supported).");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let accumulatedText = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      accumulatedText += chunk;

      if (onChunk) {
        onChunk(accumulatedText, chunk);
      }
    }

    return accumulatedText;
  } catch (error) {
    if (error.name === "AbortError") {
      console.log("Stream generation stopped by user.");
      return "";
    }
    console.error("Streaming error:", error);
    throw error;
  }
}

export default api;
