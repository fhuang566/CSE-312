FROM nginx

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./cert.pem /root/cert.pem
COPY ./private.key /root/private.key

EXPOSE 80
EXPOSE 443