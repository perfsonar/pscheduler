#
# Dockerfile for pScheduler Demo System
#

# NOTE: DO NOT TRY THIS WITH CENTOS 7.  Systemd requires DBus, and all
# of that has to be started.

FROM centos:6

MAINTAINER Mark Feit <mfeit@internet2.edu>

RUN yum -y install git
RUN git clone https://github.com/perfsonar/pscheduler.git
RUN sed -i -e 's/^ADD_BACKPLANE_HOSTS/#ADD_BACKPLANE_HOSTS/' pscheduler/scripts/system-prep
RUN pscheduler/scripts/system-prep
RUN make -C pscheduler
RUN install -m 544 pscheduler/scripts/docker/docker-run /usr/bin
RUN useradd -c "pScheduler Demo" demo

# TODO: What network ports should be exposed?

# Allow for backups
VOLUME  ["/var/lib/pgsql", "/etc/pscheduler-api-server", "/etc/pscheduler-database"]


# Set the default command to run when starting the container
CMD ["/usr/bin/docker-run"]
