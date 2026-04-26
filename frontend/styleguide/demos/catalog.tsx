"use client";

import { AiInsightPanel } from "@/components/operator/ai-insight-panel";
import { AlertBanner } from "@/components/operator/alert-banner";
import { CommandPalette } from "@/components/operator/command-palette";
import { LogStream } from "@/components/operator/log-stream";
import { RiskPanel } from "@/components/operator/risk-panel";
import { RunTimeline } from "@/components/operator/run-timeline";
import { StrategyCard } from "@/components/operator/strategy-card";
import { EquityChart } from "@/components/charts/equity-chart";
import { FreshnessSparkline } from "@/components/charts/freshness-sparkline";
import { PnLDistributionChart } from "@/components/charts/pnl-distribution-chart";
import { RiskExposureChart } from "@/components/charts/risk-exposure-chart";
import { EvidenceTable } from "@/components/data/evidence-table";
import { MetricTile } from "@/components/data/metric-tile";
import { RiskLimitMeter } from "@/components/data/risk-limit-meter";
import { RunStatusPill } from "@/components/data/run-status-pill";
import { TradesTable } from "@/components/data/trades-table";
import { Header } from "@/components/nav/header";
import { Sidebar } from "@/components/nav/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardValue } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import {
  mockCommands,
  mockEquitySeries,
  mockEvidenceRows,
  mockExposureSeries,
  mockHealthDegraded,
  mockHealthOk,
  mockHistogram,
  mockLogEvents,
  mockSparkline,
  mockTimeline,
  mockTradesEmpty,
  mockTradesPopulated,
} from "@/styleguide/mocks/fixtures";

export function BadgeDemo() {
  return (
    <div className="flex flex-wrap gap-2">
      <Badge>default</Badge>
      <Badge variant="success">success</Badge>
      <Badge variant="warning">warning</Badge>
      <Badge variant="danger">danger</Badge>
      <Badge variant="primary">primary</Badge>
      <Badge variant="outline">outline</Badge>
      <Badge variant="live">live</Badge>
      <Badge variant="paper">paper</Badge>
      <Badge variant="retired">retired</Badge>
      <Badge variant="degraded">degraded</Badge>
      <Badge variant="magenta">magenta</Badge>
    </div>
  );
}

export function CardDemo() {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>default</CardTitle>
        </CardHeader>
        <CardContent>Panel body</CardContent>
      </Card>
      <Card variant="panel">
        <CardHeader>
          <CardTitle>panel</CardTitle>
        </CardHeader>
        <CardContent>dense shell</CardContent>
      </Card>
      <Card variant="metric">
        <CardHeader>
          <CardTitle>metric</CardTitle>
        </CardHeader>
        <CardContent>
          <CardValue>1.42</CardValue>
        </CardContent>
      </Card>
      <Card variant="risk">
        <CardHeader>
          <CardTitle>risk</CardTitle>
        </CardHeader>
        <CardContent>breach surface</CardContent>
      </Card>
      <Card variant="alert">
        <CardHeader>
          <CardTitle>alert</CardTitle>
        </CardHeader>
        <CardContent>operator attention</CardContent>
      </Card>
      <Card variant="glass">
        <CardHeader>
          <CardTitle>glass</CardTitle>
        </CardHeader>
        <CardContent>frosted overlay</CardContent>
      </Card>
    </div>
  );
}

export function InputDemo() {
  return <Input placeholder="Search runs…" defaultValue="demo-query" />;
}

export function TableDemo() {
  return (
    <Table>
      <THead>
        <TR>
          <TH>col a</TH>
          <TH>col b</TH>
        </TR>
      </THead>
      <TBody>
        <TR>
          <TD>alpha</TD>
          <TD>beta</TD>
        </TR>
      </TBody>
    </Table>
  );
}

export function EquityChartDemo() {
  return (
    <div className="space-y-4">
      <EquityChart data={mockEquitySeries(60)} />
      <EquityChart data={[]} />
    </div>
  );
}

export function TradesTableDemo() {
  return (
    <div className="space-y-6">
      <TradesTable data={mockTradesPopulated} />
      <TradesTable data={mockTradesEmpty} />
    </div>
  );
}

export function HeaderDemo() {
  return (
    <div className="space-y-4">
      <Header health={mockHealthOk} title="Styleguide / fixtures" />
      <Header health={mockHealthDegraded} title="Degraded header" />
      <Header health={null} title="Unreachable API" />
    </div>
  );
}

export function SidebarDemo() {
  return <Sidebar />;
}

export function ButtonDemo() {
  return (
    <div className="flex flex-wrap gap-2">
      <Button variant="primary">primary</Button>
      <Button variant="ghost">ghost</Button>
      <Button variant="danger">danger</Button>
      <Button variant="command">command</Button>
      <Button size="sm">small</Button>
      <Button loading>loading</Button>
      <Button disabled>disabled</Button>
    </div>
  );
}

export function SelectDemo() {
  return (
    <Select defaultValue="a">
      <option value="a">alpha</option>
      <option value="b">beta</option>
    </Select>
  );
}

export function TextareaDemo() {
  return <Textarea defaultValue={"notes:\n- deterministic mocks\n- no backend"} />;
}

export function SkeletonDemo() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-4 w-2/3" />
      <Skeleton className="h-24 w-full" />
    </div>
  );
}

export function EmptyStateDemo() {
  return (
    <EmptyState
      title="No runs"
      description="Queue a backtest from the operator console to populate this surface."
    >
      <Button variant="ghost" size="sm">
        open docs
      </Button>
    </EmptyState>
  );
}

export function ErrorStateDemo() {
  return (
    <ErrorState title="Stream interrupted" description="SSE disconnected; retrying with backoff.">
      <Button variant="primary" size="sm">
        retry
      </Button>
    </ErrorState>
  );
}

export function MetricTileDemo() {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      <MetricTile label="Sharpe (OOS)" value="1.24" delta={0.12} sourceTs="2024-06-01T12:00:00Z" />
      <MetricTile label="Latency p99" value="182" unit="ms" stale delta={-4.2} sourceTs="stale" />
    </div>
  );
}

export function RunStatusPillDemo() {
  const statuses = ["queued", "running", "succeeded", "failed", "paused", "recovered"] as const;
  return (
    <div className="flex flex-wrap gap-2">
      {statuses.map((s) => (
        <RunStatusPill key={s} status={s} />
      ))}
    </div>
  );
}

export function RiskLimitMeterDemo() {
  return (
    <div className="space-y-3 max-w-md">
      <RiskLimitMeter label="gross exposure" current={0.72} limit={1.0} />
      <RiskLimitMeter
        label="per-symbol weight"
        current={0.31}
        limit={0.25}
        rejectReason="RiskCheckRejected(rule=max_per_symbol_weight)"
      />
    </div>
  );
}

export function EvidenceTableDemo() {
  return <EvidenceTable rows={mockEvidenceRows} />;
}

export function RiskExposureChartDemo() {
  return <RiskExposureChart series={mockExposureSeries} />;
}

export function PnLDistributionChartDemo() {
  return <PnLDistributionChart buckets={mockHistogram} />;
}

export function FreshnessSparklineDemo() {
  return <FreshnessSparkline points={mockSparkline} />;
}

export function StrategyCardDemo() {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      <StrategyCard name="momentum_xover" mode="paper" status="running" sharpe={1.1} gate="open" />
      <StrategyCard name="retired_probe" mode="retired" status="failed" sharpe={-0.2} gate="blocked" />
    </div>
  );
}

export function RiskPanelDemo() {
  return (
    <RiskPanel
      killSwitchArmed={false}
      limits={[
        { label: "gross", current: 0.6, limit: 1.0 },
        { label: "leverage", current: 0.9, limit: 1.0 },
      ]}
      rejects={["max_daily_loss: session halted"]}
    />
  );
}

export function RunTimelineDemo() {
  return <RunTimeline events={mockTimeline} />;
}

export function AlertBannerDemo() {
  return (
    <div className="space-y-3">
      <AlertBanner severity="info" title="Maintenance window" body="Read-only mode for 10 minutes." />
      <AlertBanner severity="warning" title="Drift detected" body="Feature z-score exceeded 3σ vs backtest." />
      <AlertBanner
        severity="critical"
        title="Kill-switch"
        body="Operator acknowledged halt; open orders cancelled."
        auditHref="#audit-kill"
      />
    </div>
  );
}

export function LogStreamDemo() {
  return <LogStream events={mockLogEvents} />;
}

export function CommandPaletteDemo() {
  return (
    <div className="relative min-h-[200px]">
      <CommandPalette
        initialOpen
        commands={mockCommands}
        onCommand={() => {
          /* styleguide: no-op */
        }}
      />
    </div>
  );
}

export function AiInsightPanelDemo() {
  return (
    <AiInsightPanel
      summary="OOS degradation likely from turnover spike after fee model change."
      cites={["docs/EVALUATION.md § gates", "run:run-a manifest.json"]}
    />
  );
}
