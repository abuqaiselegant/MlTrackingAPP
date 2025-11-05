import axios from 'axios';
import type {
  Experiment,
  Metric,
  MetricsSummary,
  Artifact,
  CreateExperimentRequest,
  UpdateStatusRequest,
  UpdateTagsRequest,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Experiments
export const getExperiments = async (
  page: number = 1,
  status?: string
): Promise<Experiment[]> => {
  const params: Record<string, number | string> = { skip: (page - 1) * 20, limit: 20 };
  if (status && status !== 'all') {
    params.status = status;
  }
  const response = await api.get('/experiments', { params });
  return response.data;
};

export const getExperiment = async (id: string): Promise<Experiment> => {
  const response = await api.get(`/experiments/${id}`);
  return response.data;
};

export const createExperiment = async (
  data: CreateExperimentRequest
): Promise<Experiment> => {
  const response = await api.post('/experiments', data);
  return response.data;
};

export const updateExperimentStatus = async (
  id: string,
  status: UpdateStatusRequest['status']
): Promise<Experiment> => {
  const response = await api.put(`/experiments/${id}/status`, { status });
  return response.data;
};

export const updateExperimentTags = async (
  id: string,
  tags: string[]
): Promise<Experiment> => {
  const response = await api.put(`/experiments/${id}/tags`, { tags });
  return response.data;
};

export const deleteExperiment = async (id: string): Promise<void> => {
  await api.delete(`/experiments/${id}`);
};

// Metrics
export const getMetrics = async (
  experimentId: string,
  metricName?: string
): Promise<Metric[]> => {
  const params = metricName ? { metric_name: metricName } : {};
  const response = await api.get(`/experiments/${experimentId}/metrics`, { params });
  return response.data;
};

export const getMetricsSummary = async (
  experimentId: string
): Promise<MetricsSummary[]> => {
  const response = await api.get(`/experiments/${experimentId}/metrics/summary`);
  return response.data;
};

export const logMetrics = async (
  experimentId: string,
  metrics: Array<{ step: number; metric_name: string; value: number }>
): Promise<void> => {
  await api.post(`/experiments/${experimentId}/metrics`, { metrics });
};

// Artifacts
export const getArtifacts = async (experimentId: string): Promise<Artifact[]> => {
  const response = await api.get(`/artifacts/experiments/${experimentId}`);
  return response.data;
};

export const downloadArtifact = async (artifactId: string): Promise<Blob> => {
  const response = await api.get(`/artifacts/${artifactId}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

export const uploadArtifact = async (
  experimentId: string,
  file: File
): Promise<Artifact> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(
    `/artifacts/experiments/${experimentId}/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

export const deleteArtifact = async (artifactId: string): Promise<void> => {
  await api.delete(`/artifacts/${artifactId}`);
};
