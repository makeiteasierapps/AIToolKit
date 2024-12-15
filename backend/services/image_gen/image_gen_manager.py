import replicate
from datetime import datetime
from dspy import LM, configure, InputField, OutputField, Signature, Predict
import os
import re
from io import BytesIO

class ImageCategorizer(Signature):
    """
    Categorize an image based on a prompt, Example categories: Landscapes, Science, Technology, Food, etc.
    """
    prompt = InputField()
    category = OutputField()

class ImageGenerator:
    def __init__(self, ssh_manager):
        self.ssh_manager = ssh_manager
        self.storage_path = '/mnt/media_storage/generated'
        lm = LM(model='anthropic/gpt-4o-mini')
        configure(lm=lm)
        self.is_dev_mode = os.getenv("LOCAL_DEV", "false") == "true"

    def clean_string(self, string):
        return re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z0-9\s]', '', os.path.splitext(string)[0])).lower()
    
    def categorize_image(self, prompt):
        file_metadata = Predict(ImageCategorizer)(prompt=prompt)
        return file_metadata.category

    def generate_image(self, prompt, file_name):
        file_name = self.clean_string(file_name)
        image_input = {
            "prompt": f"{prompt}",
            "guidance": 3.5
        }

        output = replicate.run(
            "black-forest-labs/flux-dev",
            input=image_input
        )

        category = self.clean_string(self.categorize_image(prompt))
        generated_images = []
        remote_category_path = os.path.join(self.storage_path, category)

        # Dev mode: Save both locally and via SSH
        if self.is_dev_mode:
            # First save locally with same path structure
            local_category_path = os.path.join(".", self.storage_path.lstrip('/'), category)
            os.makedirs(local_category_path, exist_ok=True)

            ssh_client = self.ssh_manager.get_client()
            if ssh_client:
                sftp = ssh_client.open_sftp()
                
                try:
                    sftp.stat(remote_category_path)
                except FileNotFoundError:
                    sftp.mkdir(remote_category_path)

                for index, item in enumerate(output):
                    image_data = item.read()
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{file_name}_{timestamp}.webp"
                    
                    # Save locally
                    local_file_path = os.path.join(local_category_path, filename)
                    with open(local_file_path, "wb") as file:
                        file.write(image_data)
                    
                    # Save to remote via SSH
                    image_data_copy = BytesIO(image_data)
                    remote_file_path = os.path.join(remote_category_path, filename)
                    sftp.putfo(image_data_copy, remote_file_path)
                    
                    generated_images.append({
                        "path": os.path.join('/mnt/media_storage/generated', category, filename),
                        "category": category
                    })
                
                sftp.close()
                ssh_client.close()
                return generated_images

        # Production: Save locally only
        os.makedirs(remote_category_path, exist_ok=True)
        
        for index, item in enumerate(output):
            filename = f"{file_name}_{index}.webp"
            file_path = os.path.join(remote_category_path, filename)
            with open(file_path, "wb") as file:
                file.write(item.read())
            generated_images.append({
                "path": os.path.join('/mnt/media_storage/generated', category, filename),
                "category": category
            })
        
        return generated_images
