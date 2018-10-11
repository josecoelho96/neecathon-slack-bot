FROM nginx:1.15.2-alpine
ARG SERVER_NAME

COPY ./config/nginx/nginx.conf /etc/nginx/
COPY ./config/nginx/slackbot.conf /slackbot.conf
RUN envsubst '${SERVER_NAME}' < /slackbot.conf > /etc/nginx/conf.d/slackbot.conf && rm /slackbot.conf
RUN rm /etc/nginx/conf.d/default.conf

COPY ./config/nginx/ssl/cert.pem /etc/nginx/ssl/cert.pem
COPY ./config/nginx/ssl/key.pem /etc/nginx/ssl/key.pem

CMD ["nginx"]