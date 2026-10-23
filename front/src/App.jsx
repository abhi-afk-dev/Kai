import "./App.css";
import Header from "./components/Header";
import Chat from "./components/Chat";
import {
  Routes,
  Route,
  Outlet,
  Navigate,
  useOutletContext,
  useLocation,
} from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import { FaBars } from "react-icons/fa";
export default function App() {
  return (
    <div className="relative h-screen w-full bg-[var(--app-panel)] overflow-hidden">
      <div
        aria-hidden="true"
        className="fixed inset-0 z-0 pointer-events-none"
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

      <div className="relative z-10 flex flex-col h-full">
        <Header />
        <Chat />
      </div>
    </div>
  );
}
