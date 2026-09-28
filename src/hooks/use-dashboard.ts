import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "@/services/dashboard-service";

export function useDashboard() {
  const statsQuery = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: () => dashboardService.getStats(),
  });

  const recentReviewsQuery = useQuery({
    queryKey: ["dashboard", "recent"],
    queryFn: () => dashboardService.getRecentReviews(),
  });

  const activityFeedQuery = useQuery({
    queryKey: ["dashboard", "activity"],
    queryFn: () => dashboardService.getActivityFeed(),
  });

  return {
    stats: statsQuery.data,
    isLoadingStats: statsQuery.isLoading,
    recentReviews: recentReviewsQuery.data || [],
    isLoadingRecent: recentReviewsQuery.isLoading,
    activityFeed: activityFeedQuery.data || [],
    refetch: () => {
      statsQuery.refetch();
      recentReviewsQuery.refetch();
      activityFeedQuery.refetch();
    },
  };
}
