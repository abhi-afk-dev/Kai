import axios from "axios";

KAI_KEY = import.meta.env.KAI_KEY;

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  // baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
    "X-Kai-Key": KAI_KEY,
  },
});

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
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
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
