FROM node:20

WORKDIR /app

ENV ROLLUP_SKIP_NATIVE=true

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
