'''
Configure absolute input and output paths for PDF's and PDFFigures2
Make sure to add a '\' at the end of output_dir so that the files go inside the output folder
writeToFile sets whether the extracted data is organized into folders, if not, it's added into device objects
writeToFile default setting is False
'''

'Example:'

input_dir = r'C:\Users\john_\Desktop\Projects\Haptipedia\inputs'
output_dir = r'C:\Users\john_\Desktop\Projects\Haptipedia\outputs\\'

# input_dir = r'C:\Users\john_\Desktop\TestPDF\inputs'
# output_dir = r'C:\Users\john_\Desktop\TestPDF\outputs\\'
pdffigures2_dir = r'C:\Users\john_\Desktop\Projects\Haptipedia\pdffigures2'
writeToFile = True