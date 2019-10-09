# CombinePics.py

from PIL import Image

# Function to combine two images into one
def combine(image1, image2, ticker):
    img1 = Image.open(image1)
    img2 = Image.open(image2)

    lar = img1.size[0] + img2.size[0] + 5

    if img1.size[1] < img2.size[1]:
        alt = img2.size[1]
        copy = img1.copy()
        copy2 = img2.copy()
    else:
        alt = img1.size[1]
        copy = img2.copy()
        copy2 = img1.copy()

    if img1.size[0] < img2.size[0]:
        lar_p = lar - img2.size[0]
    else:
        lar_p = lar - img1.size[0]

    lar_p = lar - img2.size[0]
    n_image = Image.new('RGB', (lar, alt), 'white')
    n_image.paste(copy, (0, 0))
    n_image.paste(copy2, (lar_p, 0))
    n_image.save(ticker + "Final.png")

    return
