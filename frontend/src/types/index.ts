export interface Article {
  title: string;
  url: string;
  screenshot: string | null;
  status: 'success' | 'failed' | 'processing' | 'screenshot_failed';
  summary: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface CacheStatus {
  total_articles: number;
  latest_update: string | null;
  successful_articles: number;
  is_fresh: boolean;
}

export interface ApiResponse {
  articles?: Article[];
  cache_status?: CacheStatus;
  total?: number;
  status?: string;
  message?: string;
  estimated_completion?: string;
}

export interface RefreshStatus {
  isRefreshing: boolean;
  lastRefresh: Date | null;
  error: string | null;
}