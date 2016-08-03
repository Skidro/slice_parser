#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/mman.h>

/* This simple function flushes the given address from the cache heirarchy */
inline void clflush(volatile void *p)
{
	asm volatile ("clflush (%0)" :: "r"(p));
}

/* This function can be used for getting the processor time-stamp */
inline uint64_t rdtsc(void)
{
	unsigned long top, bottom;

	// asm volatile ("cpuid; rdtscp" : "=a" (bottom), "=d" (top) :: "ebx", "ecx");
	asm volatile ("rdtscp" : "=a" (bottom), "=d" (top));

	/* Return the 64-bit time-stamp to the caller */
	return ((uint64_t)top << 32 | bottom);
}

/* Define some convenience macros for dealing with the last level cache */
#define	LLC_SIZE	(15 * 1024 * 1024)
#define BLK_SIZE	64

/* These macros are useful for verifying the functionality of this script */
#define VERIFY_CTL	0

void *g_mem_ptr = NULL;

int main(void)
{
	unsigned long block = 0;

#if (VERIFY_CTL == 1)
	unsigned long test = 0;
	uint64_t t1, t2, t3, t4;
#endif
	
	/* Request a hugetlb memory region which encompasses the entire LLC */
	g_mem_ptr = mmap(0, LLC_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);

	/* Verify that allocation was successful */
	if (g_mem_ptr == MAP_FAILED) {
		perror("Allocation from Huge Page Pool failed. Please verify that hugetlbfs is properly mounted!\n");
		exit(1);
	}

	/* Proceed with the cache flush */
	for (block = 0; block < LLC_SIZE/BLK_SIZE; block += BLK_SIZE) {
		/* Bring the line to the cache */
		*((unsigned long *)(((unsigned long long)g_mem_ptr) + block)) = block;

#if (VERIFY_CTL == 1)
		t1 = rdtsc();
		test = *((unsigned long *)(((unsigned long long)g_mem_ptr) + block));
		t2 = rdtsc();
#endif

		/* Flush the line */
		clflush((void *)(((unsigned long)g_mem_ptr) + block));

#if (VERIFY_CTL == 1)
		t3 = rdtsc();
		test = *((unsigned long *)(((unsigned long long)g_mem_ptr) + block));
		t4 = rdtsc();
		
		// printf("t3 : %llu | t4 : %llu\n", (unsigned long long)t3, (unsigned long long)t4);
		printf("Address	: %p	|	First Attempt : %lu	|	Second Attemp : %lu\n", ((unsigned long *)(((unsigned long long)g_mem_ptr) + block)), (unsigned long)(t2 - t1), (unsigned long)(t4 - t3));
#endif
	}

	/* Unmap the memory region */
	munmap(g_mem_ptr, LLC_SIZE);

	return 0;
}
