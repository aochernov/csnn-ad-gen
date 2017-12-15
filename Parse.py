import os, glob
from PIL import Image

def isCircle(image):
	threshold = 9
	width = image.size[0]
	height = image.size[1]
	Min = min(width, height)
	Max = max(width, height)
	pix = image.load()
	if ((Min / Max) < 0.85) | (width < 10) | (height < 10):
		return False
	vertical = width // 2
	horizontal = height // 2
	sz = 100 / (height * width)
	mirror = 0
	for j in range(horizontal):
		for i in range(vertical, width):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i - vertical, j] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i - vertical, j] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	mirror = 0
	for j in range(horizontal, height):
		for i in range(vertical, width):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i - vertical, j] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i - vertical, j] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	mirror = 0
	for j in range(horizontal, height):
		for i in range(vertical):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i, j - horizontal] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i, j - horizontal] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	mirror = 0
	for j in range(horizontal, height):
		for i in range(vertical, width):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i, j - horizontal] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i, j - horizontal] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	mirror = 0
	mirror_alt = 0
	for j in range(height):
		for i in range(width):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[width - 1 - i, height - 1 - j] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[width - 1 - i, height - 1 - j] == (0, 0, 0, 0))):
				mirror = mirror + 1
			if ((pix[width - 1 - i, j] == (0, 0, 0, 0)) & (pix[i, height - 1 - j] != (0, 0, 0, 0))) | ((pix[width - 1 - i, j] != (0, 0, 0, 0)) & (pix[i, height - 1 - j] == (0, 0, 0, 0))):
				mirror_alt = mirror_alt + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	perc = int(sz * mirror_alt)
	if (perc > threshold):
		return False
	return True

def eat(i, j, pix):
	blob = []
	eater = set()
	eater.add((i, j))
	while len(eater) != 0:
		(i, j) = eater.pop()
		if pix[i, j] != (255, 255, 255, 255):
			blob.append((i, j))
			pix[i, j] = (255, 255, 255, 255)
			eater.add((i - 1, j))
			eater.add((i + 1, j))
			eater.add((i, j - 1))
			eater.add((i, j + 1))
	return (blob, pix)

def get_round_size(blob):
	w = 1000000
	W = 0
	h = 1000000
	H = 0
	for i in range(len(blob)):
		if blob[i][1] < h:
			h = blob[i][1]
		if blob[i][1] > H:
			H = blob[i][1]
		if blob[i][0] < w:
			w = blob[i][0]
		if blob[i][0] > W:
			W = blob[i][0]
	return (W - w + 1, H - h + 1, w, h)

def writeIm(blob, file, W, H, w_min, h_min):
	image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
	pixels = image.load()
	im_pixels = file.load()
	for i in range(len(blob)):
		w = blob[i][0]
		h = blob[i][1]
		pixels[w - w_min, h - h_min] = im_pixels[w, h]
	return image

def colorMask(mask, blob, color):
	for i in range(len(blob)):
		mask[blob[i][0], blob[i][1]] = color
	return mask
	
def GetTree(file):
	image = Image.open(file)
	name = os.path.basename(file)
	path, ext = os.path.splitext(file)
	mask = Image.open(path + ".JPG.hand_mask.png")
	mask = mask.convert("RGBA")
	width = image.size[0]
	height = image.size[1]
	pix = mask.load()
	print(name)
	num = 1
	checkers_num = 1
	new_mask = mask.copy()
	new_mask_pixels = new_mask.load()
	for j in range(height):
		for i in range(width):
			if pix[i, j] != (255, 255, 255, 255):
				(blob, pix) = eat(i, j, pix)
				(w, h, w_min, h_min) = get_round_size(blob)
				im = writeIm(blob, image, w, h, w_min, h_min)
				if isCircle(im):
					im.save("trees/" + name + "_" + str(num) + ".png", "PNG")
					new_mask_pixels = colorMask(new_mask_pixels, blob, (255, 0, 0, 255))
					num = num + 1
	return new_mask
	
def main():
	for file in glob.glob("input\*\*.jpg"):
		new_mask = GetTree(file)
		name = os.path.basename(file)
		new_mask.save("masks/" + name + ".png", "PNG")
		
if __name__ == "__main__":
	main()