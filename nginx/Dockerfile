FROM nginx:1.21.6-alpine

COPY nginx.conf /etc/nginx/

RUN apk update \
    && apk upgrade \
    && apk --update add logrotate \
    && apk add --no-cache openssl \
    && apk add --no-cache bash

RUN apk add --no-cache curl

RUN mkdir /volunteer_cache

RUN set -x ; \
    addgroup -g 82 -S www-data ; \
    adduser -u 82 -D -S -G www-data www-data && exit 0 ; exit 1

RUN mkdir cdnhost
RUN curl -L -0 volunteer.coscup.org/img/coscup_volunteer_og.png > /cdnhost/coscup_volunteer_og.png;

RUN curl -L -0 volunteer.coscup.org/favicon.ico > /cdnhost/favicon.ico;
RUN curl -L -0 volunteer.coscup.org/css/bulma.min.091.css > /cdnhost/bulma.min.091.css;

RUN mkdir /cdnhost/css;
RUN curl -L -0 volunteer.coscup.org/faw/css/all.min.css > /cdnhost/css/all.min.css;

RUN mkdir /cdnhost/webfonts;
RUN curl -L -0 volunteer.coscup.org/faw/webfonts/fa-regular-400.ttf > /cdnhost/webfonts/fa-regular-400.ttf;
RUN curl -L -0 volunteer.coscup.org/faw/webfonts/fa-regular-400.woff > /cdnhost/webfonts/fa-regular-400.woff;
RUN curl -L -0 volunteer.coscup.org/faw/webfonts/fa-regular-400.woff2 > /cdnhost/webfonts/fa-regular-400.woff2;
RUN curl -L -0 volunteer.coscup.org/faw/webfonts/fa-solid-900.ttf > /cdnhost/webfonts/fa-solid-900.ttf;
RUN curl -L -0 volunteer.coscup.org/faw/webfonts/fa-solid-900.woff > /cdnhost/webfonts/fa-solid-900.woff;
RUN curl -L -0 volunteer.coscup.org/faw/webfonts/fa-solid-900.woff2 > /cdnhost/webfonts/fa-solid-900.woff2;
RUN curl -L -0 volunteer.coscup.org/js/vue.min.js > /cdnhost/vue.min.js;
#RUN chown www-data:www-data /cdnhost/*
RUN chown nginx:nginx /cdnhost/*

RUN rm /etc/nginx/conf.d/default.conf

CMD ["nginx"]

EXPOSE 80 81 443