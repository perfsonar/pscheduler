#
# RPM Spec for Python Module
#

%define short	jq
Name:		%{_pscheduler_python}-%{short}
Version:	1.12.0
Release:	1%{?dist}
Summary:	Python bindings to JQ
BuildArch:	%(uname -m)
License:	BSD 2-Clause
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Michael Williamson
URL:		https://github.com/mwilliamson/jq.py

Source:		%{short}-%{version}.tar.gz

Requires:       %{_pscheduler_python} >= 3.9
Requires:       expat >= 2.4.0
Requires:       jq >= 1.8

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  expat >= 2.4.0
BuildRequires:  libtool
BuildRequires:  jq-devel >= 1.8
BuildRequires:  pscheduler-rpm
BuildRequires:  %{_pscheduler_python} >= 3.9
BuildRequires:  %{_pscheduler_python}-devel >= 3.9
BuildRequires:  %{_pscheduler_python}-Cython
BuildRequires:  %{_pscheduler_python}-setuptools

%description
Python bindings to JQ


# The jq library doesn't have a way to figure this out, and the
# behavior is hard-wired into the command-line program.
%define jq_prog %(command -v jq)
%define jq_bin  %(dirname "%{jq_prog}")
%define jq_lib  %(cd "%{jq_bin}/../lib" && pwd)/jq



# Don't do automagic post-build things.
%global              __os_install_post %{nil}

# Don't need this, either.
%global              debug_package %{nil}

%prep
%setup -q -n %{short}.py-%{version}


%build
JQPY_USE_SYSTEM_LIBS=1 %{_pscheduler_python} setup.py build


%install
JQPY_USE_SYSTEM_LIBS=1 %{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
