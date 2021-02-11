%global srcname Cython
%global upname cython

%bcond_without tests

Name:           Cython
Version:        0.29.21
%global upver %{version}
Release:        4%{?dist}
Summary:        Language for writing Python extension modules

License:        ASL 2.0
URL:            http://www.cython.org
Source:         %{srcname}-%{version}.tar.gz

# Partially work around issues with class and static methods
# See https://bugzilla.redhat.com/show_bug.cgi?id=1788506
# Mostly backported from upstream: https://github.com/cython/cython/pull/3106
# This also:
# - Removes staticmethod optimizations for normal functions
# - Removes failing test for staticmethod fused functions, which still fail
#   See also: https://github.com/cython/cython/issues/3614
#Patch3106:      class-static-method-workaround.patch

BuildRequires:  gcc

%global _description \
This is a development version of Pyrex, a language\
for writing Python extension modules.

%description %{_description}

%package -n python3-%{srcname}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{srcname}}
Conflicts:      python2-%{srcname} < 0.28.4-2
Provides:       Cython = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       Cython%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      Cython < %{?epoch:%{epoch}:}%{version}-%{release}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

# A small templating library is bundled in Cython/Tempita
# Upstream version 0.5.2 is available from https://pypi.org/project/Tempita
# but the bundled copy is patched and reorganized.
# Upstream homepage is inaccessible.
Provides:       bundled(python3dist(tempita))

%description -n python3-%{srcname} %{_description}

Python 3 version.

%package -n emacs-cython-mode
Summary:        A major mode for editing Cython source files in Emacs
BuildArch:      noarch
BuildRequires:  emacs
Requires:       emacs(bin) >= %{_emacs_version}

%description -n emacs-cython-mode
cython-mode is an Emacs major mode for editing Cython source files.

%prep
%autosetup -n %{srcname}-%{upver} -p1

%build
%py3_build

# emacs-cython-mode build
echo ";;
(require 'cython-mode)" > cython-mode-init.el
cp -p Tools/cython-mode.el .
%{_emacs_bytecompile} *.el


%install
%py3_install
rm -rf %{buildroot}%{python3_sitelib}/setuptools/tests

# emacs-cython-mode install
mkdir -p %{buildroot}%{_emacs_sitelispdir}/
cp -p cython-mode.el cython-mode.elc %{buildroot}%{_emacs_sitelispdir}/
mkdir -p %{buildroot}%{_emacs_sitestartdir}/
cp -p cython-mode-init.el cython-mode-init.elc %{buildroot}%{_emacs_sitestartdir}/


%files -n python3-%{srcname}
%license LICENSE.txt
%doc *.txt Demos Tools
%{_bindir}/cython
%{_bindir}/cygdb
%{_bindir}/cythonize
%{python3_sitearch}/%{srcname}-*.egg-info/
%{python3_sitearch}/%{srcname}/
%{python3_sitearch}/pyximport/
%{python3_sitearch}/%{upname}.py
%{python3_sitearch}/__pycache__/%{upname}.*

%files -n emacs-cython-mode
%license LICENSE.txt
%{_emacs_sitelispdir}/cython*.el*
%{_emacs_sitestartdir}/cython*.el*
