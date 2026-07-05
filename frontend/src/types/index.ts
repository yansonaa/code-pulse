export interface Commit {
  id: number;
  commit_hash: string;
  author: string;
  email?: string;
  date: string;
  message?: string;
  additions: number;
  deletions: number;
  files_changed: number;
  review_comments_count: number;
  is_automated: boolean;
  repository?: string;
  branch?: string;
}

export interface KPIResponse {
  total_commits: number;
  net_lines: number;
  active_developers: number;
  avg_review_response_hours: number;
  period_days: number;
}

export interface TrendPoint {
  date: string;
  count: number;
  additions: number;
  deletions: number;
}

export interface TrendResponse {
  data: TrendPoint[];
  has_decline: boolean;
  decline_dates: string[];
}

export interface CodeStats {
  author: string;
  additions: number;
  deletions: number;
  net: number;
  commits: number;
}

export interface HeatmapPoint {
  day: number;
  hour: number;
  count: number;
}

export interface HeatmapResponse {
  data: HeatmapPoint[];
  max_count: number;
  anomalies: Array<{
    day: number;
    hour: number;
    count: number;
    type: string;
    description: string;
  }>;
}

export interface RadarDimension {
  dimension: string;
  value: number;
  full_mark: number;
}

export interface MemberRadar {
  author: string;
  dimensions: RadarDimension[];
}

export interface AnomalyReport {
  author: string;
  anomaly_type: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  details: Record<string, number>;
}

export interface RepositoryConfig {
  id: number;
  name: string;
  repo_type: 'local' | 'github' | 'gitlab';
  local_path?: string;
  remote_url?: string;
  access_token?: string;
  branch?: string;
  is_active: boolean;
  auto_sync: boolean;
  last_sync_at?: string;
  created_at: string;
  updated_at: string;
}

export interface SyncResult {
  success: boolean;
  message: string;
  imported_count: number;
  repo_name?: string;
  branch?: string;
}

export interface FilterState {
  startDate: string;
  endDate: string;
  authors: string[];
  repositories: string[];
  search: string;
}
