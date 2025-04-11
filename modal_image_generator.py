import modal
from diffusers import StableDiffusionPipeline

stub = modal.Stub("image_generator")

@stub.function(gpu="T4", image=modal.Image.debian_slim().pip_install("diffusers", "torch", "transformers"))
def generate_image(prompt):
    pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
    image = pipe(prompt).images[0]
    return image