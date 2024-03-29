#
# RPM Spec for s3-benchmark Tool
#

#

Name:		s3-benchmark
Version:	1.0
Release:	1%{?dist}

Summary:	S3 benchmark tool
BuildArch:	%(uname -m)
License:	Apache 2.0 # find out
Group:		Unspecified

Source0:	%{name}-%{version}-beta.tar.gz

Provides:	%{name} = %{version}-%{release}

# Include all required libraries here

BuildRequires:	golang


%description
S3 benchmark tool for pScheduler

%global debug_package %{nil}

%define directory %{name}-%{version}-beta

%define godir $(pwd)/GOPATH
%define gopath %{godir}:/usr/lib/golang/src/vendor:/usr/lib/golang/pkg/linux_amd64/vendor
%define gobin %{godir}/bin
%define gocache %{godir}/.cache

%prep

rm -rf %{name}-%{version}-beta
%setup -q -n %{directory}


%build -n %{directory}
mkdir -p "%{godir}" "%{gobin}"
export GOPATH="%{gopath}"
export GOBIN="%{gobin}"
export GOCACHE"=%{gocache}"

# Go leaves a bunch of directories read-only, which makes cleaning out
# the workspace difficult.  Make sure that's cleaned up no matter
# what.

mkdir -p "%{godir}"
cleanup()
{
    find "%{godir}" -type d | xargs chmod +w
}
trap cleanup EXIT

%if 0%{?el7}
# EL7 has problems with its git that cause module fetches not to work.
# Use Golang's proxy to do it instead.
export GO111MODULE=on
export GOPROXY="https://proxy.golang.org"
%endif

go mod init wasabi.com/s3-benchmark
go mod tidy
go get ./...

go build s3-benchmark.go


%install
%{__mkdir_p} %{buildroot}/%{_bindir}
install %{name} %{buildroot}/%{_bindir}/%{name}



%clean -n %{directory}
rm -rf %{buildroot}


%files
%defattr(-,root,root)
%license LICENSE
%{_bindir}/*
