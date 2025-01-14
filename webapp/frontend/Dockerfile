FROM node:18-slim  
WORKDIR /app

COPY package*.json ./
RUN npm install

# Create user and set permissions
RUN addgroup --system --gid 1008 nodejs && \
    adduser --system --uid 1008 nextjs && \
    chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Copy source with correct ownership
COPY --chown=nextjs:nodejs . .


EXPOSE 5173

CMD ["npm", "run", "dev"]
