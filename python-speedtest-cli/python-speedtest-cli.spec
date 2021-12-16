#
# RPM Spec for speedtest-cli
#

%define short	speedtest-cli
Name:		%{_pscheduler_python}-%{short}
Version:	2.1.3
Release:	1%{?dist}
Summary:	Python library for running ookla speedtest
BuildArch:	noarch
License:	ASL2
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Matt Martz
Url:		https://github.com/sivel/speedtest-cli

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools



%description 
Python library for running ookla speedtest





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
