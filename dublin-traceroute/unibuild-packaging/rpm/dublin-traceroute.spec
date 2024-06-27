#
# RPM Spec for dublin-traceroute
#

%define short dublin-traceroute
Name:		%{short}
Version:	0.4.2
Release:	2%{?dist}
Summary:	A smarter traceroute
BuildArch:	%(uname -m)
License:	BSD-2-Clause
Group:		Applications/System

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Andrea Barberio
Url:		http://www.dublin-traceroute.net

Source:		%{short}-%{version}.tar.gz

# RPM does bad things with this.
AutoReqProv: no

Requires:	libpcap
Requires:	libtins
Requires:	jsoncpp
Requires:	openssl
Requires:	rpm-post-wrapper

BuildRequires:  cmake
BuildRequires:  gcc-c++ >= 4.9
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
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'
# Deferred from the build
setcap cap_net_raw+ep %{_bindir}/%{name}
POST-WRAPPER-EOF



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
