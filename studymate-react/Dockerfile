FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker-entrypoint.d/40-study-mate-api-url.sh /docker-entrypoint.d/40-study-mate-api-url.sh
RUN chmod +x /docker-entrypoint.d/40-study-mate-api-url.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
