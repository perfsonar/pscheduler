#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	Twisted
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	22.4.0
Release:	1%{?dist}
Summary:	Event-based framework for internet applications
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Twisted Matrix
Url:		https://github.com/twisted/constantly

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}
Requires:	%{_pscheduler_python}-attrs >= 19.2.0
Requires:	%{_pscheduler_python}-Automat >= 0.8.0
Requires:	%{_pscheduler_python}-constantly >= 15.1
Requires:	%{_pscheduler_python}-hyperlink >= 17.1.1
Requires:	%{_pscheduler_python}-incremental >= 21.3.0
Requires:	%{_pscheduler_python}-typing_extensions >= 3.6.5
Requires:	%{_pscheduler_python}-zope-interface >= 4.4.2


BuildRequires:	%{_pscheduler_python}-setuptools

%description
Twisted is an event-based framework for internet applications.


# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}



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
