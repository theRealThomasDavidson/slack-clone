FROM node:16

# Create app directory and set permissions
WORKDIR /app

# Add node user and set ownership
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

# Set correct permissions
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"] 