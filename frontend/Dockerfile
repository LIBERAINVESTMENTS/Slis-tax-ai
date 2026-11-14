FROM node:24-alpine

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json ./
RUN npm install -g pnpm@9 && pnpm install

COPY . .

ENV NEXT_PUBLIC_API_URL=http://localhost:8000

RUN pnpm run build

CMD ["pnpm", "run", "start"]
