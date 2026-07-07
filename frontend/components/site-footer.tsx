import Link from 'next/link';

export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-hairline bg-canvas">
      <div className="mx-auto max-w-[1280px] px-4 py-16 sm:px-6">
        <div className="grid gap-10 md:grid-cols-[2fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-yellow">
                <span className="text-[15px] font-bold leading-none text-[#0a0a0a]">M</span>
              </span>
              <span className="text-[15px] font-bold tracking-tight text-on-dark">
                ML<span className="text-muted-foreground">Tracker</span>
              </span>
            </div>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted-foreground">
              A self-hostable, MLflow-style experiment tracking platform. Log runs,
              metrics, and artifacts from any Python project in four lines of code.
            </p>
          </div>

          <div>
            <p className="eyebrow mb-4">Product</p>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/" className="text-muted-foreground transition-colors hover:text-on-dark">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/experiments/new" className="text-muted-foreground transition-colors hover:text-on-dark">
                  New Experiment
                </Link>
              </li>
              <li>
                <Link href="/integration" className="text-muted-foreground transition-colors hover:text-on-dark">
                  Integration
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <p className="eyebrow mb-4">Resources</p>
            <ul className="space-y-3 text-sm">
              <li>
                <a
                  href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-muted-foreground transition-colors hover:text-on-dark"
                >
                  API Docs
                </a>
              </li>
              <li>
                <Link href="/integration" className="text-muted-foreground transition-colors hover:text-on-dark">
                  Python Client
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-start justify-between gap-3 border-t border-hairline pt-8 text-sm text-muted-soft sm:flex-row sm:items-center">
          <p>© {new Date().getFullYear()} ML Experiment Tracker.</p>
          <p>Built for engineers who ship models.</p>
        </div>
      </div>
    </footer>
  );
}
