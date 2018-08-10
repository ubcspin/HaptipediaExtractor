'''
Configure absolute input and output paths for PDF's and PDFFigures2
Make sure to add a '\' at the end of output_dir so that the files go inside the output folder
writeToFile sets whether the extracted data other than fig captions is added to the folder
writeToFile default setting is False
'''

'Example:'

input_dir = r'C:/Users/john_/Desktop/TestPDF/prototype_data'
output_dir = r'C:/Users/john_/Desktop/TestPDF/outputs\\'
pdffigures2_dir = r'C:/Users/john_/Desktop/TestPDF/pdffigures2'
thread_count = '4'
should_init_crossrefs = True
add_to_db = True
writeToFile = False
