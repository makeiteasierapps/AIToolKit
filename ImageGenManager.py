import replicate
import os
from io import BytesIO

class ImageGenerator:
    def __init__(self, ssh_manager):
        self.ssh_manager = ssh_manager
        self.remote_path = '/mnt/media_storage/generated'

    def generate_image(self, prompt):
        image_input = {
            "prompt": f"{prompt}",
            "guidance": 3.5
        }

        output = replicate.run(
            "black-forest-labs/flux-dev",
            input=image_input
        )

        print(f"output: {output}")

        # Get SSH client
        ssh_client = self.ssh_manager.get_client()
        if ssh_client:
            sftp = ssh_client.open_sftp()
            
            generated_files = []
            for index, item in enumerate(output):
                # Read image data into memory
                image_data = BytesIO(item.read())
                
                # Generate filename and full remote path
                filename = f"output_{index}.webp"
                remote_file_path = os.path.join(self.remote_path, filename)
                
                # Upload file to remote server
                sftp.putfo(image_data, remote_file_path)
                generated_files.append(filename)
                
            sftp.close()
            ssh_client.close()
            return generated_files
        else:
            # Fallback to local storage if no SSH connection
            for index, item in enumerate(output):
                with open(f"output_{index}.webp", "wb") as file:
                    file.write(item.read())