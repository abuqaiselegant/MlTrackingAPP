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
import { TrendingUp, Database, Tags, ArrowRight, Search } from 'lucide-react';

const QUICKSTART = `from mltracker import tracker

tracker.start("My Cool Model", learning_rate=0.001)
for epoch in range(50):
    tracker.log("loss", train_step(), step=epoch)
tracker.save_model("model.pkl")
tracker.finish()`;

function StatCallout({ value, label }: { value: number | string; label: string }) {
  return (
    <div>
      <div className="stat-callout text-4xl sm:text-5xl">{value}</div>
      <div className="eyebrow mt-2">{label}</div>
    </div>
  );
}

export default function DashboardPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'status' | 'name'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const { data: experiments, isLoading, error } = useQuery({
    queryKey: ['experiments', page, statusFilter],
    queryFn: () => getExperiments(page, statusFilter),
  });

  const handleSort = (field: 'date' | 'status' | 'name') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const stats = useMemo(() => {
    const list = experiments ?? [];
    return {
      total: list.length,
      running: list.filter((e) => e.status === 'running').length,
      completed: list.filter((e) => e.status === 'completed').length,
    };
  }, [experiments]);

  const filteredExperiments = useMemo(() => {
    if (!experiments) return experiments;

    let filtered = experiments;
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = experiments.filter(
        (exp) =>
          exp.name.toLowerCase().includes(query) ||
          exp.id.toString().includes(query) ||
          (exp.tags && exp.tags.some((tag) => tag.toLowerCase().includes(query)))
      );
    }

    const sorted = [...filtered].sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'date':
          comparison =
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
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

  const isEmpty = !isLoading && !error && experiments && experiments.length === 0;

  return (
    <div className="space-y-24">
      {/* Hero band */}
      <section className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div>
          <span className="badge-yellow">Experiment Tracking</span>
          <h1 className="mt-6 text-4xl font-bold leading-[1.05] tracking-[-0.02em] text-on-dark sm:text-6xl">
            Track every training run.
            <br />
            <span className="text-brand-yellow">Compare what matters.</span>
          </h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-body">
            Log hyperparameters, time-series metrics, and model artifacts from any
            Python project in four lines of code — then browse and compare them here.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/experiments/new">
              <Button size="lg">
                Create experiment
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/integration">
              <Button variant="secondary" size="lg">
                View integration
              </Button>
            </Link>
          </div>

          <div className="mt-12 flex gap-12">
            <StatCallout value={stats.total} label="Experiments" />
            <StatCallout value={stats.running} label="Running" />
            <StatCallout value={stats.completed} label="Completed" />
          </div>
        </div>

        {/* Code-window hero artifact */}
        <div className="code-window">
          <div className="code-window__bar">
            <span className="code-window__dot bg-[#ff5f56]" />
            <span className="code-window__dot bg-[#ffbd2e]" />
            <span className="code-window__dot bg-[#27c93f]" />
            <span className="ml-2 text-xs text-muted-foreground">train.py</span>
          </div>
          <pre className="overflow-x-auto p-6 text-[13px] leading-relaxed text-body-strong">
            <code>{QUICKSTART}</code>
          </pre>
          <div className="flex items-center justify-between border-t border-hairline px-6 py-3 text-xs text-muted-soft">
            <span>Python · requests only</span>
            <span className="text-success">● connected</span>
          </div>
        </div>
      </section>

      {/* Empty-state feature cards */}
      {isEmpty && (
        <section className="space-y-8">
          <div className="grid gap-4 md:grid-cols-3">
            {[
              {
                icon: TrendingUp,
                title: 'Track metrics',
                body: 'Log and visualize model performance over time with interactive charts.',
              },
              {
                icon: Database,
                title: 'Store artifacts',
                body: 'Upload and manage model files, datasets, and other run artifacts.',
              },
              {
                icon: Tags,
                title: 'Organize with tags',
                body: 'Categorize experiments with custom tags and find them with search.',
              },
            ].map(({ icon: Icon, title, body }) => (
              <div
                key={title}
                className="rounded-[12px] border border-hairline bg-surface-card p-8"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-md bg-brand-yellow">
                  <Icon className="h-5 w-5 text-[#0a0a0a]" />
                </div>
                <h3 className="mt-5 text-base font-semibold text-on-dark">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
              </div>
            ))}
          </div>

          <div className="cta-band flex flex-col items-start justify-between gap-6 p-8 sm:flex-row sm:items-center sm:p-10">
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-[#0a0a0a] sm:text-3xl">
                No experiments yet.
              </h2>
              <p className="mt-2 max-w-md text-sm text-[#0a0a0a]/70">
                Create your first experiment from the dashboard, or wire up the Python
                client and it will appear here automatically.
              </p>
            </div>
            <Link href="/experiments/new">
              <button className="inline-flex h-11 items-center gap-2 rounded-md bg-[#0a0a0a] px-6 text-sm font-semibold text-brand-yellow transition-colors hover:bg-[#1a1a1a]">
                Get started
                <ArrowRight className="h-4 w-4" />
              </button>
            </Link>
          </div>
        </section>
      )}

      {/* Experiments table */}
      <section>
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <span className="eyebrow">All runs</span>
            <h2 className="mt-2 text-2xl font-bold tracking-tight text-on-dark">
              Experiments
            </h2>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-soft" />
              <Input
                placeholder="Search experiments..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 sm:w-[260px]"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full bg-surface-card sm:w-[170px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All status</SelectItem>
                <SelectItem value="running">Running</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {isLoading ? (
          <div className="rounded-[12px] border border-hairline bg-surface-card py-16 text-center text-sm text-muted-foreground">
            Loading experiments...
          </div>
        ) : error ? (
          <div className="rounded-[12px] border border-destructive/30 bg-destructive/5 py-16 text-center text-sm text-[#ff8a8a]">
            Error loading experiments. Make sure the API is running at{' '}
            <code className="font-mono">
              {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
            </code>
          </div>
        ) : filteredExperiments ? (
          <>
            <ExperimentsTable
              experiments={filteredExperiments}
              sortBy={sortBy}
              sortOrder={sortOrder}
              onSort={handleSort}
            />
            <div className="mt-4 flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">Page {page}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={!experiments || experiments.length < 20}
              >
                Next
              </Button>
            </div>
          </>
        ) : null}
      </section>
    </div>
  );
}
