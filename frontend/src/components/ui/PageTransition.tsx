"use client";

import React from "react";
import { motion } from "framer-motion";
import { useSettings } from "@/components/layout/SettingsProvider";

export const PageTransition: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { reducedMotion } = useSettings();
  
  if (reducedMotion) {
    return <div className="w-full animate-fade-in">{children}</div>;
  }
  
  return (
    <motion.div
      className="w-full"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.24, ease: [0.4, 0, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
};
export default PageTransition;
