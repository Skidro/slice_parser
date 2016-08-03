from generic_page import *
from helper_functions import *

class page_file(File, Helper):
        """ A subclass of generic File type objects. This class is for
            parsing files which contain physical page frame number for
            an application """

        # Initialize the slice dictionary which needs to be populated
        BLOCK_SLICE_HASH = {}
        PAGE_SLICE_HASH = {}
        COLOR_HASH = {}
        INPUT_DATA = {}
        COLOR_MASK = 0x18000
        NUM_OF_SLICES = 6
        PAGE_SIZE_KB = 4
        BLOCK_SIZE = 64

	def __init__(self, filename):
                # Call the super class constructor
                super(page_file, self).__init__(filename)

                # Initialize the hashes
                self.init_hash(self.BLOCK_SLICE_HASH, self.NUM_OF_SLICES)
                self.init_hash(self.PAGE_SLICE_HASH, self.NUM_OF_SLICES)

                # Number of cache-colors is equal to 2 ^ (number of set bits in color mask)
                self.init_hash(self.COLOR_HASH, (1 << len(self.bit_numbers(self.COLOR_MASK))))

	def check_pages_populated(self):
                # Perform basic sanity checks
                if not page_file.INPUT_DATA.has_key('pages'):
                        raise KeyError, "Parser has not been called yet"
                elif not page_file.INPUT_DATA['pages']:
                        raise ValueError, "Input file is empty"

                return

	def init_hash(self, hash, size):
	        """ This function initializes a given hash according to the
	            given size """
	        for item in range(0, size):
	                hash[item] = 0
	        return
	
	def block_map(self, pfn):
	        """ This function takes a page-frame number and calculates the slice
	            mapping of all the cache-lines which fall in its range. In doing
	            so, an assumption as made that all the cache lines are symmetrically
	            accessed """
	
	        # This is calculated on the basis of a 4K page and 64 bytes line size
	        blocks_in_page = 64
	
	        # Make room for block address in page-frame number
	        pfn <<= 6
	
	        for block_index in range(0, blocks_in_page):
	                slice = self.slice_map(pfn + block_index)
	                self.BLOCK_SLICE_HASH[slice] += 1
	
	        return
	
	def page_map(self, pfn):
	        """ This function takes a page-frame number and calculates the slice
	            mapping of its first cache-line """
	
	        # Zero out the cache-line address in page-frame number
	        pfn <<= 6
	
	        slice = self.slice_map(pfn)
	        self.PAGE_SLICE_HASH[slice] += 1
	
	        return
	
	def slice_block_analysis(self):
	        """ This function calculates the slice utilization information on per-block
	            basis """
	
	        # Call the sanity checker
		self.check_pages_populated()
	
	        # Proceed with the analysis
		for page_frame in page_file.INPUT_DATA['pages']:
	                self.block_map(page_frame)
	
	        return
	
	def slice_page_analysis(self):
	        """ This function calculates the slice utilization information on per-page
	            basis """
	
	        # Call the sanity checker
	        self.check_pages_populated()
	
	        # Proceed with the analysis
	        for page_frame in page_file.INPUT_DATA['pages']:
	                self.page_map(page_frame)
	
	        return
	
	def color_analysis(self):
		""" This function calculates the distribution of pages across different
		    cache colors. It can only be called after the page-file has been
		    parsed """
		
		# Call the sanity checker
		self.check_pages_populated()
		
		# Proceed with the analysis
		for page_frame in page_file.INPUT_DATA['pages']:
		        color = 0
		        index = 0
		
		        for bit in self.bit_mask(page_file.COLOR_MASK):
		                if (bit & page_frame):
		                        color |= (1 << index)
		
		                index += 1
		
		        # Record the page against the calculated color in the color hash
		        page_file.COLOR_HASH[color] += 1
		
		return
	
	def print_colors(self):
	        """ This function prints the distribution of pages across colors.
	            It can only be called after the COLOR_HASH has been populated """
	
	        print '\nColor	:	Pages	:	Size (MB)	:	Percentage Utilization'
	        for color in self.COLOR_HASH.keys():
	                print "%d	:	%d	:	%.3f		:	%.3f %%" % (color, self.COLOR_HASH[color],
	                                                                                            self.COLOR_HASH[color] * self.PAGE_SIZE_KB / 1024.0,
	                                                                                            self.COLOR_HASH[color] * 100.0 / self.INPUT_DATA['number'])
	
	        return
	
	def print_slice_blocks(self):
	        """ This function prints the slice utilization information on
	            per-block basis """
	
	        print '\nSlice	:	Blocks	:	Size (KB)	:	Percentage Utilization'
	        for slice in self.BLOCK_SLICE_HASH.keys():
	                print "%d	:	%d	:	%.3f	:	%.3f %%" % (slice, self.BLOCK_SLICE_HASH[slice],
	                                                                                    self.BLOCK_SLICE_HASH[slice] * self.BLOCK_SIZE / 1024.0,
	                                                                                    self.BLOCK_SLICE_HASH[slice] * 100.0 / sum(self.BLOCK_SLICE_HASH.values()))
	
	        return
	
	def print_slice_pages(self):
	        """ This function prints the slice utilization information on
	            per-page basis """
	
	        print '\nSlice	:	Pages	:	Size (KB)	:	Percentage Utilization'
	        for slice in self.PAGE_SLICE_HASH.keys():
	                print "%d	:	%d	:	%.3f	:	%.3f %%" % (slice, self.PAGE_SLICE_HASH[slice],
	                                                                                    self.PAGE_SLICE_HASH[slice] * self.PAGE_SIZE_KB,
	                                                                                    self.PAGE_SLICE_HASH[slice] * 100.0 / sum(self.PAGE_SLICE_HASH.values()))
	
	        return
