###############################################################################################
#
# File
#	simple_page.py
#
# Description
#	This is the final child class which parses a file containing page-data recorded in
#	simple format i.e. one page-frame number per line of the file
#
###############################################################################################

import sys

# Add the path of the parent scripts directory to python search path
sys.path.append('/home/wali/work/cat_exp/set_exp/git/cat_exp/second_exp/bench/parser/scripts')

# Now import the parent module
from page import *

class simple_page_file(page_file):
        """ A subclass of page-file which handles page information recorded in simple
            format i.e. one page-frame number per line of the file """

        def parse(self):
                """ This function parses information stored in the page-file """

                # Open the input file
                fdi = open(self.get_name(), 'r')

                # Read all the lines in the input file
                lines = fdi.readlines()

                # Close the input file
                fdi.close()

                # Discard the first line
                lines = lines[1:]

                # Convert each element in the line to integer
                try:
                        pfn_array = [int(pfn) for pfn in lines]
                except:
                        raise ValueError, "Unexpected page-frame number in input file!"

                # Sort the array of page frame numbers
                pages = sorted(pfn_array)

                # Store the page information in input data hash
                page_file.INPUT_DATA['pages'] = pages
                page_file.INPUT_DATA['number'] = len(pages)

                # Calculate the working set size
                ws_size = (float(page_file.PAGE_SIZE_KB) * len(pages)) / 1024

                print 'Working Set Size :', format(ws_size, '0.3f'), 'MB'

                return


def main():
	""" This is the main entry point into this script """
	myFile = simple_page_file('/tmp/pages.log')
	myFile.parse()
	myFile.color_analysis()
	myFile.print_colors()
	myFile.slice_page_analysis()
	myFile.print_slice_pages()
	myFile.slice_block_analysis()
	myFile.print_slice_blocks()

	return

# Declare 'main' as the entry point
if __name__ == "__main__":
	# Call the main function
	main()
