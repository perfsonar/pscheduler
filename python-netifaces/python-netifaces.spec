#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	netifaces
Name:		%{_pscheduler_python}-%{short}
Version:	0.10.9
Release:	1%{?dist}
Summary:	Network interface utilities for Python
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Alastair Houghton <alastair@alastairs-place.net>
Url:		https://github.com/al45tair/netifaces

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools

%description
Network interface utilities for Python


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-release_%(echo "%{version}" | tr . _ )



%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install \
    --root=$RPM_BUILD_ROOT \
    --single-version-externally-managed \
    -O1 \
    --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
