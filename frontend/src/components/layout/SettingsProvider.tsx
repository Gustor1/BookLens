"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface SettingsContextType {
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light") => void;
  reducedMotion: boolean;
  setReducedMotion: (val: boolean) => void;
  resetAll: () => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<"dark" | "light">("dark");
  const [reducedMotion, setReducedMotionState] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedTheme = localStorage.getItem("medialens_theme");
      if (savedTheme === "light" || savedTheme === "dark") {
        setThemeState(savedTheme);
      }
      
      const savedMotion = localStorage.getItem("medialens_reduced_motion");
      if (savedMotion !== null) {
        setReducedMotionState(savedMotion === "true");
      } else {
        const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
        setReducedMotionState(mediaQuery.matches);
      }
    }
  }, []);

  const setTheme = (newTheme: "dark" | "light") => {
    setThemeState(newTheme);
    localStorage.setItem("medialens_theme", newTheme);
    
    const root = window.document.documentElement;
    if (newTheme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  };

  const setReducedMotion = (val: boolean) => {
    setReducedMotionState(val);
    localStorage.setItem("medialens_reduced_motion", String(val));
    
    const root = window.document.documentElement;
    if (val) {
      root.setAttribute("data-reduced-motion", "true");
    } else {
      root.removeAttribute("data-reduced-motion");
    }
  };

  const resetAll = () => {
    setTheme("dark");
    setReducedMotion(false);
    localStorage.removeItem("medialens_theme");
    localStorage.removeItem("medialens_reduced_motion");
    localStorage.removeItem("medialens_favorites");
    if (typeof window !== "undefined") {
      window.location.reload();
    }
  };

  return (
    <SettingsContext.Provider value={{ theme, setTheme, reducedMotion, setReducedMotion, resetAll }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
};
