FROM node:20-alpine AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json (или yarn.lock)
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Создаем production сборку
RUN npm run build

# Стадия production
FROM nginx:alpine

# Копируем собранные файлы из стадии builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем nginx конфигурацию
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Экспонируем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"] 