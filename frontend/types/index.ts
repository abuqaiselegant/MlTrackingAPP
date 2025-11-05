export interface Experiment {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed';
  hyperparameters: Record<string, any>;
  tags: string[];
  created_at: string;
}

export interface Metric {
  id: number;
  experiment_id: string;
  step: number;
  metric_name: string;
  value: number;
  timestamp: string;
}

export interface MetricsSummary {
  metric_name: string;
  min: number;
  max: number;
  avg: number;
  latest: number;
}

export interface Artifact {
  id: string;
  experiment_id: string;
  filename: string;
  size_bytes: number;
  uploaded_at: string;
}

export interface CreateExperimentRequest {
  name: string;
  hyperparameters: Record<string, any>;
  tags?: string[];
}

export interface UpdateStatusRequest {
  status: 'running' | 'completed' | 'failed';
}

export interface UpdateTagsRequest {
  tags: string[];
}
