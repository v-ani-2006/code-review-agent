"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="h-9 w-9 rounded-xl border border-border bg-secondary/50" />;
  }

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      type="button"
      className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
      title={`Switch to ${isDark ? "light" : "dark"} mode`}
    >
      {isDark ? (
        <Sun className="h-4 w-4 transition-transform hover:rotate-45" />
      ) : (
        <Moon className="h-4 w-4 transition-transform hover:-rotate-12" />
      )}
      <span className="sr-only">Toggle theme</span>
    </button>
  );
}
