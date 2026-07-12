"use client";

import React from "react";
import { Star, AlertCircle, X, Loader2 } from "lucide-react";

// Button Component
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "icon";
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "secondary",
  className = "",
  isLoading,
  ...props
}) => {
  const baseStyle = "inline-flex items-center justify-center font-medium rounded-lg text-sm px-4 py-2 transition-all focus:outline-none focus:ring-2 focus:ring-teal-500 disabled:opacity-50 disabled:pointer-events-none";
  const variants = {
    primary: "bg-teal-600 text-white hover:bg-teal-500 shadow-md hover:shadow-teal-500/20 active:scale-95",
    secondary: "bg-slate-900 border border-slate-800 text-slate-200 hover:bg-slate-800 hover:text-white active:scale-95",
    ghost: "text-slate-400 hover:text-white hover:bg-slate-900/50 active:scale-95",
    icon: "p-2 hover:bg-slate-900 text-slate-400 hover:text-white rounded-full active:scale-95"
  };

  return (
    <button className={`${baseStyle} ${variants[variant]} ${className}`} disabled={isLoading || props.disabled} {...props}>
      {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin text-teal-400" />}
      {children}
    </button>
  );
};

// IconButton Component
export interface IconButtonProps extends ButtonProps {
  icon: React.ReactNode;
  label: string;
}

export const IconButton: React.FC<IconButtonProps> = ({ icon, label, className = "", ...props }) => {
  return (
    <Button variant="icon" className={`w-10 h-10 ${className}`} aria-label={label} {...props}>
      {icon}
    </Button>
  );
};

// RatingBadge Component
export const RatingBadge: React.FC<{ rating: number; source?: string }> = ({ rating, source }) => {
  return (
    <div className="inline-flex items-center gap-1 bg-amber-500/10 border border-amber-500/20 text-amber-500 px-2 py-0.5 rounded text-xs font-semibold">
      <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
      <span>{rating.toFixed(1)}</span>
      {source && <span className="text-[10px] opacity-75 text-slate-400 font-normal ml-0.5">({source})</span>}
    </div>
  );
};

// SourceBadge Component
export const SourceBadge: React.FC<{ type: "books" | "movies" | "games" }> = ({ type }) => {
  const config = {
    books: { text: "Livre", bg: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" },
    movies: { text: "Film", bg: "bg-sky-500/10 border-sky-500/20 text-sky-400" },
    games: { text: "Jeu Vidéo", bg: "bg-indigo-500/10 border-indigo-500/20 text-indigo-400" }
  };
  const current = config[type] || config.books;
  return (
    <span className={`inline-flex items-center border px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide uppercase ${current.bg}`}>
      {current.text}
    </span>
  );
};

// TagChip Component
export const TagChip: React.FC<{ label: string; active?: boolean; onClick?: () => void }> = ({
  label,
  active,
  onClick
}) => {
  return (
    <button
      onClick={onClick}
      disabled={!onClick}
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-all ${
        onClick ? "cursor-pointer active:scale-95" : "cursor-default"
      } ${
        active
          ? "bg-teal-500/20 border border-teal-500 text-teal-400"
          : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
      }`}
    >
      {label}
    </button>
  );
};

// Skeleton Component
export const Skeleton: React.FC<{ className?: string }> = ({ className = "" }) => {
  return <div className={`animate-pulse bg-slate-900/80 rounded border border-slate-800/40 ${className}`} />;
};

// EmptyState Component
export const EmptyState: React.FC<{ title: string; description: string; actionLabel?: string; onAction?: () => void }> = ({
  title,
  description,
  actionLabel,
  onAction
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/20 max-w-md mx-auto">
      <AlertCircle className="w-12 h-12 text-slate-600 mb-4" />
      <h3 className="text-lg font-semibold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 mb-4">{description}</p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

// ErrorState Component
export const ErrorState: React.FC<{ title?: string; description?: string; onRetry?: () => void }> = ({
  title = "Erreur de chargement",
  description = "Nous n'avons pas réussi à récupérer les données.",
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center border border-red-500/10 rounded-xl bg-red-950/5 max-w-md mx-auto my-4">
      <AlertCircle className="w-10 h-10 text-red-500 mb-3" />
      <h3 className="text-md font-semibold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 mb-4">{description}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          Réessayer
        </Button>
      )}
    </div>
  );
};

// Toast Notification
export const Toast: React.FC<{ message: string; type?: "info" | "success" | "error"; onClose: () => void }> = ({
  message,
  type = "info",
  onClose
}) => {
  const styles = {
    info: "border-slate-800 bg-slate-950 text-slate-200",
    success: "border-teal-500/30 bg-slate-950 text-teal-400",
    error: "border-red-500/30 bg-slate-950 text-red-400"
  };

  return (
    <div className={`fixed bottom-20 right-4 md:bottom-6 md:right-6 flex items-center gap-3 border p-4 rounded-xl shadow-2xl backdrop-blur-md z-50 transition-all ${styles[type]}`}>
      <span className="text-sm font-medium">{message}</span>
      <button onClick={onClose} aria-label="Close message" className="p-1 hover:bg-slate-900 rounded-full text-slate-500 hover:text-white transition-all">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
