"use client";

import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp } from "lucide-react";
import { useMemo, useState } from "react";

import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";

export type EvidenceRow = {
  runId: string;
  sharpeOos: number;
  maxDdOos: number;
  artifact: string;
  configHash: string;
  auditHash: string;
};

export function EvidenceTable({ rows }: { rows: EvidenceRow[] }) {
  const columns = useMemo<ColumnDef<EvidenceRow>[]>(
    () => [
      { accessorKey: "runId", header: "Run", cell: ({ getValue }) => getValue<string>() },
      {
        accessorKey: "sharpeOos",
        header: "Sharpe (OOS)",
        cell: ({ getValue }) => getValue<number>().toFixed(2),
      },
      {
        accessorKey: "maxDdOos",
        header: "Max DD (OOS)",
        cell: ({ getValue }) => `${(getValue<number>() * 100).toFixed(1)}%`,
      },
      { accessorKey: "artifact", header: "Artifact" },
      { accessorKey: "configHash", header: "Config" },
      { accessorKey: "auditHash", header: "Audit" },
    ],
    [],
  );

  const [sorting, setSorting] = useState<SortingState>([{ id: "sharpeOos", desc: true }]);
  const table = useReactTable({
    data: rows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <Table>
      <THead>
        {table.getHeaderGroups().map((hg) => (
          <tr key={hg.id}>
            {hg.headers.map((h) => (
              <TH
                key={h.id}
                onClick={h.column.getToggleSortingHandler()}
                className="cursor-pointer select-none"
              >
                <span className="inline-flex items-center gap-1">
                  {flexRender(h.column.columnDef.header, h.getContext())}
                  {h.column.getIsSorted() === "asc" ? (
                    <ArrowUp className="h-3 w-3" />
                  ) : h.column.getIsSorted() === "desc" ? (
                    <ArrowDown className="h-3 w-3" />
                  ) : null}
                </span>
              </TH>
            ))}
          </tr>
        ))}
      </THead>
      <TBody>
        {table.getRowModel().rows.map((row) => (
          <TR key={row.id}>
            {row.getVisibleCells().map((cell) => (
              <TD key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TD>
            ))}
          </TR>
        ))}
      </TBody>
    </Table>
  );
}
