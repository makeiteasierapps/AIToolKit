import os
import paramiko

class SSHManager:
    def __init__(self, is_dev_mode, logger):
        self.is_dev_mode = is_dev_mode
        self.logger = logger
        self.dev_server_ip = 'myserver.local'

    def _get_ssh_client(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_key_path = os.path.expanduser('~/.ssh/abyssus')
            ssh.connect(
                self.dev_server_ip,
                username=os.getenv('SERVER_USERNAME'),
                key_filename=ssh_key_path
            )
            return ssh
        except Exception as e:
            self.logger.error(f"Failed to establish SSH connection: {str(e)}")
            return None

    def get_client(self):
        if self.is_dev_mode:
            return self._get_ssh_client()
        return None