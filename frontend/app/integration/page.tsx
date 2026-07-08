'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Copy, Check, Download, ArrowRight } from 'lucide-react';

function CodeWindow({
  code,
  id,
  filename,
  copiedCode,
  onCopy,
}: {
  code: string;
  id: string;
  filename: string;
  copiedCode: string | null;
  onCopy: (code: string, id: string) => void;
}) {
  return (
    <div className="code-window">
      <div className="code-window__bar">
        <span className="code-window__dot bg-[#ff5f56]" />
        <span className="code-window__dot bg-[#ffbd2e]" />
        <span className="code-window__dot bg-[#27c93f]" />
        <span className="ml-2 text-xs text-muted-foreground">{filename}</span>
        <button
          onClick={() => onCopy(code, id)}
          className="ml-auto flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-surface-elevated hover:text-on-dark"
        >
          {copiedCode === id ? (
            <>
              <Check className="h-3.5 w-3.5 text-success" /> Copied
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" /> Copy
            </>
          )}
        </button>
      </div>
      <pre className="overflow-x-auto p-6 text-[13px] leading-relaxed text-body-strong">
        <code>{code}</code>
      </pre>
    </div>
  );
}

const METHOD_STYLES: Record<string, string> = {
  GET: 'bg-info/10 text-[#7cb0ff] border-info/30',
  POST: 'bg-success/10 text-success border-success/30',
  PUT: 'bg-[#f59e0b]/10 text-[#f5b544] border-[#f59e0b]/30',
  DELETE: 'bg-destructive/10 text-[#ff8a8a] border-destructive/30',
};

function Endpoint({ method, path, desc }: { method: string; path: string; desc: string }) {
  return (
    <div className="flex flex-col gap-2 rounded-[12px] border border-hairline bg-surface-card p-4 sm:flex-row sm:items-center sm:gap-4">
      <span
        className={`inline-flex w-fit items-center rounded-md border px-2.5 py-1 font-mono text-xs font-semibold ${METHOD_STYLES[method]}`}
      >
        {method}
      </span>
      <code className="font-mono text-sm text-on-dark">{path}</code>
      <span className="text-sm text-muted-foreground sm:ml-auto">{desc}</span>
    </div>
  );
}

export default function IntegrationPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

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
    <div className="space-y-24">
      {/* Hero */}
      <section>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <span className="badge-yellow">Integration</span>
            <h1 className="mt-6 max-w-2xl text-4xl font-bold leading-[1.08] tracking-[-0.02em] text-on-dark sm:text-5xl">
              Add tracking to any project in minutes.
            </h1>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-body">
              One file. No setup. Drop <code className="font-mono text-brand-yellow">mltracker.py</code>{' '}
              into your project and start logging with four lines of code.
            </p>
          </div>
          <Link href="/">
            <Button variant="outline">← Back to dashboard</Button>
          </Link>
        </div>

        {/* Steps */}
        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {[
            { n: '1', title: 'Start tracking', body: 'Give your experiment a name and add hyperparameters.' },
            { n: '2', title: 'Log results', body: 'Record metrics like accuracy and loss as you train.' },
            { n: '3', title: 'Save & view', body: 'Upload your model and see charts on the dashboard.' },
          ].map((step) => (
            <div key={step.n} className="rounded-[12px] border border-hairline bg-surface-card p-8">
              <div className="stat-callout text-4xl">{step.n}</div>
              <h3 className="mt-4 text-base font-semibold text-on-dark">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{step.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Download CTA band */}
      <section className="cta-band flex flex-col items-start justify-between gap-8 p-8 sm:flex-row sm:items-center sm:p-10">
        <div className="max-w-lg">
          <h2 className="text-2xl font-bold tracking-tight text-[#0a0a0a] sm:text-3xl">
            Get the tracker file
          </h2>
          <p className="mt-2 text-sm text-[#0a0a0a]/70">
            A single Python file with only <code className="font-mono">requests</code> as a
            dependency. Drop it in your project and start tracking.
          </p>
        </div>
        <button
          onClick={downloadMLTracker}
          className="inline-flex h-11 shrink-0 items-center gap-2 rounded-md bg-[#0a0a0a] px-6 text-sm font-semibold text-brand-yellow transition-colors hover:bg-[#1a1a1a]"
        >
          <Download className="h-4 w-4" />
          Download mltracker.py
        </button>
      </section>

      {/* Quick usage + Base URL */}
      <section className="grid gap-6 lg:grid-cols-2">
        <div>
          <span className="eyebrow">Then use it like this</span>
          <div className="mt-4">
            <CodeWindow
              filename="quickstart.py"
              code={`from mltracker import tracker

tracker.start("My Experiment", lr=0.001)
tracker.log("loss", 0.5, step=1)
tracker.save_model("model.pkl")
tracker.finish()`}
              id="quickstart"
              copiedCode={copiedCode}
              onCopy={copyToClipboard}
            />
          </div>
        </div>
        <div>
          <span className="eyebrow">API base URL</span>
          <div className="mt-4 flex items-center gap-3 rounded-[12px] border border-hairline bg-surface-card px-5 py-6 font-mono text-sm">
            <span className="text-muted-foreground">Base URL</span>
            <span className="font-semibold text-brand-yellow">{apiUrl}</span>
          </div>
          <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
            Point the client at this URL, or set{' '}
            <code className="font-mono text-body-strong">NEXT_PUBLIC_API_URL</code> in your
            environment. Full interactive docs live at{' '}
            <a
              href={`${apiUrl}/docs`}
              target="_blank"
              rel="noreferrer"
              className="text-brand-yellow underline underline-offset-4"
            >
              {apiUrl}/docs
            </a>
            .
          </p>
        </div>
      </section>

      {/* Code examples */}
      <section>
        <span className="eyebrow">Code examples</span>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-on-dark">
          Copy, paste, ship
        </h2>
        <div className="mt-6">
          <Tabs defaultValue="python">
            <TabsList>
              <TabsTrigger value="python">Python</TabsTrigger>
              <TabsTrigger value="curl">cURL</TabsTrigger>
              <TabsTrigger value="nodejs">Node.js</TabsTrigger>
            </TabsList>

            <TabsContent value="python" className="mt-4">
              <CodeWindow
                filename="train.py"
                code={pythonExample}
                id="python"
                copiedCode={copiedCode}
                onCopy={copyToClipboard}
              />
            </TabsContent>
            <TabsContent value="curl" className="mt-4">
              <CodeWindow
                filename="requests.sh"
                code={curlExample}
                id="curl"
                copiedCode={copiedCode}
                onCopy={copyToClipboard}
              />
            </TabsContent>
            <TabsContent value="nodejs" className="mt-4">
              <CodeWindow
                filename="track.js"
                code={nodeExample}
                id="nodejs"
                copiedCode={copiedCode}
                onCopy={copyToClipboard}
              />
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* API reference */}
      <section>
        <span className="eyebrow">API reference</span>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-on-dark">Endpoints</h2>
        <div className="mt-6 space-y-3">
          <Endpoint method="POST" path="/experiments" desc="Create a new experiment" />
          <Endpoint method="GET" path="/experiments" desc="List all experiments" />
          <Endpoint method="GET" path="/experiments/{id}" desc="Get experiment details" />
          <Endpoint method="POST" path="/experiments/{id}/metrics" desc="Log a metric value" />
          <Endpoint
            method="POST"
            path="/artifacts/experiments/{id}/upload"
            desc="Upload an artifact file"
          />
          <Endpoint method="PUT" path="/experiments/{id}/status" desc="Update experiment status" />
          <Endpoint method="PUT" path="/experiments/{id}/tags" desc="Update experiment tags" />
          <Endpoint method="DELETE" path="/experiments/{id}" desc="Delete an experiment" />
        </div>
      </section>

      {/* Closing CTA */}
      <section className="rounded-[12px] border border-hairline bg-surface-card p-8 text-center sm:p-12">
        <h2 className="text-2xl font-bold tracking-tight text-on-dark sm:text-3xl">
          Ready to track your first run?
        </h2>
        <p className="mx-auto mt-3 max-w-md text-sm text-muted-foreground">
          Create an experiment from the dashboard, or wire up the client and it appears
          automatically.
        </p>
        <div className="mt-6 flex justify-center">
          <Link href="/experiments/new">
            <Button size="lg">
              Create experiment
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
