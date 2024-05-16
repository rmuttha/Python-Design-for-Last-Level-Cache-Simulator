# MSD_PROJECT_GRP8
The simulation of the last level cache (LLC) for a new processor
that can be used with up to three other processors in a shared memory configuration.

The cache has a total capacity of 16MB, uses 64-byte lines, and is 8-way set associative. It
employs a write allocate policy and uses the MESI protocol to ensure cache coherence. The
replacement policy is implemented with a pseudo-LRU scheme.

Modeled communication between your LLC and the next higher level cache,
bus operations that your LLC performs, snoop results that your LLC reports on the bus in
response to snooping the simulated bus operations of other processors and their caches.
