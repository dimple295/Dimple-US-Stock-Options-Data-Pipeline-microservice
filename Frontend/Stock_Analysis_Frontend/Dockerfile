FROM node:20-alpine

WORKDIR /app

RUN npm install -g @angular/cli

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 4200

CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--port", "4200"]
