import React, { useState, useEffect } from "react";
import { Moon, Sun } from "lucide-react";

function Header() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("kai-theme") || "dark";
  });

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    localStorage.setItem("kai-theme", nextTheme);
  };

  return (
    <div className="flex jet border-b border-[var(--app-border)] w-full items-center text-[var(--app-text)] hover:bg-[var(--app-hover)] cursor-pointer transition-all duration-300 select-none justify-between py-4 px-10">
      <a href="/"
        className="bungee-text text-[var(--app-text)] text-2xl flex items-center gap-2">
        <span className="w-[26px] h-[26px] flex items-center justify-center border-2 border-[var(--app-text)] rounded-md text-[var(--app-text)] text-[13px] font-extrabold">
          魁
        </span>

        <div className="overflow-hidden transition-all duration-300 ease-in-out w-24 opacity-100">
          <h1>Kai</h1>
        </div>
      </a>

      <button
        onClick={toggleTheme}
        aria-label="Toggle theme"
        className="p-1.5 text-[var(--app-text-muted)] hover:text-[var(--app-text)] transition-colors rounded-md hover:bg-[var(--app-overlay)] cursor-pointer"
      >
        {theme === "dark" ? (
          <Sun className="w-4 h-4" />
        ) : (
          <Moon className="w-4 h-4" />
        )}
      </button>
    </div>
  );
}

export default Header;
