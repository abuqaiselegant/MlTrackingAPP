'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { createExperiment } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function NewExperimentPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [hyperparameters, setHyperparameters] = useState('{}');
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: createExperiment,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
      router.push(`/experiments/${data.id}`);
    },
    onError: (error: Error) => {
      setError(error.message);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Experiment name is required');
      return;
    }

    let parsedParams = {};
    if (hyperparameters.trim()) {
      try {
        parsedParams = JSON.parse(hyperparameters);
      } catch {
        setError('Invalid JSON format for hyperparameters');
        return;
      }
    }

    mutation.mutate({
      name: name.trim(),
      hyperparameters: parsedParams,
      tags: tags,
    });
  };

  const handleAddTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Create New Experiment</h1>
        <p className="text-muted-foreground">
          Start tracking a new machine learning experiment
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Experiment Details</CardTitle>
          <CardDescription>
            Provide information about your experiment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Experiment Name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., ResNet-50 Training"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="hyperparameters">Hyperparameters (JSON)</Label>
              <textarea
                id="hyperparameters"
                value={hyperparameters}
                onChange={(e) => setHyperparameters(e.target.value)}
                placeholder='{"learning_rate": 0.001, "batch_size": 32}'
                className="w-full min-h-[100px] px-3 py-2 text-sm border rounded-md"
              />
              <p className="text-xs text-muted-foreground">
                Enter hyperparameters as JSON. Example: {`{"lr": 0.001, "batch_size": 32}`}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags (Optional)</Label>
              <div className="flex gap-2">
                <Input
                  id="tags"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                  placeholder="Add tags..."
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleAddTag}
                  disabled={!newTag.trim()}
                >
                  Add
                </Button>
              </div>
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {tags.map((tag) => (
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
              )}
            </div>

            {error && (
              <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Creating...' : 'Create Experiment'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push('/')}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
