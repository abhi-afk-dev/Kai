import { useEffect, useState } from "react";
import "../App.css";
import Header from "../components/Header";
import Chat from "../components/Chat";

export default function Home() {
  const [viewportStyle, setViewportStyle] = useState({
    height: "100vh",
    top: "0px",
  });

  useEffect(() => {
    if (typeof window === "undefined" || !window.visualViewport) return;

    const handleResize = () => {
      setViewportStyle({
        height: `${window.visualViewport.height}px`,
        top: `${window.visualViewport.offsetTop}px`,
      });
      window.scrollTo(0, 0);
    };

    window.visualViewport.addEventListener("resize", handleResize);
    window.visualViewport.addEventListener("scroll", handleResize);

    handleResize();

    return () => {
      window.visualViewport.removeEventListener("resize", handleResize);
      window.visualViewport.removeEventListener("scroll", handleResize);
    };
  }, []);

  return (
    <div
      className="fixed left-0 w-full bg-[var(--app-panel)] flex flex-col overflow-hidden"
      style={{
        height: viewportStyle.height,
        top: viewportStyle.top,
      }}
    >
      <div
        aria-hidden="true"
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(var(--app-dot) 1.5px, transparent 1.5px)",
          backgroundSize: "28px 28px",
          backgroundPosition: "center top",
          maskImage: "linear-gradient(to bottom, black 40%, transparent 100%)",
          WebkitMaskImage:
            "linear-gradient(to bottom, black 40%, transparent 100%)",
        }}
      />

      <div className="relative z-50 flex-shrink-0 w-full bg-transparent">
        <Header />
      </div>

      <div className="relative z-10 flex-1 w-full min-h-0 overflow-hidden">
        <Chat />
      </div>
    </div>
  );
}
