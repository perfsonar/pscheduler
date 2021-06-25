#
# RPM Spec for scapy
#

%define short	scapy
Name:		%{_pscheduler_python}-%{short}
Version:	2.4.5
Release:	1%{?dist}
Summary:	Python library for manipulating packets
BuildArch:	noarch
License:	GPL2
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Philippe Biondi
Url:		https://github.com/secdev/scapy

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools



%description 
Python library for manipulating packets





# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES -O1


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
