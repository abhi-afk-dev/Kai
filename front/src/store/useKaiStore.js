import { create } from "zustand";
import { streamChatResponse } from "../api";

export const useKaiStore = create((set, get) => ({
  messages: [],
  isLoading: false,
  isBusy: false,
  agentStatus: "Initializing sequence...",
  currentAbortController: null,

  sendMessage: async (prompt, image = null) => {
    if (!prompt?.trim() || get().isLoading) return;

    const abortController = new AbortController();

    set((state) => ({
      isLoading: true,
      isBusy: true,
      agentStatus: "Evaluating routing tier & executing...",
      currentAbortController: abortController,
      messages: [
        ...state.messages,
        { role: "user", content: prompt, image, timestamp: Date.now() },
        { role: "ai", content: "", isStreaming: true, timestamp: Date.now() },
      ],
    }));

    try {
      await streamChatResponse(
        prompt,
        (fullText) => {
          set((state) => {
            const newMessages = [...state.messages];
            const lastMsg = newMessages[newMessages.length - 1];
            if (lastMsg && lastMsg.role === "ai") {
              lastMsg.content = fullText;
            }
            return { messages: newMessages };
          });
        },
        abortController.signal,
      );
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Chat streaming failed:", err);
        set((state) => {
          const newMessages = [...state.messages];
          const lastMsg = newMessages[newMessages.length - 1];
          if (lastMsg && lastMsg.role === "ai") {
            lastMsg.content =
              "❌ Sorry, Kai encountered an error while processing your request.";
          }
          return { messages: newMessages };
        });
      }
    } finally {
      set((state) => {
        const newMessages = [...state.messages];
        const lastMsg = newMessages[newMessages.length - 1];
        if (lastMsg && lastMsg.role === "ai") {
          lastMsg.isStreaming = false;
        }
        return {
          isLoading: false,
          isBusy: false,
          currentAbortController: null,
          agentStatus: "",
        };
      });
    }
  },

  stopMessage: () => {
    const { currentAbortController } = get();
    if (currentAbortController) {
      currentAbortController.abort();
      set({
        isLoading: false,
        isBusy: false,
        currentAbortController: null,
        agentStatus: "",
      });
    }
  },

  clearMessages: () => set({ messages: [] }),
}));
