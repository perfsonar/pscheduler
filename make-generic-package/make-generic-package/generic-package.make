#
# Include a package-building Makefile depending on the system's
# packaging model.
#

ifdef BUILD_PATH

include $(BUILD_PATH)/generic-common.make
include $(BUILD_PATH)/generic-$(PACKAGE_FORMAT).make

else

include make/generic-common.make
include make/generic-$(PACKAGE_FORMAT).make

endif
