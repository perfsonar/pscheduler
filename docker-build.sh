#!/usr/bin/env bash

# Constants
BUILD_DIR=multiarch_build

# Variables
PROJECT=pscheduler
export OS=debian10
export REPO=perfsonar-5.0-snapshot

# To run in Jenkins only
#git clone https://github.com/perfsonar/${PROJECT}.git
#cd ${PROJECT}
#if [ -n "${tag}" ]; then
#  echo "We have a tag, this is a release build."
#  git checkout ${tag}
#else
#  echo "We build from a branch, this is a snapshot build."
#  git checkout ${branch}
#fi

# Launch all containers
ARCHES='linux/amd64 linux/arm64 linux/armv7 linux/ppc64le'
CONTAINERS=""
for ARCH in ${ARCHES[@]}; do
    LARCH=${ARCH#*\/}
    if [[ $LARCH != "amd64" ]]; then
        CONTAINERS+="${OS}_${LARCH} "
    fi
done
docker compose down
docker compose up -d $CONTAINERS
# The amd64 container need to be launched separately as it doesn't run systemd
docker compose run -d --rm ${OS}_amd64

# Prepare the containers
for ARCH in ${ARCHES[@]}; do
    LARCH=${ARCH#*\/}
    LARCH=${LARCH/\/}
    # TODO: can we run all builds in parallel?
    docker compose exec ${OS}_${LARCH} bash -c "\
        curl http://downloads.perfsonar.net/debian/$REPO.gpg.key | apt-key add - && \
        curl -o /etc/apt/sources.list.d/$REPO.list http://downloads.perfsonar.net/debian/$REPO.list && \
        apt-get update \
        "
done

# Make the master build with unibuild (on amd64 container)
#docker compose exec ${OS}_amd64 unibuild build

# Then loop on all packages from the unibuild/build-order file
cd unibuild-repo
mkdir -p $BUILD_DIR
for p in `cat unibuild/build-order`; do
    # Extract source package
    rm -rf $BUILD_DIR/*
    if grep -q '(native)' ../${p}/*/unibuild-packaging/deb/source/format ; then
        echo "This is a Debian native package, there is no orig tarball."
        tar -x -C $BUILD_DIR --strip-components 1 -f ${p}*.tar.xz
    else
        tar -x -C $BUILD_DIR --strip-components 1 -f ${p}*.orig.*
        tar -x -C $BUILD_DIR -f ${p}*.debian.*
    fi

    if grep '^Architecture: ' $BUILD_DIR/debian/control | grep -qv 'Architecture: all'; then
        # We need to build this package for all architectures
        for ARCH in ${ARCHES[@]}; do
            LARCH=${ARCH#*\/}
            LARCH=${LARCH/\/}
            if [[ $LARCH != "amd64" ]]; then
                echo -e "\n===== Building \033[1mbinary package ${p}\033[0m on \033[1m${ARCH}\033[0m in \033[1m${OS}_${LARCH}\033[0m container ====="
                # TODO: can we run all builds in parallel?
                docker compose exec -T ${OS}_${LARCH} bash -c "cd /app/unibuild-repo/$BUILD_DIR/ && mk-build-deps --install --tool 'apt-get --yes --no-install-recommends -o Debug::pkgProblemResolver=yes' --remove"
                docker compose exec -T ${OS}_${LARCH} bash -c "cd /app/unibuild-repo/$BUILD_DIR/ && dpkg-buildpackage -us -uc -i -sa -b"
            fi
        done
    fi
done

# Shutdown all containers
cd ..
docker compose stop ${OS}_amd64
docker compose down

