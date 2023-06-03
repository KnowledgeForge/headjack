FROM node:18-alpine

WORKDIR /code
COPY . /code

RUN npm ci
RUN npm run build

ENV PORT=4000
EXPOSE 4000

CMD [ "npm", "run", "start" ]
