"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { Toaster } from "sonner";
import { queryClient } from "@/lib/query-client";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
      <QueryClientProvider client={queryClient}>
        {children}
        <Toaster position="top-right" richColors closeButton theme="dark" />
      </QueryClientProvider>
    </NextThemesProvider>
  );
}
