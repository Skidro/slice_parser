########################################################################################
#
# File 
# 	generic_parser.py
#
# Description
#	This file contains python classes for parsing different types of files
#
########################################################################################

import os
import sys

class File(object):
	""" A simple class for handling files """
	def __init__(self, filename = 'Nill'):
		if os.path.isfile(filename):
			self.name = filename
		else:
			raise ValueError, 'File (%s) does not exists!' % (filename)

		return

	def __str__(self):
		return self.name

	def parse(self):
		raise ValueError, 'Parser not implemented'

	def get_name(self):
		return self.name

class Helper(object):
	""" This class defines helper functions to be used by other classes """
	def bit_mask(self, number):
		""" A generator function which returns the set bits in a number
		    in their original positions iteratively. This is a very
		    efficient implementation """
		while(number):
			# This line extracts the first set bit in the number
			set_bit = number & (~number + 1)

			# Return the set bit to the user
			yield set_bit

			# Reset the bit for the next iteration
			number ^= set_bit

		return

	def bit_numbers(self, number):
		""" A function which returns the digit value of set bit positions
		    in a number """
		bit_list = []
		
		# Iterate over the set bits in the number
		index = 0
		for bits in self.bit_mask(number):
			bits >>= index
			while (bits):
				bits >>= 1
				index += 1
			bit_list.append(index-1)

		return bit_list

	def slice_map(self, address):
		""" This function takes the physical address of a memory access and calculates
		    the cache-slice that the physical address belongs to. The hash function for
		    calculating this slice-map is extracted from the paper 'Mapping Intel Last
		    Level Cache' by Y.Yarom et. al"""
		
		address |= (1 << 30)
		
		# Transform the address into bits
		addr_array = [int(bit) for bit in bin(address)[2:]]
	
		# Calculate the first level slice map
		I0 = addr_array[0] ^ addr_array[6]  ^ addr_array[11] ^ addr_array[12] ^ addr_array[16] ^ addr_array[18] ^ addr_array[21] ^ addr_array[23] ^ addr_array[24] ^ addr_array[26]
	
		I1 = addr_array[1] ^ addr_array[6]  ^ addr_array[7]  ^ addr_array[11] ^ addr_array[13] ^ addr_array[16] ^ addr_array[17] ^ addr_array[18] ^ addr_array[19] ^ addr_array[21] ^ addr_array[22] ^ addr_array[25] ^ addr_array[26] ^ addr_array[27]
	
		I2 = addr_array[2] ^ addr_array[7]  ^ addr_array[8]  ^ addr_array[12] ^ addr_array[14] ^ addr_array[17] ^ addr_array[18] ^ addr_array[19] ^ addr_array[20] ^ addr_array[22] ^ addr_array[26] ^ addr_array[27] ^ addr_array[28]
	
		I3 = addr_array[3] ^ addr_array[8]  ^ addr_array[9]  ^ addr_array[13] ^ addr_array[15] ^ addr_array[18] ^ addr_array[19] ^ addr_array[20] ^ addr_array[21] ^ addr_array[23] ^ addr_array[27] ^ addr_array[28]
	
		I4 = addr_array[4] ^ addr_array[9]  ^ addr_array[10] ^ addr_array[14] ^ addr_array[16] ^ addr_array[19] ^ addr_array[20] ^ addr_array[21] ^ addr_array[22] ^ addr_array[24] ^ addr_array[28]
	
		I5 = addr_array[5] ^ addr_array[10] ^ addr_array[11] ^ addr_array[15] ^ addr_array[17] ^ addr_array[20] ^ addr_array[21] ^ addr_array[22] ^ addr_array[23] ^ addr_array[25]
	
		I6 = addr_array[6] ^ addr_array[7]  ^ addr_array[8]  ^ addr_array[9]  ^ addr_array[10] ^ addr_array[12] ^ addr_array[13] ^ addr_array[14] ^ addr_array[15] ^ addr_array[18] ^ addr_array[19] ^ addr_array[20] ^ addr_array[22] ^ addr_array[24] ^ addr_array[25]
	
		# Calculate the second level slice map
		S2 = (I0 ^ I5) and (I2 or I3 and (I4 or I5))
		S1 = I1 and not(S2)
		S0 = I0 ^ I1 ^ I2 ^ I3 ^ I4 ^ I6
	
		# Finally, calculate the slice number
		slice_num = (S2 << 2) | (S1 << 1) | S0
	
		return slice_num


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

	def print_colors(self):
		""" This function prints the distribution of pages across colors.
		    It can only be called after the COLOR_HASH has been populated """
		
		print '\nColor	:	Pages	:	Size (MB)	:	Percentage Utilization'
		for color in self.COLOR_HASH.keys():
			print "%d	:	%d	:	%.3f    	:	%.3f %%" % (color, self.COLOR_HASH[color],
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

	def check_pages_populated(self):
		# Perform basic sanity checks
		if not page_file.INPUT_DATA.has_key('pages'):
			raise KeyError, "Parser has not been called yet"
		elif not page_file.INPUT_DATA['pages']:
			raise ValueError, "Input file is empty"

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
		

myFile = simple_page_file('/tmp/pages.log')
myFile.parse()
myFile.color_analysis()
myFile.print_colors()
myFile.slice_page_analysis()
myFile.print_slice_pages()
myFile.slice_block_analysis()
myFile.print_slice_blocks()
