import { Badge } from "@/components/ui/badge";

export type RunStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "paused"
  | "recovered";

const variantFor = (status: RunStatus) => {
  switch (status) {
    case "succeeded":
      return "success" as const;
    case "failed":
      return "danger" as const;
    case "running":
      return "live" as const;
    case "queued":
      return "outline" as const;
    case "paused":
      return "warning" as const;
    case "recovered":
      return "paper" as const;
  }
};

export function RunStatusPill({ status }: { status: RunStatus }) {
  return <Badge variant={variantFor(status)}>{status}</Badge>;
}
