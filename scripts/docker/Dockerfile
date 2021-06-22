#
# Dockerfile for pScheduler Demo System
#

# NOTE: DO NOT TRY THIS WITH CENTOS 7.  Systemd requires DBus, and all
# of that has to be started.

FROM centos:6

MAINTAINER Mark Feit <mfeit@internet2.edu>

ARG BUILD_NAME

RUN curl -s -O https://raw.githubusercontent.com/perfsonar/pscheduler/master/scripts/install-from-repos
RUN curl -s -O https://raw.githubusercontent.com/perfsonar/pscheduler/master/scripts/docker/docker-run

RUN chmod +x ./install-from-repos
RUN ./install-from-repos ${BUILD_NAME}

RUN install -m 544 docker-run /usr/bin
RUN useradd -c "pScheduler Demo" demo

# TODO: What network ports should be exposed?

# Allow for backups
VOLUME  ["/var/lib/pgsql", "/etc/pscheduler"]

# Set the default command to run when starting the container
CMD ["/usr/bin/docker-run"]
