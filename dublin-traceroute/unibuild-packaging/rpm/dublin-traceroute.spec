#
# RPM Spec for dublin-traceroute
#

%define short dublin-traceroute
Name:		%{short}
Version:	0.4.2
Release:	1%{?dist}
Summary:	A smarter traceroute
BuildArch:	%(uname -m)
License:	BSD-2-Clause
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Andrea Barberio
Url:		http://www.dublin-traceroute.net

Source:		%{short}-%{version}.tar.gz

Requires:	libpcap
Requires:	libtins
Requires:	jsoncpp
Requires:	openssl

BuildRequires:  cmake
#TODO: They really want this; EL7 doesn't have it.
#BuildRequires:  gcc-c++ >= 4.9
BuildRequires:  gcc-c++
BuildRequires:  libpcap-devel
BuildRequires:  libtins-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  openssl-devel

%description
A smarter traceroute


# Don't need this.
%global debug_package %{nil}


%prep
%setup -q


%build
mkdir build
cd build

# The disabled setcap will be done during installation.
cmake ../ \
    "-DCMAKE_INSTALL_PREFIX=${RPM_BUILD_ROOT}/%{_usr}" \
    "-DSETCAP_EXECUTABLE:FILEPATH=/bin/true"
make


%install
cd build
%makeinstall

# RPM wants it elsewhere.
mv "${RPM_BUILD_ROOT}/%{_usr}/lib" "${RPM_BUILD_ROOT}/%{_libdir}"



%clean
rm -rf %{buildroot}


%post
# Deferred from the build
setcap cap_net_raw+ep %{_bindir}/%{name}



%files
%defattr(-,root,root)
%{_bindir}/*
%{_libdir}/*


#
# Development Subpackage
#

%package -n %{name}-devel
Summary: Header files for %{name} development
Group: Development/Libraries
Provides: %{name}-devel = %{version}-%{release}
Requires: %{name} = %{version}-%{release}

%description -n %{name}-devel
Header files for %{name} development

%files -n %{name}-devel
%defattr(-,root,root)
%{_includedir}/dublintraceroute
