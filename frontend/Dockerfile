# Next.js frontend container, multi-stage with standalone output.

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --no-audit --no-fund

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
# Server components call the API from inside the docker network; keep in sync
# with docker-compose `environment` and `api.ts` default.
ENV NEXT_PUBLIC_API_URL=http://backend:8000
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
RUN addgroup -S app && adduser -S nextjs -G app

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:app /app/.next/standalone ./
COPY --from=builder --chown=nextjs:app /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
