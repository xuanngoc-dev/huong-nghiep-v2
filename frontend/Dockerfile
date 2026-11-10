# Frontend: chỉ đóng gói thư mục dist đã build sẵn, không build lại trong image.
# Trước khi build image:
#   cd frontend && npm ci && npm run build
# Build image (context là thư mục frontend):
#   docker build -t huongnghiep-frontend ./frontend
FROM nginx:1.27-alpine

# Địa chỉ backend mà nginx proxy /api tới (dùng trong nginx/default.conf.template)
ENV BACKEND_URL=http://backend:3060

RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY dist/ /usr/share/nginx/html/

EXPOSE 80
