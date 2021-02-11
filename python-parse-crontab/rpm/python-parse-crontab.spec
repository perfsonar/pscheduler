#
# RPM Spec for Python isodate Module
#

%define short	parse-crontab
Name:		%{_pscheduler_python}-%{short}
Version:	0.22.6
Release:	1%{?dist}
Summary:	Python library for parsing crontab entries
BuildArch:	noarch
License:	LGPL 2/3
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Josiah Carlson
Url:		https://github.com/josiahcarlson/parse-crontab

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools



%description
This module parses crontab time entries and calculates when the next
time the job should be run.




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
