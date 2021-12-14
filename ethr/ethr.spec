#
# RPM Spec for Ethr
#

%define short ethr
Name:		%{short}
Version:	0.2.1
Release:	1%{?dist}
Summary:	A cross-platform network performance measurement tool
BuildArch:	%(uname -m)
License:	MIT
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Microsoft Corporation
URL:		https://github.com/microsoft/ethr

Source:		%{short}-%{version}.tar.gz

BuildRequires:  golang


%description
Ethr is a cross platform network performance measurement tool written
in golang. The goal of this project is to provide a native tool for
comprehensive network performance measurements of bandwidth,
connections/s, packets/s, latency, loss & jitter, across multiple
protocols such as TCP, UDP, HTTP, HTTPS, and across multiple platforms
such as Windows, Linux and other Unix systems.

%global debug_package %{nil}


%define gopath $(pwd)/GOPATH
%define gobin %{gopath}/bin
%define gocache %{gopath}/.cache

%prep
%setup -q

mkdir -p %{gopath} %{gobin}

export GOPATH=%{gopath}
export GOBIN=%{gobin}
export GOCACHE=%{gocache}

go get ./...



%build
export GOPATH=%{gopath}
export GOBIN=%{gobin}
export GOCACHE=%{gocache}

go build



%install
%{__mkdir_p} %{buildroot}/%{_bindir}
install %{name}-%{version} %{buildroot}/%{_bindir}/%{name}



%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root)
%license LICENSE
%{_bindir}/*
