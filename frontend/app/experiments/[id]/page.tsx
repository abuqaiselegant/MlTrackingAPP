'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import Link from 'next/link';
import { getExperiment, getMetrics, getArtifacts, updateExperimentStatus, updateExperimentTags, downloadArtifact } from '@/lib/api';
import { StatusBadge } from '@/components/experiments/status-badge';
import { MetricsChart } from '@/components/experiments/metrics-chart';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export default function ExperimentDetailPage() {
  const params = useParams();
  const queryClient = useQueryClient();
  const experimentId = params.id as string;
  const [newTag, setNewTag] = useState('');

  const { data: experiment, isLoading: expLoading } = useQuery({
    queryKey: ['experiment', experimentId],
    queryFn: () => getExperiment(experimentId),
  });

  const { data: metrics = [], isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics', experimentId],
    queryFn: () => getMetrics(experimentId),
    enabled: !!experimentId,
  });

  const { data: artifacts = [], isLoading: artifactsLoading } = useQuery({
    queryKey: ['artifacts', experimentId],
    queryFn: () => getArtifacts(experimentId),
    enabled: !!experimentId,
  });

  const statusMutation = useMutation({
    mutationFn: (status: 'running' | 'completed' | 'failed') =>
      updateExperimentStatus(experimentId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] });
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
    },
  });

  const tagsMutation = useMutation({
    mutationFn: (tags: string[]) => updateExperimentTags(experimentId, tags),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] });
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
      setNewTag('');
    },
  });

  const handleAddTag = () => {
    if (newTag.trim() && experiment) {
      const updatedTags = [...(experiment.tags || []), newTag.trim()];
      tagsMutation.mutate(updatedTags);
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    if (experiment) {
      const updatedTags = experiment.tags.filter(tag => tag !== tagToRemove);
      tagsMutation.mutate(updatedTags);
    }
  };

  const handleDownload = async (artifactId: string, filename: string) => {
    try {
      const blob = await downloadArtifact(artifactId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  if (expLoading) {
    return <div className="text-center py-8">Loading experiment...</div>;
  }

  if (!experiment) {
    return <div className="text-center py-8">Experiment not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/" className="text-sm text-muted-foreground hover:underline mb-2 inline-block">
            ← Back to experiments
          </Link>
          <h1 className="text-3xl font-bold tracking-tight">{experiment.name}</h1>
          <p className="text-muted-foreground">
            Created {new Date(experiment.created_at).toLocaleString()}
          </p>
        </div>
        <StatusBadge 
          status={experiment.status}
          onStatusChange={(newStatus) => statusMutation.mutate(newStatus)}
          disabled={statusMutation.isPending}
        />
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="artifacts">Artifacts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Experiment Details</CardTitle>
                <CardDescription>Basic information about this experiment</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Name</p>
                    <p className="text-lg font-semibold">{experiment.name}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Status</p>
                    <div className="mt-1">
                      <StatusBadge status={experiment.status} />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Created</p>
                    <p className="text-lg">{new Date(experiment.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Experiment ID</p>
                    <p className="text-sm font-mono text-muted-foreground">{experiment.id}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Hyperparameters</CardTitle>
                <CardDescription>Configuration used for this experiment</CardDescription>
              </CardHeader>
              <CardContent>
                {Object.keys(experiment.hyperparameters).length > 0 ? (
                  <div className="space-y-2">
                    {Object.entries(experiment.hyperparameters).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="font-medium">{key}</span>
                        <code className="text-sm bg-background px-2 py-1 rounded">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </code>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-4">No hyperparameters configured</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tags</CardTitle>
                <CardDescription>Organize and categorize your experiment</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add a tag..."
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                      disabled={tagsMutation.isPending}
                    />
                    <Button 
                      onClick={handleAddTag}
                      disabled={!newTag.trim() || tagsMutation.isPending}
                    >
                      Add
                    </Button>
                  </div>
                  
                  {experiment.tags && experiment.tags.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {experiment.tags.map((tag) => (
                        <Badge 
                          key={tag} 
                          variant="secondary"
                          className="px-3 py-1 cursor-pointer hover:bg-destructive hover:text-destructive-foreground"
                          onClick={() => handleRemoveTag(tag)}
                        >
                          {tag} ×
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground text-center py-4">No tags added yet</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="metrics">
          <Card>
            <CardHeader>
              <CardTitle>Metrics Visualization</CardTitle>
              <CardDescription>Training metrics over time</CardDescription>
            </CardHeader>
            <CardContent>
              {metricsLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Loading metrics...
                </div>
              ) : (
                <MetricsChart metrics={metrics} />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="artifacts">
          <Card>
            <CardHeader>
              <CardTitle>Artifacts</CardTitle>
              <CardDescription>Files associated with this experiment</CardDescription>
            </CardHeader>
            <CardContent>
              {artifactsLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Loading artifacts...
                </div>
              ) : artifacts.length === 0 ? (
                <p className="text-center py-8 text-muted-foreground">No artifacts uploaded</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Filename</TableHead>
                      <TableHead>Size</TableHead>
                      <TableHead>Uploaded</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {artifacts.map((artifact) => (
                      <TableRow key={artifact.id}>
                        <TableCell className="font-medium">{artifact.filename}</TableCell>
                        <TableCell>{(artifact.size_bytes / 1024).toFixed(2)} KB</TableCell>
                        <TableCell>{new Date(artifact.uploaded_at).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDownload(artifact.id, artifact.filename)}
                          >
                            Download
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
