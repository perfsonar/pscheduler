#
# RPM Spec for libtins
#

%define short tins

Name:		lib%{short}
Version:	4.2
Release:	1%{?dist}
Summary:	C++ library for manipulating raw network packets
License:	BSD-2-Clause

BuildArch:	%(uname -m)
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

# Whoever produces this does a good job staying anonymous
# Vendor:		
URL:		http://libtins.github.io/
Source:		%{name}-%{version}.tar.gz

Requires:	libpcap
Requires:	openssl

BuildRequires: cmake
BuildRequires: pkgconfig
BuildRequires: gcc-c++
BuildRequires: libpcap-devel
BuildRequires: openssl-devel


%description
The library's main purpose is to provide the C++ developer an easy,
efficient, platform and endianess-independent way to create tools which
need to send, receive and manipulate specially crafted packets.


%prep
%setup -q


%build
mkdir build
cd build
cmake ../ \
    -DLIBTINS_ENABLE_CXX11=1 \
    "-DCMAKE_INSTALL_PREFIX=${RPM_BUILD_ROOT}/%{_usr}"
make


%install
cd build
%makeinstall

# This is unneeded
rm -rf "${RPM_BUILD_ROOT}/%{_usr}/lib/cmake"

# RPM wants it elsewhere.
mv "${RPM_BUILD_ROOT}/%{_usr}/lib" "${RPM_BUILD_ROOT}/%{_libdir}"

# The build process leaves some paths from the build around.
fgrep -lr "${RPM_BUILD_ROOT}" "${RPM_BUILD_ROOT}" \
      | xargs sed -i -e "s|${RPM_BUILD_ROOT}||g"



%files
%defattr(-,root,root)
%license LICENSE
%{_libdir}/%{name}.so*
%{_libdir}/pkgconfig/*


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
%{_includedir}/%{short}
