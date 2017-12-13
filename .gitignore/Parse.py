import fullImageDistortion as dist, os, glob
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
	for i in range(vertical, width):
		for j in range(horizontal):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i - vertical, j] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i - vertical, j] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	mirror = 0
	for i in range(vertical, width):
		for j in range(horizontal, height):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i - vertical, j] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i - vertical, j] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	mirror = 0
	for i in range(vertical):
		for j in range(horizontal, height):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i, j - horizontal] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i, j - horizontal] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	mirror = 0
	for i in range(vertical, width):
		for j in range(horizontal, height):
			if ((pix[i, j] == (0, 0, 0, 0)) & (pix[i, j - horizontal] != (0, 0, 0, 0))) | ((pix[i, j] != (0, 0, 0, 0)) & (pix[i, j - horizontal] == (0, 0, 0, 0))):
				mirror = mirror + 1
	perc = int(sz * mirror)
	if (perc > threshold):
		return False
	return True

def eat(j, i, matrix):
	blob = []
	eater = set()
	eater.add((j, i))
	while len(eater) != 0:
		(j, i) = eater.pop()
		if matrix[j][i] == 1:
			blob.append((j, i))
			matrix[j][i] = 0
			eater.add((j - 1, i))
			eater.add((j + 1, i))
			eater.add((j, i - 1))
			eater.add((j, i + 1))
	return (blob, matrix)

def get_round_size(blob):
	w = 1000000
	W = 0
	h = 1000000
	H = 0
	for i in range(len(blob)):
		if blob[i][0] < h:
			h = blob[i][0]
		if blob[i][0] > H:
			H = blob[i][0]
		if blob[i][1] < w:
			w = blob[i][1]
		if blob[i][1] > W:
			W = blob[i][1]
	return (W - w + 1, H - h + 1, w, h)

def writeIm(blob, file, W, H, w_min, h_min):
	image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
	pixels = image.load()
	im_pixels = file.load()
	for i in range(len(blob)):
		w = blob[i][1]
		h = blob[i][0]
		pixels[w - w_min, h - h_min] = im_pixels[w, h]
	return image

def colorMask(mask, blob):
	for i in range(len(blob)):
		mask[blob[i][1], blob[i][0]] = (255, 0, 0, 255)
	return mask
	
def GetTree():
	for file in glob.glob("input\*\*.jpg"):
		image = Image.open(file)
		name = os.path.basename(file)
		path, ext = os.path.splitext(file)
		mask = Image.open(path + ".JPG.hand_mask.png")
		width = image.size[0]
		height = image.size[1]
		matrix = [[0 for x in range(width)] for y in range(height)]
		pix = mask.load()
		print(name)
		for i in range(width):
			for j in range(height):
				if (pix[i, j] != (255, 255, 255, 255)) & (pix[i, j] != 1):
					matrix[j][i] = 1
		num = 1
		new_mask = mask.copy()
		new_mask = new_mask.convert("RGBA")
		new_mask_pixels = new_mask.load()
		for i in range(width):
			for j in range(height):
				if matrix[j][i] == 1:
					(blob, matrix) = eat(j, i, matrix)
					(w, h, w_min, h_min) = get_round_size(blob)
					im = writeIm(blob, image, w, h, w_min, h_min)
					if isCircle(im):
						im.save("trees/" + name + "_" + str(num) + ".png", "PNG")
						new_mask_pixels = colorMask(new_mask_pixels, blob)
						num = num + 1
		new_mask.save("masks/" + name + ".png", "PNG")