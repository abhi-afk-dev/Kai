import React, { useState, useRef, useEffect } from "react";
import { ImSpinner8 } from "react-icons/im";
import {
  PiPaperPlaneTiltFill,
  PiStopFill,
} from "react-icons/pi";

function Prompter({
  isLoading,
  isBusy,
  onStop,
  onSubmit
}) {
  const [localPrompt, setLocalPrompt] = useState("");
  const textareaRef = useRef(null);
  const prompterRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 100)}px`;
    }
  }, [localPrompt]);

  useEffect(() => {
    const handleViewportResize = () => {
      if (document.activeElement === textareaRef.current) {
        setTimeout(() => {
          prompterRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
          });
        }, 100);
      }
    };

    if (typeof window !== "undefined" && window.visualViewport) {
      window.visualViewport.addEventListener("resize", handleViewportResize);
      return () =>
        window.visualViewport.removeEventListener(
          "resize",
          handleViewportResize,
        );
    }
  }, []);

  const handleSend = () => {
    if ((!localPrompt.trim()) || isLoading) return;

    onSubmit(localPrompt, );
    setLocalPrompt("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      ref={prompterRef}
      className="group/prompter jet w-full max-w-5xl mb-16 sm:mb-0 scroll-m-16 px-4 py-3 sm:px-6 sm:py-4 bg-[var(--app-panel)] backdrop-blur-md border border-[var(--app-border)] shadow-2xl flex flex-col items-center gap-4 relative z-10 rounded-lg transition-transform"
    >
      <div className="flex items-end sm:items-center w-full gap-3">
        <textarea
          ref={textareaRef}
          value={localPrompt}
          onChange={(e) => setLocalPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            setTimeout(() => {
              prompterRef.current?.scrollIntoView({
                behavior: "smooth",
                block: "end",
              });
            }, 300);
          }}
          rows={1}
          placeholder="Tell me bud..."
          className="flex-1 min-w-0 max-h-28 sm:max-h-[200px] bg-transparent border-none outline-none text-[var(--app-text)] placeholder-[var(--app-text-muted)] text-base sm:text-lg py-3 sm:py-4 resize-none overflow-y-auto custom-scrollbar2"
          disabled={isLoading}
        />

        <button
          type="button"
          onClick={isBusy ? onStop : handleSend}
          disabled={!isLoading && !localPrompt.trim()}
          aria-label={isBusy ? "Stop" : "Send prompt"}
          title={isBusy ? "Stop" : "Send"}
          className="robotocondensed-text flex-shrink-0 p-3 sm:p-3 text-black transition-all hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center rounded-md"
        >
          <span className="text-[var(--app-text-dim)]">
            {isBusy ? (
              <PiStopFill size="26" />
            ) : isLoading ? (
              <ImSpinner8 className="animate-spin" size="26" />
            ) : (
              <PiPaperPlaneTiltFill
                size="26"
                className="transition-transform duration-300 hover:rotate-12 hover:scale-110"
              />
            )}
          </span>
        </button>
      </div>
    </div>
  );
}

export default Prompter;
