import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from '@/components/ui/select';
import type { Experiment } from '@/types';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: Experiment['status'];
  onStatusChange?: (status: 'running' | 'completed' | 'failed') => void;
  disabled?: boolean;
}

export function StatusBadge({ status, onStatusChange, disabled }: StatusBadgeProps) {
  const statusConfig = {
    running: {
      variant: 'default' as const,
      className: 'bg-success text-success-foreground hover:bg-success/90 border-success',
      emoji: '🟢',
    },
    completed: {
      variant: 'default' as const,
      className: 'bg-info text-info-foreground hover:bg-info/90 border-info',
      emoji: '🔵',
    },
    failed: {
      variant: 'destructive' as const,
      className: '',
      emoji: '🔴',
    },
  } as const;

  const config = statusConfig[status];

  // If no onChange handler, render as plain badge
  if (!onStatusChange) {
    return (
      <Badge variant={config.variant} className={cn('capitalize', config.className)}>
        {status}
      </Badge>
    );
  }

  // Render as clickable dropdown
  return (
    <Select
      value={status}
      onValueChange={(value) => onStatusChange(value as 'running' | 'completed' | 'failed')}
      disabled={disabled}
    >
      <SelectTrigger 
        className={cn(
          'w-auto h-auto border-0 p-0 hover:opacity-80 focus:ring-0 focus:ring-offset-0',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <Badge variant={config.variant} className={cn('capitalize cursor-pointer', config.className)}>
          {status}
        </Badge>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="running">🟢 Running</SelectItem>
        <SelectItem value="completed">🔵 Completed</SelectItem>
        <SelectItem value="failed">🔴 Failed</SelectItem>
      </SelectContent>
    </Select>
  );
}

