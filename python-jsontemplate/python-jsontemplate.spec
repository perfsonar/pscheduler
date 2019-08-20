#
# RPM Spec for Python jsontemplate module
#

%define short	jsontemplate
Name:		%{_pscheduler_python}-%{short}
Version:	0.87
Release:	1%{?dist}
Summary:	Template system for JSON
BuildArch:	%(uname -m)
License:	Apache 2.0
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Google
Url:		https://code.google.com/archive/p/json-template

Source:		%{short}-%{version}.tar.gz

Patch0:		%{short}-%{version}-00-2to3.patch


Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools



%description
Template system for JSON



# Don't do automagic post-build things.
%global              __os_install_post %{nil}
%global		     debug_package %{nil}

%prep
%setup -q -n %{short}-%{version}
%patch0 -p1


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
