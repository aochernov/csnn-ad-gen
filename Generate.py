import os, glob, random
from PIL import Image, ImageFilter
import Parse as GT

def GetTree(trees, w, h):
	tree = trees[random.randint(0, len(trees) - 1)]
	template = Image.open(tree)
	W = template.size[0]
	H = template.size[1]
	wd = W / w
	hd = H / h
	new_tree = template.copy()
	new_tree = new_tree.transform((w, h), Image.AFFINE, (wd, 0, 0, 0, hd, 0))
	return new_tree

def DrawTree(image, mask, tree, w, h, wd, hd):
	for i in range(w):
		for j in range(h):
			if tree[i, j] != (0, 0, 0, 0):
				mask[i + wd, j + hd] = (0, 255, 0, 255)
				image[i + wd, j + hd] = tree[i, j]
	return (image, mask)

def Separate(pixels, i, j):
	new_blob = []
	checked = set()
	checked.add((i, j))
	while len(checked) != 0:
		(i, j) = checked.pop()
		if (pixels[i, j] == (0, 255, 0, 255)):
			pixels[i, j] = (0, 0, 255, 255)
			new_blob.append((i, j))
			checked.add((i - 1, j))
			checked.add((i + 1, j))
			checked.add((i, j - 1))
			checked.add((i, j + 1))
		elif (pixels[i, j] == (0, 0, 0, 255)):
			pixels[i, j] = (255, 255, 255, 255)
	return (pixels, new_blob)
	
def Blur(pixels, x, y):
	color = (0, 0, 0)
	for i in range(-5, 6):
		for j in range(-5, 6):
			pix = pixels[x + i, y + j]
			color = (color[0] + pix[0], color[1] + pix[1], color[2] + pix[2])
	new_color = (color[0] // 121, color[1] // 121, color[2] // 121)
	return new_color

def CreateTree(file, trees):
	image = Image.open(file)
	name = os.path.basename(file)
	mask = Image.open("masks/" + name + ".png")
	width = image.size[0]
	height = image.size[1]
	pix = mask.load()
	print(name)
	new_image = image.copy()
	new_mask = mask.copy()
	new_image_pixels = new_image.load()
	new_mask_pixels = new_mask.load()
	for i in range(width):
		for j in range(height):
			if pix[i, j] == (255, 0, 0, 255):
				(blob, pix) = GT.eat(i, j, pix)
				(w, h, w_min, h_min) = GT.get_round_size(blob)
				new_tree = GetTree(trees, w, h)
				tree_pix = new_tree.load()
				(new_image_pixels, new_mask_pixels) = DrawTree(new_image_pixels, new_mask_pixels, tree_pix, w, h, w_min, h_min)
				(new_mask_pixels, new_blob) = Separate(new_mask_pixels, (w // 2) + w_min, (h // 2) + h_min)
				for k in range(len(new_blob)):
					new_mask_pixels[new_blob[k][0], new_blob[k][1]] = (0, 0, 0, 255)
	for i in range(width):
		for j in range(height):
			if new_mask_pixels[i, j] == (255, 0, 0, 255):
				new_mask_pixels[i, j] = (255, 255, 255, 255)
				new_image_pixels[i, j] = Blur(new_image_pixels, i, j)
	return(new_image, new_mask)
	
#def main():
trees = []
for file in glob.glob("trees\*.png"):
	trees.append(file)
images = []
for file in glob.glob("input\*\*.jpg"):
	images.append(file)
number = int(input())
for i in range(number):
	im = images[random.randint(0, len(images) - 1)]
	(new_im, new_mask) = CreateTree(im, trees)
	new_im.save("output/generated_image_" + str(i + 1) + ".jpg", "JPEG")
	new_mask.save("output/generated_image_" +str(i + 1) + ".JPG.hand_mask.png", "PNG")