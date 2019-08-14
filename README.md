# Whole Slide Images
Pre-Processing Scripts
---------------
### 1. Converting svs to jpeg
See code/convert_sprue_data.py for some code to convert images from svs into jpg. This uses OpenSlide and takes a while. How much you want to compress images will depend on the resolution that they were originally scanned, but a guideline that has worked for us is 3-5 MB per WSI. You can compress the image sizes by changing the compression_factor in the code.

### 2. Generating overlay grids for annotations





