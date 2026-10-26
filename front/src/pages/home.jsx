import "../App.css";
import Header from "../components/Header";
import Chat from "../components/Chat";

export default function Home() {
  return (
    <div className="relative h-[100dvh] w-full bg-[var(--app-panel)] flex flex-col overflow-hidden">
      {/* Background Dots Layer */}
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

      {/* Sticky Header Layer */}
      <div className="relative z-50 flex-shrink-0 w-full bg-transparent">
        <Header />
      </div>

      {/* Chat Component Layer (Takes up remaining height) */}
      <div className="relative z-10 flex-1 w-full h-full overflow-hidden">
        <Chat />
      </div>
    </div>
  );
}
