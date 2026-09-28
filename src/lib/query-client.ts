import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2, // 2 minutes cache validity
      refetchOnWindowFocus: false,
      retry: (failureCount, error: any) => {
        // Don't retry on client errors (401, 403, 404)
        if (error?.response?.status && [401, 403, 404].includes(error.response.status)) {
          return false;
        }
        return failureCount < 2;
      },
    },
    mutations: {
      retry: 1,
    },
  },
});
