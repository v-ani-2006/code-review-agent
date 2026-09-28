import { useQuery } from "@tanstack/react-query";
import { historyService } from "@/services/history-service";

export function useHistory(params: {
  page?: number;
  page_size?: number;
  search?: string;
  language?: string;
  favorite_only?: boolean;
} = {}) {
  const historyQuery = useQuery({
    queryKey: ["history", params],
    queryFn: () => historyService.getHistory(params),
  });

  return {
    items: historyQuery.data?.items || [],
    total: historyQuery.data?.total || 0,
    page: historyQuery.data?.page || 1,
    totalPages: historyQuery.data?.total_pages || 1,
    isLoading: historyQuery.isLoading,
    refetch: historyQuery.refetch,
  };
}
