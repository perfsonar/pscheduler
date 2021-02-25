#
# RPM Spec for Python Module
#

%define short	pyjq
Name:		%{_pscheduler_python}-%{short}
Version:	2.4.0
Release:	2%{?dist}
Summary:	Python bindings to JQ
BuildArch:	%(uname -m)
License:	BSD 2-Clause
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		OMOTO Kenji
URL:		https://github.com/doloopwhile/pyjq

Source:		%{short}-%{version}.tar.gz
Patch0:		python-%{short}-%{version}-00-nodownloads.patch
Patch1:		python-%{short}-%{version}-01-integer.patch

Requires:       %{_pscheduler_python}
# Note that 1.6.10 is a pScheduler-specific version that includes a
# bug fix required for this module.  See #717.
Requires:       jq >= 1.6.10
Requires:       oniguruma >= 5.9

BuildRequires:  %{_pscheduler_python}
BuildRequires:  %{_pscheduler_python}-setuptools
%if 0%{?el8}
BuildRequires:  %{_pscheduler_python}-Cython >= 0.19
%endif
%if 0%{?el7}
BuildRequires:  Cython >= 0.19
%endif
BuildRequires:  jq-devel >= 1.5
BuildRequires:  oniguruma-devel >= 5.9

%description
Python bindings to JQ


# The jq library doesn't have a way to figure this out, and the
# behavior is hard-wired into the command-line program.
%define jq_prog %(which jq)
%define jq_bin  %(dirname "%{jq_prog}")
%define jq_lib  %(cd "%{jq_bin}/../lib" && pwd)/jq



# Don't do automagic post-build things.
%global              __os_install_post %{nil}


%prep
%setup -q -n %{short}-%{version}
%patch0 -p1
%patch1 -p1


%build
cython _pyjq.pyx
%{_pscheduler_python} setup.py build


%install
%{_pscheduler_python} setup.py install --root=$RPM_BUILD_ROOT -O1  --record=INSTALLED_FILES


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
