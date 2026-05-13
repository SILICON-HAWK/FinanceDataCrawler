FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json .npmrc ./
RUN npm ci && npm cache clean --force
COPY . .
RUN npm run build
EXPOSE 3000
ENV PORT=3000
CMD ["node", ".svelte-kit/output/server/index.js"]
