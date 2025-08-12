FROM nginx:alpine

RUN apk add --no-cache bash gettext

COPY index.html /usr/share/nginx/html/index.template.html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV NEXT_PUBLIC_FIREBASE_PROJECT_ID="" \
    NEXT_PUBLIC_FIREBASE_APP_ID="" \
    NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="" \
    NEXT_PUBLIC_FIREBASE_API_KEY="" \
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="" \
    NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="" \
    NEXT_PUBLIC_FIREBASE_DATABASE_URL=""

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
