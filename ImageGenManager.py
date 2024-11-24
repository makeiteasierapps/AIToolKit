import replicate
from dspy import LM, configure, InputField, OutputField, Signature, Predict
import os
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
        self.remote_path = '/mnt/media_storage/generated'
        lm = LM(model='openai/gpt-4o-mini')
        configure(lm=lm)

    def categorize_image(self, prompt):
        file_metadata = Predict(ImageCategorizer)(prompt=prompt)
        return file_metadata.category

    def generate_image(self, prompt, file_name):
        image_input = {
            "prompt": f"{prompt}",
            "guidance": 3.5
        }

        output = replicate.run(
            "black-forest-labs/flux-dev",
            input=image_input
        )

        category = self.categorize_image(prompt)

        # Get SSH client
        ssh_client = self.ssh_manager.get_client()
        if ssh_client:
            sftp = ssh_client.open_sftp()

            # Create category directory path
            category_path = os.path.join(self.remote_path, category)
            
            # Check if category directory exists, create if it doesn't
            try:
                sftp.stat(category_path)
            except FileNotFoundError:
                sftp.mkdir(category_path)
            
            generated_images = []
            for index, item in enumerate(output):
                # Read image data into memory
                image_data = BytesIO(item.read())
                
                # Generate filename and full remote path
                filename = f"{file_name}_{index}.webp"
                remote_file_path = os.path.join(category_path, filename)
                
                # Upload file to remote server
                sftp.putfo(image_data, remote_file_path)
                generated_images.append({
                    "path": os.path.join(category, filename), 
                    "category": category
                })
                
            sftp.close()
            ssh_client.close()
            return generated_images
        
        # Fallback to local storage if no SSH connection
        os.makedirs(category_path, exist_ok=True)
        
        generated_images = []
        for index, item in enumerate(output):
            filename = f"{file_name}_{index}.webp"
            file_path = os.path.join(category_path, filename)
            with open(file_path, "wb") as file:
                file.write(item.read())
            generated_images.append({
                "path": os.path.join(category, filename), 
                "category": category
            })
        return generated_images
