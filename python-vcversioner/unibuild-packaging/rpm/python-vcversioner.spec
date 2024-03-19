#
# RPM Spec for repoze.lru
#

%define short	vcversioner
Name:		%{_pscheduler_python}-%{short}
Version:	2.16.0.0
Release:	1%{?dist}
Summary:	Python version extractor
BuildArch:	noarch
License:	ISC
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Aaron Gallagher
URL:		https://github.com/habnabit/vcversioner 

Source:		%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}
BuildRequires:	%{_pscheduler_python}-setuptools


%description
Python version extractor



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
