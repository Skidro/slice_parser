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
