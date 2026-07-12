import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MediaLens - Bibliothèque Culturelle IA",
  description: "Plateforme immersive pour explorer des livres, films et jeux vidéo à l'aide de l'intelligence artificielle.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#050811] text-[#f8fafc]">
        {children}
      </body>
    </html>
  );
}
