'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Copy, Check, Code, BookOpen, Zap, Download, ChevronDown, ChevronUp } from 'lucide-react';

function CodeBlock({ code, id, copiedCode, onCopy }: { 
  code: string; 
  id: string; 
  copiedCode: string | null;
  onCopy: (code: string, id: string) => void;
}) {
  return (
    <div className="relative">
      <div className="absolute right-2 top-2 z-10">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onCopy(code, id)}
          className="h-8 w-8 p-0"
        >
          {copiedCode === id ? (
            <Check className="h-4 w-4 text-green-500" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
        </Button>
      </div>
      <pre className="overflow-x-auto rounded-lg border bg-muted p-4 text-sm">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export default function IntegrationPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [showPythonCode, setShowPythonCode] = useState(false);
  const [showCurlCode, setShowCurlCode] = useState(false);
  const [showNodeCode, setShowNodeCode] = useState(false);

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const downloadMLTracker = async () => {
    try {
      const response = await fetch('/mltracker.py');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'mltracker.py';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download mltracker.py:', error);
    }
  };

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Simple, human-friendly Python example
  const pythonExample = `from mltracker import tracker

# Start tracking your experiment
tracker.start("My Cool Model", learning_rate=0.001, epochs=50)

# Log metrics as you train
for epoch in range(50):
    loss = train_one_epoch()  # Your training code here
    tracker.log("loss", loss, step=epoch)

# Save your trained model
tracker.save_model("my_model.pkl")

# Mark as done
tracker.finish()

# That's it! Check the dashboard to see your results.`;

  // Simple curl examples
  const curlExample = `# Create an experiment
curl -X POST "${apiUrl}/experiments" \\
  -H "Content-Type: application/json" \\
  -d '{"name": "My Experiment", "hyperparameters": {"lr": 0.001}}'

# Log a metric (replace YOUR_EXPERIMENT_ID)
curl -X POST "${apiUrl}/experiments/YOUR_EXPERIMENT_ID/metrics" \\
  -H "Content-Type: application/json" \\
  -d '{"metric_name": "accuracy", "value": 0.95, "step": 1}'

# Update status
curl -X PUT "${apiUrl}/experiments/YOUR_EXPERIMENT_ID/status" \\
  -H "Content-Type: application/json" \\
  -d '{"status": "completed"}'`;

  // Simple Node.js example
  const nodeExample = `const axios = require('axios');

const API_URL = '${apiUrl}';
let experimentId = null;

// Create experiment
async function createExperiment() {
  const response = await axios.post(\`\${API_URL}/experiments\`, {
    name: 'My Experiment',
    hyperparameters: { learning_rate: 0.001 },
    tags: ['nodejs', 'test']
  });
  experimentId = response.data.id;
  console.log('Experiment created:', experimentId);
}

// Log metric
async function logMetric(name, value, step) {
  await axios.post(\`\${API_URL}/experiments/\${experimentId}/metrics\`, {
    metric_name: name,
    value: value,
    step: step
  });
  console.log(\`Logged \${name}: \${value}\`);
}

// Usage
(async () => {
  await createExperiment();
  await logMetric('accuracy', 0.95, 1);
})();`;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Integrate with Your Project</h1>
          <p className="text-muted-foreground">
            Add experiment tracking to any ML project in minutes
          </p>
        </div>
        <Link href="/">
          <Button variant="outline">← Back to Dashboard</Button>
        </Link>
      </div>

      {/* Quick Start */}
      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            How It Works
          </CardTitle>
          <CardDescription>Track your experiments in 3 simple steps</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
                1
              </div>
              <h3 className="font-semibold">Start Tracking</h3>
              <p className="text-sm text-muted-foreground">
                Give your experiment a name and add hyperparameters
              </p>
            </div>
            <div className="space-y-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
                2
              </div>
              <h3 className="font-semibold">Log Results</h3>
              <p className="text-sm text-muted-foreground">
                Record metrics like accuracy and loss as you train
              </p>
            </div>
            <div className="space-y-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
                3
              </div>
              <h3 className="font-semibold">Save & View</h3>
              <p className="text-sm text-muted-foreground">
                Upload your model and see beautiful charts on the dashboard
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Download MLTracker */}
      <Card className="border-green-500/20 bg-green-500/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-green-600 dark:text-green-400" />
            Get the Tracker File
          </CardTitle>
          <CardDescription>
            One file. No setup. Just works.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">Download mltracker.py</p>
              <p className="text-xs text-muted-foreground">
                Drop it in your project and start tracking with 4 lines of code
              </p>
            </div>
            <Button 
              onClick={downloadMLTracker}
              className="gap-2 bg-green-600 hover:bg-green-700"
            >
              <Download className="h-4 w-4" />
              Download File
            </Button>
          </div>
          
          <div className="rounded-lg border bg-muted/50 p-4">
            <p className="text-sm font-semibold mb-2">Then use it like this:</p>
            <pre className="text-xs overflow-x-auto">
              <code>{`from mltracker import tracker

tracker.start("My Experiment", lr=0.001)
tracker.log("loss", 0.5, step=1)
tracker.save_model("model.pkl")
tracker.finish()`}</code>
            </pre>
          </div>
        </CardContent>
      </Card>

      {/* API Endpoint */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Code className="h-5 w-5" />
            API Endpoint
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 rounded-lg border bg-muted p-3 font-mono text-sm">
            <span className="text-muted-foreground">Base URL:</span>
            <span className="font-semibold">{apiUrl}</span>
          </div>
        </CardContent>
      </Card>

      {/* Code Examples */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Code Examples
          </CardTitle>
          <CardDescription>
            Simple, copy-paste examples to get you started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="python">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="python">Python</TabsTrigger>
              <TabsTrigger value="curl">cURL</TabsTrigger>
              <TabsTrigger value="nodejs">Node.js</TabsTrigger>
            </TabsList>
            
            <TabsContent value="python" className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">Python - The Easy Way</h3>
                    <p className="text-sm text-muted-foreground">
                      Download mltracker.py and use it in your training code
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowPythonCode(!showPythonCode)}
                    className="gap-2"
                  >
                    {showPythonCode ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    {showPythonCode ? 'Hide Code' : 'Show Code'}
                  </Button>
                </div>
              </div>
              {showPythonCode && (
                <CodeBlock code={pythonExample} id="python" copiedCode={copiedCode} onCopy={copyToClipboard} />
              )}
            </TabsContent>

            <TabsContent value="curl" className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">cURL - For Testing</h3>
                    <p className="text-sm text-muted-foreground">
                      Quick commands to test the API from terminal
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowCurlCode(!showCurlCode)}
                    className="gap-2"
                  >
                    {showCurlCode ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    {showCurlCode ? 'Hide Code' : 'Show Code'}
                  </Button>
                </div>
              </div>
              {showCurlCode && (
                <CodeBlock code={curlExample} id="curl" copiedCode={copiedCode} onCopy={copyToClipboard} />
              )}
            </TabsContent>

            <TabsContent value="nodejs" className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">Node.js - For JS Projects</h3>
                    <p className="text-sm text-muted-foreground">
                      Simple async functions for your Node.js apps
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowNodeCode(!showNodeCode)}
                    className="gap-2"
                  >
                    {showNodeCode ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    {showNodeCode ? 'Hide Code' : 'Show Code'}
                  </Button>
                </div>
              </div>
              {showNodeCode && (
                <CodeBlock code={nodeExample} id="nodejs" copiedCode={copiedCode} onCopy={copyToClipboard} />
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* API Reference */}
      <Card>
        <CardHeader>
          <CardTitle>API Reference</CardTitle>
          <CardDescription>Available endpoints and their usage</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-green-500/10 px-2 py-1 text-xs font-semibold text-green-600 dark:text-green-400">
                  POST
                </span>
                <code className="text-sm">/experiments</code>
              </div>
              <p className="text-sm text-muted-foreground">Create a new experiment</p>
            </div>

            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-blue-500/10 px-2 py-1 text-xs font-semibold text-blue-600 dark:text-blue-400">
                  GET
                </span>
                <code className="text-sm">/experiments</code>
              </div>
              <p className="text-sm text-muted-foreground">List all experiments</p>
            </div>

            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-blue-500/10 px-2 py-1 text-xs font-semibold text-blue-600 dark:text-blue-400">
                  GET
                </span>
                <code className="text-sm">/experiments/&#123;id&#125;</code>
              </div>
              <p className="text-sm text-muted-foreground">Get experiment details</p>
            </div>

            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-green-500/10 px-2 py-1 text-xs font-semibold text-green-600 dark:text-green-400">
                  POST
                </span>
                <code className="text-sm">/experiments/&#123;id&#125;/metrics</code>
              </div>
              <p className="text-sm text-muted-foreground">Log a metric value</p>
            </div>

            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-green-500/10 px-2 py-1 text-xs font-semibold text-green-600 dark:text-green-400">
                  POST
                </span>
                <code className="text-sm">/experiments/&#123;id&#125;/artifacts</code>
              </div>
              <p className="text-sm text-muted-foreground">Upload an artifact file</p>
            </div>

            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-orange-500/10 px-2 py-1 text-xs font-semibold text-orange-600 dark:text-orange-400">
                  PUT
                </span>
                <code className="text-sm">/experiments/&#123;id&#125;/status</code>
              </div>
              <p className="text-sm text-muted-foreground">Update experiment status</p>
            </div>

            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-orange-500/10 px-2 py-1 text-xs font-semibold text-orange-600 dark:text-orange-400">
                  PUT
                </span>
                <code className="text-sm">/experiments/&#123;id&#125;/tags</code>
              </div>
              <p className="text-sm text-muted-foreground">Update experiment tags</p>
            </div>

            <div className="rounded-lg border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded bg-red-500/10 px-2 py-1 text-xs font-semibold text-red-600 dark:text-red-400">
                  DELETE
                </span>
                <code className="text-sm">/experiments/&#123;id&#125;</code>
              </div>
              <p className="text-sm text-muted-foreground">Delete an experiment</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
