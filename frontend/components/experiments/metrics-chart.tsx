'use client';

import { useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import html2canvas from 'html2canvas';
import { Download } from 'lucide-react';
import type { Metric } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface MetricsChartProps {
  metrics: Metric[];
}

export function MetricsChart({ metrics }: MetricsChartProps) {
  const chartRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});

  if (metrics.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No metrics data available
      </div>
    );
  }

  const handleExportChart = async (metricName: string) => {
    const chartElement = chartRefs.current[metricName];
    if (!chartElement) return;

    try {
      const canvas = await html2canvas(chartElement, {
        backgroundColor: '#ffffff',
        scale: 2,
      });
      
      const link = document.createElement('a');
      link.download = `${metricName}-chart.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('Failed to export chart:', error);
    }
  };

  // Group metrics by metric_name
  const metricsByName = metrics.reduce((acc, metric) => {
    if (!acc[metric.metric_name]) {
      acc[metric.metric_name] = [];
    }
    acc[metric.metric_name].push(metric);
    return acc;
  }, {} as Record<string, Metric[]>);

  const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

  return (
    <div className="space-y-6">
      {Object.entries(metricsByName).map(([metricName, metricData], index) => {
        // Sort by step and transform for recharts
        const chartData = metricData
          .sort((a, b) => a.step - b.step)
          .map(m => ({
            step: m.step,
            value: m.value,
          }));

        return (
          <Card key={metricName} ref={(el) => { chartRefs.current[metricName] = el; }}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg capitalize">{metricName}</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExportChart(metricName)}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="step" 
                    label={{ value: 'Step', position: 'insideBottom', offset: -5 }}
                    className="text-sm"
                  />
                  <YAxis 
                    label={{ value: 'Value', angle: -90, position: 'insideLeft' }}
                    className="text-sm"
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--background))', 
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-2 text-sm text-muted-foreground text-center">
                {chartData.length} data points
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
