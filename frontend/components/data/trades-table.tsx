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
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { type Trade } from "@/lib/api";
import { formatDate, formatNumber } from "@/lib/utils";

const columns: ColumnDef<Trade>[] = [
  {
    accessorKey: "ts",
    header: "Time",
    cell: ({ getValue }) => formatDate(getValue<string>()),
  },
  {
    accessorKey: "venue",
    header: "Venue",
    cell: ({ getValue }) => {
      const v = getValue<string>();
      const variant = v === "live" ? "primary" : v === "paper" ? "warning" : "outline";
      return <Badge variant={variant}>{v}</Badge>;
    },
  },
  { accessorKey: "exchange", header: "Exchange" },
  { accessorKey: "symbol", header: "Symbol" },
  {
    accessorKey: "side",
    header: "Side",
    cell: ({ getValue }) => {
      const s = getValue<string>();
      return <Badge variant={s === "buy" ? "success" : "danger"}>{s.toUpperCase()}</Badge>;
    },
  },
  {
    accessorKey: "quantity",
    header: "Qty",
    cell: ({ getValue }) => formatNumber(getValue<number>(), 6),
  },
  {
    accessorKey: "price",
    header: "Price",
    cell: ({ getValue }) => formatNumber(getValue<number>(), 2),
  },
  {
    accessorKey: "fee",
    header: "Fee",
    cell: ({ getValue }) => formatNumber(getValue<number>(), 2),
  },
  {
    accessorKey: "pnl",
    header: "PnL",
    cell: ({ getValue }) => {
      const v = getValue<number | null>();
      if (v == null) return "—";
      return (
        <span className={v >= 0 ? "text-success" : "text-danger"}>{formatNumber(v, 2)}</span>
      );
    },
  },
  { accessorKey: "strategy_id", header: "Strategy" },
];

export function TradesTable({ data }: { data: Trade[] }) {
  const [sorting, setSorting] = useState<SortingState>([{ id: "ts", desc: true }]);
  const table = useReactTable({
    data,
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
        {table.getRowModel().rows.length === 0 ? (
          <tr>
            <TD colSpan={columns.length} className="text-center text-muted-foreground py-6">
              No trades yet.
            </TD>
          </tr>
        ) : (
          table.getRowModel().rows.map((row) => (
            <TR key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <TD key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TD>
              ))}
            </TR>
          ))
        )}
      </TBody>
    </Table>
  );
}
