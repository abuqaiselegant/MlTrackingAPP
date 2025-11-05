'use client';

import Link from 'next/link';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Trash2, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StatusBadge } from './status-badge';
import { updateExperimentStatus, deleteExperiment } from '@/lib/api';
import type { Experiment } from '@/types';

type SortField = 'name' | 'status' | 'date';
type SortOrder = 'asc' | 'desc';

interface ExperimentsTableProps {
  experiments: Experiment[];
  sortBy?: SortField;
  sortOrder?: SortOrder;
  onSort?: (field: SortField) => void;
}

function SortableHeader({ 
  field, 
  children, 
  sortBy, 
  sortOrder, 
  onSort 
}: { 
  field: SortField; 
  children: React.ReactNode;
  sortBy?: SortField;
  sortOrder?: SortOrder;
  onSort?: (field: SortField) => void;
}) {
  const getSortIcon = () => {
    if (sortBy !== field) return <ArrowUpDown className="ml-2 h-4 w-4" />;
    return sortOrder === 'asc' 
      ? <ArrowUp className="ml-2 h-4 w-4" />
      : <ArrowDown className="ml-2 h-4 w-4" />;
  };

  return (
    <TableHead>
      <Button
        variant="ghost"
        onClick={() => onSort?.(field)}
        className="h-auto p-0 hover:bg-transparent font-semibold"
      >
        {children}
        {getSortIcon()}
      </Button>
    </TableHead>
  );
}

export function ExperimentsTable({ experiments, sortBy, sortOrder, onSort }: ExperimentsTableProps) {
  const queryClient = useQueryClient();

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: 'running' | 'completed' | 'failed' }) =>
      updateExperimentStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteExperiment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
    },
  });

  const handleStatusChange = (experimentId: string, newStatus: string) => {
    statusMutation.mutate({ 
      id: experimentId, 
      status: newStatus as 'running' | 'completed' | 'failed' 
    });
  };

  const handleDelete = (experimentId: string, experimentName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete "${experimentName}"? This action cannot be undone.`)) {
      deleteMutation.mutate(experimentId);
    }
  };

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHeader field="name" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort}>
              Name
            </SortableHeader>
            <SortableHeader field="status" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort}>
              Status
            </SortableHeader>
            <TableHead>Tags</TableHead>
            <SortableHeader field="date" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort}>
              Created
            </SortableHeader>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {experiments.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                No experiments found
              </TableCell>
            </TableRow>
          ) : (
            experiments.map((experiment) => (
              <TableRow key={experiment.id} className="hover:bg-muted/50">
                <TableCell>
                  <Link
                    href={`/experiments/${experiment.id}`}
                    className="font-medium hover:underline"
                  >
                    {experiment.name}
                  </Link>
                </TableCell>
                <TableCell>
                  <StatusBadge 
                    status={experiment.status}
                    onStatusChange={(newStatus) => handleStatusChange(experiment.id, newStatus)}
                    disabled={statusMutation.isPending}
                  />
                </TableCell>
                <TableCell>
                  {experiment.tags && experiment.tags.length > 0 ? (
                    <div className="flex flex-wrap gap-1">
                      {experiment.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {experiment.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{experiment.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  ) : (
                    <span className="text-xs text-muted-foreground">No tags</span>
                  )}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {new Date(experiment.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => handleDelete(experiment.id, experiment.name, e)}
                    disabled={deleteMutation.isPending}
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
