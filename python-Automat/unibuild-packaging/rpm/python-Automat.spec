#
# RPM Spec for a Python Module
#

# DEBIAN:  This may need to be packaged for Debian

%define short	Automat
%define long	python-%{short}
Name:		%{_pscheduler_python}-%{short}
Version:	20.2.0
Release:	1%{?dist}
Summary:	Self-service finite-state machines for the programmer on the go.
BuildArch:	%(uname -m)
License:	MIT
Group:		Development/Libraries

Provides:	%{name} = %{version}-%{release}
Prefix:		%{_prefix}

Vendor:		Glyph <glyph@twistedmatrix.com>
Url:		https://github.com/glyph/Automat

Source:		python-%{short}-%{version}.tar.gz

Requires:	%{_pscheduler_python}

BuildRequires:	%{_pscheduler_python}-setuptools

%description
Automat is a library for concise, idiomatic Python expression of
finite-state automata (particularly deterministic finite-state
transducers).


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
