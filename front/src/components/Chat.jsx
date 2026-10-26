import Prompter from "./Prompter";
import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../App.css";
import api from "../api";
import ChatEmptyState from "./ChatEmptyState";
import { useKaiStore } from "../store/useKaiStore";
function useIsNarrowViewport(breakpointPx = 768) {
  const [isNarrow, setIsNarrow] = useState(
    typeof window !== "undefined" ? window.innerWidth < breakpointPx : false,
  );

  useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${breakpointPx - 1}px)`);
    const handler = (e) => setIsNarrow(e.matches);
    mql.addEventListener("change", handler);
    setIsNarrow(mql.matches);
    return () => mql.removeEventListener("change", handler);
  }, [breakpointPx]);

  return isNarrow;
}

const normalizeContent = (text) => {
  if (!text) return "";
  let out = text;
  out = out.replace(/\\n/g, "\n");
  out = out.replace(/^```markdown\s*\n([\s\S]*?)\n?```\s*$/i, "$1");
  out = out.replace(/^```\s*\n([\s\S]*?)\n?```\s*$/i, "$1");
  out = out.replace(/^```[a-z]*\s*\n([\s\S]*?)\n?```\s*$/i, "$1");
  return out.trim();
};

const aiMdComponents = {
  h1: ({ node, ...props }) => (
    <h1
      className="text-xl sm:text-2xl font-bold text-[var(--app-text)] mb-4 border-b border-[var(--app-border)] pb-2 font-sans"
      {...props}
    />
  ),
  h2: ({ node, ...props }) => (
    <h2
      className="text-lg sm:text-xl font-semibold text-[var(--app-text)] mb-3 mt-5 font-sans"
      {...props}
    />
  ),
  h3: ({ node, ...props }) => (
    <h3
      className="text-base sm:text-lg font-semibold text-[var(--app-text)] mb-2 mt-4 font-sans"
      {...props}
    />
  ),
  p: ({ node, ...props }) => (
    <p
      className="text-sm sm:text-base text-[var(--app-text-dim)] leading-relaxed font-sans"
      {...props}
    />
  ),
  ul: ({ node, ...props }) => (
    <ul
      className="list-disc list-outside ml-6 mb-3 space-y-1.5 font-sans text-sm sm:text-base text-[var(--app-text-dim)]"
      {...props}
    />
  ),
  ol: ({ node, ...props }) => (
    <ol
      className="list-decimal list-outside ml-6 mb-3 space-y-1.5 font-sans text-sm sm:text-base text-[var(--app-text-dim)]"
      {...props}
    />
  ),
  li: ({ node, ...props }) => (
    <li className="text-[var(--app-text-dim)] font-sans pl-1" {...props} />
  ),
  strong: ({ node, ...props }) => (
    <strong className="font-semibold text-[var(--app-text)]" {...props} />
  ),
  em: ({ node, ...props }) => (
    <em className="italic text-[var(--app-text-dim)]" {...props} />
  ),
  code: ({ node, inline, ...props }) =>
    inline ? (
      <code
        className="bg-[var(--app-overlay)] px-1.5 py-0.5 text-sm font-mono text-[var(--app-text-dim)] border border-[var(--app-border)] rounded-md break-words"
        {...props}
      />
    ) : (
      <code
        className="block bg-[var(--app-overlay)] p-4 text-sm font-mono text-[var(--app-text-dim)] border border-[var(--app-border)] overflow-x-auto"
        {...props}
      />
    ),
  pre: ({ node, ...props }) => (
    <pre
      className="bg-[var(--app-overlay)] border border-[var(--app-border)] mb-4 overflow-x-auto rounded-md max-w-full"
      style={{ fontFamily: "monospace" }}
      {...props}
    />
  ),
  blockquote: ({ node, ...props }) => (
    <blockquote
      className="border-l-4 border-zinc-600 pl-4 my-3 text-sm sm:text-base text-[var(--app-text-dim)] italic font-sans bg-[var(--app-overlay)] py-2 pr-2 rounded-r-md"
      {...props}
    />
  ),
  a: ({ node, ...props }) => (
    <a
      className="text-[var(--app-text-dim)] underline hover:text-[var(--app-text)] transition-colors break-words"
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    />
  ),
  hr: ({ node, ...props }) => (
    <hr className="border-[var(--app-border)] my-4" {...props} />
  ),

  table: ({ node, ...props }) => (
    <div className="overflow-x-auto w-full my-5 rounded-md border border-[var(--app-border)] custom-scrollbar">
      <table
        className="w-full text-left border-collapse text-sm sm:text-base font-sans min-w-[500px]"
        {...props}
      />
    </div>
  ),
  thead: ({ node, ...props }) => (
    <thead
      className="bg-[var(--app-panel-alt)] text-[var(--app-text)] border-b border-[var(--app-border)]"
      {...props}
    />
  ),
  tbody: ({ node, ...props }) => (
    <tbody className="divide-y divide-[var(--app-border)]" {...props} />
  ),
  tr: ({ node, ...props }) => (
    <tr className="hover:bg-[var(--app-hover)] transition-colors" {...props} />
  ),
  th: ({ node, ...props }) => (
    <th
      className="px-4 py-3 sm:px-5 sm:py-3.5 font-semibold border-r border-[var(--app-border)] last:border-r-0 whitespace-nowrap"
      {...props}
    />
  ),
  td: ({ node, ...props }) => (
    <td
      className="px-4 py-3 sm:px-5 sm:py-3.5 border-r border-[var(--app-border)] last:border-r-0 text-[var(--app-text-dim)] align-top"
      {...props}
    />
  ),
};

const userMdComponents = {
  h1: ({ node, ...props }) => (
    <h1 className="text-lg sm:text-xl font-bold mb-3 font-sans" {...props} />
  ),
  h2: ({ node, ...props }) => (
    <h2
      className="text-base sm:text-lg font-bold mb-2 mt-3 font-sans"
      {...props}
    />
  ),
  h3: ({ node, ...props }) => (
    <h3
      className="text-sm sm:text-base font-bold mb-1 mt-2 font-sans opacity-90"
      {...props}
    />
  ),
  p: ({ node, ...props }) => (
    <p
      className="text-base leading-relaxed mb-2 last:mb-0 font-sans"
      {...props}
    />
  ),
  ul: ({ node, ...props }) => (
    <ul
      className="list-disc list-outside ml-5 mb-2 space-y-1 font-sans text-base"
      {...props}
    />
  ),
  ol: ({ node, ...props }) => (
    <ol
      className="list-decimal list-outside ml-5 mb-2 space-y-1 font-sans text-base "
      {...props}
    />
  ),
  li: ({ node, ...props }) => <li className=" font-sans" {...props} />,
  strong: ({ node, ...props }) => <strong className="font-bold " {...props} />,
  em: ({ node, ...props }) => <em className="italic opacity-80" {...props} />,
  code: ({ node, inline, ...props }) =>
    inline ? (
      <code
        className="px-1.5 py-0.5 rounded-md text-sm font-mono bg-[var(--app-overlay)] border border-[var(--app-border)] break-words"
        {...props}
      />
    ) : (
      <code
        className="block p-4 rounded-md text-sm font-mono bg-[var(--app-overlay)] border border-[var(--app-border)] overflow-x-auto shadow-inner"
        {...props}
      />
    ),
  pre: ({ node, ...props }) => (
    <pre
      className="mb-3 overflow-x-auto custom-scrollbar max-w-full"
      style={{ fontFamily: "monospace" }}
      {...props}
    />
  ),
  blockquote: ({ node, ...props }) => (
    <blockquote
      className="border-l-[4px] border-[var(--app-accent-contrast)]/30 pl-3 my-2 opacity-90 italic font-sans"
      {...props}
    />
  ),
  a: ({ node, ...props }) => (
    <a
      className="font-medium underline hover:opacity-70 transition-opacity break-words"
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    />
  ),
  hr: ({ node, ...props }) => (
    <hr className="border-[var(--app-accent-contrast)]/20 my-3" {...props} />
  ),
};

const remarkPlugins = [remarkGfm];

const AgentResponse = ({ message }) => {
  const { meta } = message;
  const content = normalizeContent(message.content);
  const isNarrow = useIsNarrowViewport(768);

  return (
    <div className="flex flex-col gap-3 w-full px-1 sm:px-2 lg:px-0 lg:max-w-5xl animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="border border-[var(--app-border)] p-2 sm:p-2 shadow-lg rounded-md">
        <ReactMarkdown
          components={aiMdComponents}
          remarkPlugins={remarkPlugins}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
};

function Chat() {
  const bottomRef = useRef(null);
  const scrollContainerRef = useRef(null);

  const messages = useKaiStore((s) => s.messages);
  const isLoading = useKaiStore((s) => s.isLoading);
  const agentStatus = useKaiStore((s) => s.agentStatus);
  const sendMessage = useKaiStore((s) => s.sendMessage);
  const stopMessage = useKaiStore((s) => s.stopMessage);

  const scrollToBottom = () => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  const handleGenerate = (inputText) => {
    if (!inputText?.trim()) return;
    sendMessage(inputText);
  };

  return (
    <div className="w-full h-full flex flex-col min-h-0">
      <div
        ref={scrollContainerRef}
        className="flex-1 w-full overflow-y-auto custom-scrollbar p-3 sm:p-6"
      >
        <div className="flex text-[var(--app-text)] flex-col w-full max-w-7xl mx-auto gap-6 sm:gap-8">
          {messages.length === 0 && !isLoading && (
            <div className="mt-10 w-full flex items-center justify-center">
              <ChatEmptyState
                onPromptSelect={(prompt) => handleGenerate(prompt)}
              />
            </div>
          )}

          {messages.map((msg, idx) => {
            if (msg.role === "ai" && !msg.isStreaming && !msg.content?.trim()) {
              return null;
            }

            return (
              <div
                key={idx}
                className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "user" && (
                  <div className="flex flex-col items-end gap-2 max-w-[90%] sm:max-w-[75%]">
                    {msg.image && (
                      <img
                        src={msg.image}
                        className="w-40 sm:w-56 border border-[var(--app-border)] rounded-md"
                        alt="User upload"
                      />
                    )}
                    <div className="border border-[var(--app-border)] text-white px-5 py-1.5 sm:px-6 sm:py-2 text-base shadow-lg rounded-md break-words w-full">
                      <ReactMarkdown components={userMdComponents}>
                        {normalizeContent(msg.content)}
                      </ReactMarkdown>
                    </div>
                    <span className="text-xs text-[var(--app-text-muted)] mr-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                )}
                {msg.role === "ai" && (
                  <div className="flex gap-3 sm:gap-4 w-full max-w-[95%] sm:max-w-[90%] lg:max-w-[85%] animate-in fade-in">
                    {msg.isStreaming &&
                    (!msg.content || msg.content.trim() === "") ? (
                      <div className="bg-[var(--app-panel)] border border-[var(--app-border)] px-5 py-4 shadow-xl rounded-md flex items-center gap-2 mt-1 h-12">
                        <span
                          className="w-2 h-2 bg-[var(--app-text-muted)] rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        ></span>
                        <span
                          className="w-2 h-2 bg-[var(--app-text-muted)] rounded-full animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        ></span>
                        <span
                          className="w-2 h-2 bg-[var(--app-text-muted)] rounded-full animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        ></span>
                      </div>
                    ) : (
                      <AgentResponse message={msg} />
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {isLoading && !messages.some((m) => m.isStreaming) && (
            <div className="flex gap-3 sm:gap-4 w-full max-w-[95%] sm:max-w-[90%] lg:max-w-[85%] animate-in fade-in slide-in-from-bottom-2">
              <div className="bg-[var(--app-panel)] border border-[var(--app-border)] p-5 sm:p-6 shadow-2xl rounded-md w-full flex flex-col gap-4">
                <div className="flex items-center gap-3">
                  <div className="relative flex h-3.5 w-3.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--app-text-muted)] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-[var(--app-text-dim)]"></span>
                  </div>
                  <span className="text-[var(--app-text-dim)] text-sm font-mono uppercase tracking-wider font-semibold">
                    System Executing
                  </span>
                </div>
                <div className="text-[var(--app-text-dim)] font-mono text-sm bg-[var(--app-overlay)] p-4 border border-[var(--app-border)] rounded-md break-words">
                  <span className="text-[var(--app-text-muted)] mr-2">➜</span>
                  {agentStatus || "Initializing sequence..."}
                  <span className="animate-pulse ml-1">_</span>
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} className="h-1" />
        </div>
      </div>

      <div className="flex-shrink-0 w-full z-20 bg-gradient-to-t from-[var(--app-bg)] via-[var(--app-bg)]/95 to-transparent backdrop-blur-sm pt-2 pb-[env(safe-area-inset-bottom)] px-3 sm:px-6">
        <div className="w-full max-w-5xl mx-auto flex justify-center pb-2">
          <Prompter
            isLoading={isLoading}
            onStop={() => stopMessage()}
            onSubmit={handleGenerate}
            onFocus={scrollToBottom}
          />
        </div>
      </div>
    </div>
  );
}

export default Chat;
