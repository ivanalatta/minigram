FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Vite fija las variables VITE_* al momento del build.
# VITE_API_URL vacío = mismo dominio (nginx hace de proxy al backend).
ARG VITE_API_URL=""
ARG VITE_GOOGLE_CLIENT_ID=""
ENV VITE_API_URL=$VITE_API_URL VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 80 443
