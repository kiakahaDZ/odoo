FROM odoo:18.0

USER root

# Install any OS dependencies you might need (optional)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     python3-magic \
#     && rm -rf /var/lib/apt/lists/*

# If you have actual custom python libraries NOT in Odoo core, add them here
# For now, we omit the standard Odoo requirements.txt because they are already pre-installed
# and cause build timeouts/conflicts.
# COPY requirements_custom.txt /tmp/requirements_custom.txt
# RUN pip install --no-cache-dir -r /tmp/requirements_custom.txt || true

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure odoo user has permissions to the config directory and file
COPY odoo.conf /etc/odoo/odoo.conf
RUN chown -R odoo:odoo /etc/odoo

# Create directory for custom addons
RUN mkdir -p /mnt/extra-addons && chown -R odoo:odoo /mnt/extra-addons

WORKDIR /var/lib/odoo

# Switch back to odoo user
USER odoo

# Expose port
EXPOSE 8069

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]