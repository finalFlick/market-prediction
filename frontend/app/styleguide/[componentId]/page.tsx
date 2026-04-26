import { notFound } from "next/navigation";

import { getComponent } from "@/styleguide/registry";

import { StyleguideDetailClient } from "./detail-client";

export default async function StyleguideComponentPage({
  params,
}: {
  params: Promise<{ componentId: string }>;
}) {
  const { componentId } = await params;
  if (!getComponent(componentId)) {
    notFound();
  }
  return <StyleguideDetailClient componentId={componentId} />;
}
