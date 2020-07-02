#
# RPM Spec for Python Module
#

%define short	pyasn1-modules
Name:		%{_pscheduler_python}-%{short}
Version:	0.2.4
Release:	1%{?dist}
Summary:	ASN1 modules for Python
BuildArch:	%(uname -m)
License:	BSD
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Provides:	%{_pscheduler_python}-%{short} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Ilya Etingof <etingof@gmail.com>
URL:		https://github.com/etingof/pyasn1

Source:		%{short}-%{version}.tar.gz

Requires:       %{_pscheduler_python}
Requires:       %{_pscheduler_python}-pyasn1 >= 0.4.5

BuildRequires:  %{_pscheduler_python}
BuildRequires:  %{_pscheduler_python}-setuptools

%description
ASN1 modules for Python



# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global		     debug_package %{nil}


%prep
%setup -q -n %{short}-%{version}


%build
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install \
    --root=$RPM_BUILD_ROOT \
    -O1 \
    --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
