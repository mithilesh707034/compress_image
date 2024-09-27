from django.shortcuts import render
from .models import MyImage
from PIL import Image
import io

def home_page(request):
    data=''
    if request.method == "POST":
        image_file = request.FILES.get('image')
        if image_file:
            # Open the uploaded image
            img = Image.open(image_file)

            # Convert image to RGB if necessary (for PNG or other formats)
            if img.mode in ("RGBA", "P"): 
                img = img.convert("RGB")

            # Compress the image
            output_io_stream = io.BytesIO()
            img.save(output_io_stream, format='JPEG', quality=60)  # You can adjust the quality (0-100)
            output_io_stream.seek(0)

            # Save the compressed image to your model
            mi = MyImage()
            mi.image.save(image_file.name, output_io_stream, save=False)
            mi.save()
            data=mi.image

    return render(request, 'index.html',{'data':data})
import cv2
import numpy as np
from PIL import Image
import io
from django.shortcuts import render
from .models import MyImage

def remove_watermark(request):
    data = ''
    if request.method == "POST":
        image_file = request.FILES.get('image')
        if image_file:
            # Open the uploaded image using PIL
            img = Image.open(image_file)

            # Convert to OpenCV format (numpy array)
            img_cv = np.array(img)

            # If the image has an alpha channel (transparency), remove it
            if img_cv.shape[2] == 4:  # Check if it's RGBA
                img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2RGB)

            # Convert image to grayscale to detect watermark
            gray_img = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

            # Adjust the color range to target white watermark (high RGB values close to 255)
            lower_val = np.array([230, 230, 230])  # Lower bound for detecting white
            upper_val = np.array([255, 255, 255])  # Upper bound for detecting white

            # Create a mask based on the color range (detect white parts of the watermark)
            mask = cv2.inRange(img_cv, lower_val, upper_val)

            # **Expand the mask**: Use dilation followed by erosion to better cover the watermark
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=5)  # Increase size of the mask
            mask = cv2.erode(mask, kernel, iterations=0)   # Shrink back to original size

            # Inpainting to remove the watermark using the mask
            inpainted_img = cv2.inpaint(img_cv, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

            # Convert the result back to a PIL image
            result_image = Image.fromarray(inpainted_img)

            # Map extensions to formats supported by PIL (make everything lowercase)
            extension = image_file.name.split('.')[-1].lower()
            format_mapping = {
                'jpg': 'jpeg',
                'jpeg': 'jpeg',
                'png': 'png',
                'bmp': 'bmp',
                'gif': 'gif',
            }

            # Check if the extension is valid
            image_format = format_mapping.get(extension)
            if not image_format:
                return render(request, 'index.html', {'error': 'Unsupported file format.'})

            # Save the processed image in the original format
            output_io_stream = io.BytesIO()
            result_image.save(output_io_stream, format=image_format)
            output_io_stream.seek(0)

            # Save the image to your model
            mi = MyImage()
            mi.image.save(image_file.name, output_io_stream, save=False)
            mi.save()

            data = mi.image

    return render(request, 'index.html', {'data': data})


# import pywhatkit
# def send_auto_bulk_whatsapp_message():
#     number=["+917009679903","+919056225284"]
#     for item in number:
#         pywhatkit.sendwhatmsg_instantly(phone_no=item,message="This is Test Message",wait_time=15,tab_close=True,close_time=3)
# send_auto_bulk_whatsapp_message()


# import pandas as pd
# import pywhatkit
# from django.shortcuts import render
# from django.core.exceptions import ValidationError
# import os

# def send_auto_bulk_whatsapp_message(request):
#     if request.method == "POST":
#         file = request.FILES.get('file')
#         message = request.POST.get('message')

#         # Check if the file is a valid CSV or Excel file
#         if file:
#             try:
#                 # Ensure the file extension is either .csv or .xlsx
#                 if file.name.endswith('.csv'):
#                     df = pd.read_csv(file)  # Read CSV file
#                 elif file.name.endswith('.xlsx'):
#                     df = pd.read_excel(file)  # Read Excel file
#                 else:
#                     return render(request, 'whatsapp-form.html', {'error': 'File type not supported. Please upload a CSV or Excel file.'})

#                 # Ensure your file has a column with phone numbers
#                 if 'PhoneNumber' not in df.columns:
#                     return render(request, 'whatsapp-form.html', {'error': 'PhoneNumber column is missing in the file.'})

#                 number = df['PhoneNumber'].tolist()  # Extract phone numbers

#                 for item in number:
#                     item = "+91"+str(item)  # Strip any whitespace
#                     if item:  # Check if the phone number is not empty
#                         print("Number: ",item)
#                         # Send WhatsApp message
#                         pywhatkit.sendwhatmsg_instantly(phone_no=item, message=message, wait_time=15, tab_close=True, close_time=3)

#                 return render(request, 'whatsapp-form.html', {'success': True})

#             except (ValidationError, ValueError) as e:
#                 return render(request, 'whatsapp-form.html', {'error': f'Error processing file: {str(e)}'})
#             except Exception as e:
#                 return render(request, 'whatsapp-form.html', {'error': f'An error occurred: {str(e)}'})

#     return render(request, 'whatsapp-form.html')

import pandas as pd
import pywhatkit
from django.shortcuts import render
from django.core.exceptions import ValidationError
import bleach  # Import bleach to clean HTML

def send_auto_bulk_whatsapp_message(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        message = request.POST.get('message')

        # Clean the HTML message to plain text
        message = bleach.clean(message, strip=True)  # Strips HTML tags

        if file:
            try:
                # Ensure the file extension is either .csv or .xlsx
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    return render(request, 'whatsapp-form.html', {'error': 'Invalid file format. Please upload a .csv or .xlsx file.'})

                for index, row in df.iterrows():
                    number = row['Phone']
                    number = "+91" + str(number)  # Format phone number
                    if number:  # Check if the phone number is not empty
                        print("Number: ", number)
                        # Send WhatsApp message
                        pywhatkit.sendwhatmsg_instantly(phone_no=number, message=message)
               
                return render(request, 'whatsapp-form.html', {'success': True})

            except (ValidationError, ValueError) as e:
                return render(request, 'whatsapp-form.html', {'error': f'Error processing file: {str(e)}'})
            except Exception as e:
                return render(request, 'whatsapp-form.html', {'error': f'An error occurred: {str(e)}'})

    return render(request, 'whatsapp-form.html')

# import pandas as pd
# import pywhatkit
# from django.shortcuts import render
# from django.core.exceptions import ValidationError
# import time  # Import time for sleep functionality

# def send_auto_bulk_whatsapp_message(request):
#     if request.method == "POST":
#         file = request.FILES.get('file')
#         message = request.POST.get('message')

#         # Check if the file is a valid CSV or Excel file
#         if file:
#             try:
#                 # Ensure the file extension is either .csv or .xlsx
#                 if file.name.endswith('.xlsx'):
#                     df = pd.read_excel(file)  # Read Excel file
#                 else:
#                     return render(request, 'whatsapp-form.html', {'error': 'Only .xlsx files are supported.'})

#                 # Check if the phone numbers column exists
#                 if 'PhoneNumber' not in df.columns:
#                     return render(request, 'whatsapp-form.html', {'error': 'PhoneNumber column is missing in the file.'})

#                 numbers = df['PhoneNumber'].tolist()  # Extract phone numbers

#                 for number in numbers:
#                     number = "+91" + str(number).strip()  # Format phone number
#                     if number:  # Check if the phone number is not empty
#                         try:
#                             print("Sending message to: ", number)
#                             # Send WhatsApp message
#                             pywhatkit.sendwhatmsg_instantly(phone_no=number, message=message, wait_time=15, tab_close=True)
#                             time.sleep(30)  # Wait for a longer time before sending the next message
#                         except Exception as e:
#                             print(f"Error sending message to {number}: {str(e)}")
#                             break  # Break out of the loop if there is an error

#                 return render(request, 'whatsapp-form.html', {'success': True})

#             except (ValidationError, ValueError) as e:
#                 return render(request, 'whatsapp-form.html', {'error': f'Error processing file: {str(e)}'})
#             except Exception as e:
#                 return render(request, 'whatsapp-form.html', {'error': f'An error occurred: {str(e)}'})

#     return render(request, 'whatsapp-form.html')
