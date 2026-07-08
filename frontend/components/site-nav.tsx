'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';

const NAV_LINKS = [
  { href: '/', label: 'Dashboard' },
  { href: '/integration', label: 'Integration' },
];

function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2.5">
      <span className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-yellow">
        <span className="text-[15px] font-bold leading-none text-[#0a0a0a]">M</span>
      </span>
      <span className="text-[15px] font-bold tracking-tight text-on-dark">
        ML<span className="text-muted-foreground">Tracker</span>
      </span>
    </Link>
  );
}

export function SiteNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) =>
    href === '/' ? pathname === '/' : pathname.startsWith(href);

  return (
    <header className="sticky top-0 z-50 border-b border-hairline bg-canvas/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-[1280px] items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-8">
          <Logo />
          <nav className="hidden items-center gap-6 md:flex">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'text-sm font-medium transition-colors',
                  isActive(link.href)
                    ? 'text-on-dark'
                    : 'text-muted-foreground hover:text-on-dark'
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`}
            target="_blank"
            rel="noreferrer"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-on-dark"
          >
            API Docs
          </a>
          <Link
            href="/experiments/new"
            className="inline-flex h-10 items-center justify-center rounded-md bg-brand-yellow px-5 text-sm font-semibold text-[#0a0a0a] transition-colors hover:bg-brand-yellow-active"
          >
            New Experiment
          </Link>
        </div>

        <button
          className="flex h-9 w-9 items-center justify-center rounded-md text-on-dark md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-hairline bg-canvas px-4 py-4 md:hidden">
          <nav className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className={cn(
                  'rounded-md px-3 py-2 text-sm font-medium',
                  isActive(link.href)
                    ? 'bg-surface-card text-on-dark'
                    : 'text-muted-foreground'
                )}
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/experiments/new"
              onClick={() => setOpen(false)}
              className="mt-2 inline-flex h-10 items-center justify-center rounded-md bg-brand-yellow px-5 text-sm font-semibold text-[#0a0a0a]"
            >
              New Experiment
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
