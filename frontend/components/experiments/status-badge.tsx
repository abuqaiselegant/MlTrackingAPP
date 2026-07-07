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

const statusConfig = {
  running: {
    label: 'Running',
    dot: 'bg-success',
    className: 'border-success/30 bg-success/10 text-success',
  },
  completed: {
    label: 'Completed',
    dot: 'bg-info',
    className: 'border-info/30 bg-info/10 text-[#7cb0ff]',
  },
  failed: {
    label: 'Failed',
    dot: 'bg-destructive',
    className: 'border-destructive/30 bg-destructive/10 text-[#ff8a8a]',
  },
} as const;

function Pill({ status }: { status: Experiment['status'] }) {
  const config = statusConfig[status];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium',
        config.className
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full', config.dot)} />
      {config.label}
    </span>
  );
}

export function StatusBadge({ status, onStatusChange, disabled }: StatusBadgeProps) {
  if (!onStatusChange) {
    return <Pill status={status} />;
  }

  return (
    <Select
      value={status}
      onValueChange={(value) => onStatusChange(value as 'running' | 'completed' | 'failed')}
      disabled={disabled}
    >
      <SelectTrigger
        className={cn(
          'h-auto w-auto border-0 bg-transparent p-0 shadow-none hover:opacity-80 focus-visible:ring-0 [&>svg]:hidden',
          disabled && 'cursor-not-allowed opacity-50'
        )}
      >
        <span className="cursor-pointer">
          <Pill status={status} />
        </span>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="running">Running</SelectItem>
        <SelectItem value="completed">Completed</SelectItem>
        <SelectItem value="failed">Failed</SelectItem>
      </SelectContent>
    </Select>
  );
}
