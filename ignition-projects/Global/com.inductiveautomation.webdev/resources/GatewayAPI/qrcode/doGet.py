def doGet(request, session):
	# import libraries for creating a barcode
	import java.io.ByteArrayOutputStream
	import javax.imageio.ImageIO
	
	# get code info from a URL like:
	# http://localhost:8088/main/system/webdev/QRGenerator/qrcode?width=150&height=150&code=XXX
	# version -1 means auto, positive numbers mean different types of barcodes
	code = request['params'].get('code')
	width = request['params'].get('width', 400)
	height = request['params'].get('height', 400)
	version = request['params'].get('version', -1)
	# generate the code using a script library in this project
	qr_img = qrlib.generateQrCode(code, int(width), int(height), int(version))
	# create an output stream
	baos = java.io.ByteArrayOutputStream()
	javax.imageio.ImageIO.write(qr_img, "jpg", baos)
	# return the byte array as an image
	return {
		'bytes': baos.toByteArray(),
		'contentType': 'image/jpeg'
	}