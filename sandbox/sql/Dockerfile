# SQL Sandbox Docker Image
FROM mysql:8.0

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=sandbox_root_pass
ENV MYSQL_DATABASE=sandbox_db
ENV MYSQL_USER=sandbox_user
ENV MYSQL_PASSWORD=sandbox_pass

# Copy security configuration
COPY security_config.cnf /etc/mysql/conf.d/security.cnf

# Copy initialization script
COPY init_db.sql /docker-entrypoint-initdb.d/

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose MySQL port
EXPOSE 3306

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD mysqladmin ping -h localhost -u $MYSQL_USER -p$MYSQL_PASSWORD || exit 1

# Use custom entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["mysqld"]
