'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { getExperiments } from '@/lib/api';
import { ExperimentsTable } from '@/components/experiments/experiments-table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Lightbulb, TrendingUp, Database, Tags, ChevronDown, ChevronUp } from 'lucide-react';

export default function DashboardPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'status' | 'name'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showHowItWorks, setShowHowItWorks] = useState(false);

  const { data: experiments, isLoading, error } = useQuery({
    queryKey: ['experiments', page, statusFilter],
    queryFn: () => getExperiments(page, statusFilter),
  });

  const handleSort = (field: 'date' | 'status' | 'name') => {
    if (sortBy === field) {
      // Toggle order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to descending
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  // Filter and sort experiments
  const filteredExperiments = useMemo(() => {
    if (!experiments) return experiments;
    
    // First, filter by search query
    let filtered = experiments;
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = experiments.filter((exp) => 
        exp.name.toLowerCase().includes(query) ||
        exp.id.toString().includes(query) ||
        (exp.tags && exp.tags.some(tag => tag.toLowerCase().includes(query)))
      );
    }

    // Then, sort
    const sorted = [...filtered].sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'date':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [experiments, searchQuery, sortBy, sortOrder]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Experiments</h1>
          <p className="text-muted-foreground">
            Track and monitor your machine learning experiments
          </p>
        </div>
        <Link href="/experiments/new">
          <Button>Create New Experiment</Button>
        </Link>
      </div>

      {/* Overview Section */}
      {(!experiments || experiments.length === 0) && !isLoading && (
        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-primary" />
              Welcome to ML Experiment Tracker
            </CardTitle>
            <CardDescription>
              A powerful platform to organize and monitor your machine learning experiments
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="flex gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <TrendingUp className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">Track Metrics</h3>
                  <p className="text-sm text-muted-foreground">
                    Log and visualize your model performance metrics over time with interactive charts
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <Database className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">Store Artifacts</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload and manage model files, datasets, and other experiment artifacts securely
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <Tags className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">Organize with Tags</h3>
                  <p className="text-sm text-muted-foreground">
                    Categorize experiments with custom tags and find them easily with powerful search
                  </p>
                </div>
              </div>
            </div>
            <div className="mt-6 rounded-lg border bg-card p-4">
              <button
                onClick={() => setShowHowItWorks(!showHowItWorks)}
                className="flex w-full items-center justify-between text-left transition-colors hover:text-primary"
              >
                <h4 className="font-semibold">How It Works:</h4>
                {showHowItWorks ? (
                  <ChevronUp className="h-5 w-5 text-muted-foreground" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-muted-foreground" />
                )}
              </button>
              {showHowItWorks && (
                <div className="mt-4 space-y-4">
                  <ol className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex gap-2">
                      <span className="font-semibold text-primary">1.</span>
                      <span>Create a new experiment with hyperparameters and optional tags</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold text-primary">2.</span>
                      <span>Log metrics during training using the API to track model performance</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold text-primary">3.</span>
                      <span>Upload artifacts like trained models, visualizations, or datasets</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold text-primary">4.</span>
                      <span>Compare experiments, export charts, and manage experiment status</span>
                    </li>
                  </ol>
                  <div>
                    <Link href="/experiments/new">
                      <Button className="w-full sm:w-auto">
                        Get Started - Create Your First Experiment
                      </Button>
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>All Experiments</CardTitle>
              <CardDescription>
                View and manage your experiment runs
              </CardDescription>
            </div>
            <div className="flex gap-3">
              <Input
                placeholder="Search experiments..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-[250px]"
              />
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="running">Running</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading experiments...
            </div>
          ) : error ? (
            <div className="text-center py-8 text-destructive">
              Error loading experiments. Make sure the API is running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
            </div>
          ) : filteredExperiments ? (
            <>
              <ExperimentsTable 
                experiments={filteredExperiments}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSort={handleSort}
              />
              <div className="flex items-center justify-between mt-4">
                <Button
                  variant="outline"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">Page {page}</span>
                <Button
                  variant="outline"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!experiments || experiments.length < 20}
                >
                  Next
                </Button>
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
