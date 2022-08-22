#
# RPM Spec for Python Py-Radix
#

%define short	py-radix
Name:		%{_pscheduler_python}-%{short}
Version:	0.9.6
Release:	1%{?dist}
Summary:        Radix tree for Python
BuildArch:	%(uname -m)
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Michael J. Schultz
URL:		https://github.com/mjschultz/py-radix

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	gcc
BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-setuptools
BuildRequires:	%{_pscheduler_python}-devel

%description
A network address manipulation library for Python



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
