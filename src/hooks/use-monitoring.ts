import { useQuery } from "@tanstack/react-query";
import { monitoringService } from "@/services/monitoring-service";

export function useMonitoring() {
  const healthQuery = useQuery({
    queryKey: ["monitoring", "health"],
    queryFn: () => monitoringService.getHealth(),
    refetchInterval: 10000, // Poll every 10 seconds for real-time status
  });

  const versionQuery = useQuery({
    queryKey: ["monitoring", "version"],
    queryFn: () => monitoringService.getVersion(),
  });

  const metricsQuery = useQuery({
    queryKey: ["monitoring", "metrics"],
    queryFn: () => monitoringService.getSystemMetrics(),
    refetchInterval: 10000,
  });

  return {
    health: healthQuery.data,
    isLoadingHealth: healthQuery.isLoading,
    version: versionQuery.data,
    metrics: metricsQuery.data,
    refetch: () => {
      healthQuery.refetch();
      metricsQuery.refetch();
    },
  };
}
