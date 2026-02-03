# 第一阶段：构建 (Build)
FROM node:18-alpine as build-stage

WORKDIR /app

# 设置 npm 淘宝镜像 (加速下载)
RUN npm config set registry https://registry.npmmirror.com

# 复制依赖文件
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建生产环境代码
RUN npm run build

# 第二阶段：运行 (Production)
FROM nginx:stable-alpine as production-stage

# 复制构建产物到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]