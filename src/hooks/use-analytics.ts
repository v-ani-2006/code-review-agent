import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "@/services/analytics-service";

export function useAnalytics(days = 30) {
  const summaryQuery = useQuery({
    queryKey: ["analytics", "summary", days],
    queryFn: () => analyticsService.getSummary(days),
  });

  return {
    data: summaryQuery.data,
    isLoading: summaryQuery.isLoading,
    isError: summaryQuery.isError,
    refetch: summaryQuery.refetch,
  };
}
