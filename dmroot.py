#!/usr/bin/env python3

import click
import os
import random
import string

def generate_password():
    """Generates a secure password meeting specified criteria."""
    while True:
        password = ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation, k=20))
        if (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in string.punctuation for c in password) and
            not password[-1].isdigit()):
            return password

@click.command()
@click.option('--docker_image', prompt='Docker image for the Dockerfile', help="Docker image to use for the Dockerfile.")
@click.option('--admin_name', prompt="Admin user name", help="Name of the admin user with sudo privileges.")
@click.option('--admin_password', prompt="Admin user password", hide_input=True, confirmation_prompt=True, help="Password for the admin user.")
@click.option('--database_image', prompt='Docker image for the database', help="Docker image to use for the database.")
@click.option('--lure_users', prompt="Number of lure users (max 100)", type=click.IntRange(1, 100), help="Number of lure users to create.")
def create_mirroot_files(docker_image, admin_name, admin_password, database_image, lure_users):
    """Creates the necessary files for the Docker environment setup."""
    # Display ASCII art
    click.echo(r"""
        _                 _   
  /\/\ (_)_ __ ___   ___ | |_ 
 /    \| | '__/ _ \ / _ \| __|
/ /\/\ \ | | | (_) | (_) | |_ 
\/    \/_|_|  \___/ \___/ \__|
    """)

    # List of names for generating random users
    prenoms = "Alice,Bob,Charlie,David,Emma,Fiona,George,Harry,Isla,Jack,Kate,Liam,Mia,Noah,Olivia,Paul,Quinn,Ruby,Sophia,Tom,Uma,Vincent,Wendy,Xander,Yara,Zack,Amelia,Bruno,Cara,Dylan,Eliza,Freya,Grant,Holly,Ian,Jade,Kevin,Lara,Mason,Nina,Oscar,Piper,Quentin,Rachel,Sean,Tina,Ulrich,Victor,Will,Xena,Yuki,Zephyr"
    
    try:
        # Content for the Dockerfile
        dockerfile_content = f"""
FROM {docker_image}

# Install necessary packages
RUN apt-get update && apt-get install -y sudo rng-tools pwgen auditd fail2ban \
    && rm -rf /var/lib/apt/lists/*

# Create admin user and add to sudoers
ARG ADMIN_NAME
ARG ADMIN_PASSWORD

RUN useradd -m -s /bin/bash ${{ADMIN_NAME}} \\
    && echo "${{ADMIN_NAME}}:${{ADMIN_PASSWORD}}" | chpasswd \\
    && usermod -aG sudo ${{ADMIN_NAME}} \\
    && echo '${{ADMIN_NAME}} ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Copy scripts and set permissions
COPY create_lure_users.sh /home/${{ADMIN_NAME}}/create_lure_users.sh
COPY lure_monitor.sh /home/${{ADMIN_NAME}}/lure_monitor.sh
COPY jail.local /etc/fail2ban/jail.local
COPY audit.rules /etc/audit/rules.d/audit.rules
COPY entrypoint.sh /entrypoint.sh

# Ajout des commandes chmod pour donner les permissions d'exécution
RUN chown ${{ADMIN_NAME}}:${{ADMIN_NAME}} /home/${{ADMIN_NAME}}/create_lure_users.sh /home/${{ADMIN_NAME}}/lure_monitor.sh \\
    && chmod 700 /home/${{ADMIN_NAME}}/create_lure_users.sh /home/${{ADMIN_NAME}}/lure_monitor.sh \\
    && chmod +x /home/${{ADMIN_NAME}}/create_lure_users.sh /home/${{ADMIN_NAME}}/lure_monitor.sh \\
    && chmod +x /entrypoint.sh

# Expose necessary ports (adjust if needed)
EXPOSE 22

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
        """

        # Content for the create_lure_users.sh script
        create_lure_users_content = f"""#!/bin/bash

generate_password() {{
    while true; do
        password=$(< /dev/urandom tr -dc 'A-Za-z0-9!@?~' | head -c20)
        if [[ $password =~ [A-Z] ]] && [[ $password =~ [a-z] ]] && [[ $password =~ [0-9] ]] && [[ $password =~ [!@?~] ]] && [[ ! $password =~ [0-9]$ ]]; then
            echo $password
            break
        fi
    done
}}

PRENOMS_LIST="{prenoms}"

for i in $(seq 1 {lure_users}); do
  RANDOM_PRENOM=$(echo $PRENOMS_LIST | tr "," "\\n" | shuf -n 1)
  username="lure_$RANDOM_PRENOM"
  password=$(generate_password)
  useradd -m -s /bin/bash $username
  echo "$username:$password" | chpasswd
  usermod -aG sudo $username
done
        """

        # Content for the lure_monitor.sh script
        lure_monitor_content = """
#!/bin/bash

# Monitor Audit logs
while true; do
  ausearch -i -f /home | grep "lure_" | while read -r line; do
    user=$(echo $line | grep -oP '(?<=acct=).*?(?= )')
    ip=$(echo $line | grep -oP '(?<=addr=).*?(?= )')
    if [[ ! -z "$user" && ! -z "$ip" ]]; then
      echo "Lure user $user logged in from IP $ip" >> /var/log/lure_users.log
    fi
  done
  sleep 0
done
        """

        # Content for the jail.local configuration for fail2ban
        jail_local_content = """
[DEFAULT]
ignoreip = 127.0.0.1/8
bantime  = 3600
findtime  = 600
maxretry = 3

[lure_users]
enabled = true
port    = all
filter  = lure_users
logpath = /var/log/lure_users.log
maxretry = 1
        """

        # Content for the audit.rules configuration for auditd
        audit_rules_content = """
-w /home -p rwxa -k lure_users
        """

        # Content for the entrypoint.sh script
        entrypoint_content = """
#!/bin/bash

# Start necessary services
service auditd start
service fail2ban start

# Run the create_lure_users script as the admin user
sudo -u ${ADMIN_NAME} bash /home/${ADMIN_NAME}/create_lure_users.sh

# Start the monitoring script in the background
sudo -u ${ADMIN_NAME} bash /home/${ADMIN_NAME}/lure_monitor.sh &

# Start a bash shell to keep the container running and allow interactive access
exec /bin/bash
        """

        # Writing the files
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)
        with open("create_lure_users.sh", "w") as f:
            f.write(create_lure_users_content)
        with open("lure_monitor.sh", "w") as f:
            f.write(lure_monitor_content)
        with open("jail.local", "w") as f:
            f.write(jail_local_content)
        with open("audit.rules", "w") as f:
            f.write(audit_rules_content)
        with open("entrypoint.sh", "w") as f:
            f.write(entrypoint_content)

        # Définition des permissions d'exécution uniquement pour le propriétaire
        os.chmod("create_lure_users.sh", 0o700)
        os.chmod("lure_monitor.sh", 0o700)
        os.chmod("entrypoint.sh", 0o700)

        # Content for the docker-compose.yml file
        docker_compose_content = f"""
services:
  app:
    build: .
    container_name: mirroot_app
    environment:
      - ADMIN_NAME={admin_name}
      - ADMIN_PASSWORD={admin_password}
    ports:
      - "22:22" # adjust if you need SSH access to the container

  database:
    image: {database_image}
    container_name: mirroot_db
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=my_database
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
    driver: local
  cowrie_data:
    driver: local
        """

        with open("docker-compose.yml", "w") as f:
            f.write(docker_compose_content)

        click.echo("Dockerfile, create_lure_users.sh, lure_monitor.sh, jail.local, audit.rules, entrypoint.sh, and docker-compose.yml files have been successfully created.")

    except Exception as e:
        click.echo(f"An error occurred while creating the files: {e}")

if __name__ == '__main__':
    click.echo(r"""
        _                 _   
  /\/\ (_)_ __ ___   ___ | |_ 
 /    \| | '__/ _ \ / _ \| __|
/ /\/\ \ | | | (_) | (_) | |_ 
\/    \/_|_|  \___/ \___/ \__|
    """)
    create_mirroot_files()