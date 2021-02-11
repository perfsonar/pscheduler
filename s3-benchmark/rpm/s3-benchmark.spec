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

%define gopath $(pwd)/GOPATH:/usr/lib/golang/src/vendor:/usr/lib/golang/pkg/linux_amd64/vendor
%define gobin %{gopath}/bin
%define gocache %{gopath}/.cache

%prep 
%setup -q -n %{directory}

mkdir -p %{gopath} %{gobin}

export GOPATH=%{gopath}
export GOBIN=%{gobin}
export GOCACHE=%{gocache}

#doesn't work
#go get ./...

go get golang.org/x/net/http2
go get code.cloudfoundry.org/bytefmt
go get github.com/aws/aws-sdk-go/aws
go get github.com/aws/aws-sdk-go/aws/credentials
go get github.com/aws/aws-sdk-go/aws/session
go get github.com/aws/aws-sdk-go/service/s3


%build -n %{directory}
export GOPATH=%{gopath}
export GOBIN=%{gobin}
export GOCACHE=%{gocache}

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
