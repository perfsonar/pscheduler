# Note about upgrading iperf3

When upgrading iperf3, it's important to confirm that the name of the tarball matches the format `iperf3-[version].tar.gz`, otherwise unibuild will not recognize the presence of the already compressed source.

The name of the tarball downloaded directly from the iperf3 source will likely not be in this format and will need to be renamed to add the 3 after iperf.
