export interface SubsystemHealth {
  status: "healthy" | "degraded" | "unhealthy";
  latency_ms?: number;
  message?: string;
  details?: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  api_status: string;
  application: string;
  app_name: string;
  version: string;
  environment: string;
  uptime: string;
  timestamp: string;
  ai_provider: string;
  database: SubsystemHealth;
  redis: SubsystemHealth;
  gemini: SubsystemHealth;
  storage: SubsystemHealth;
}

export interface SystemMetrics {
  cpu_usage_percent: number;
  memory_used_mb: number;
  memory_total_mb: number;
  memory_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  active_requests: number;
}
