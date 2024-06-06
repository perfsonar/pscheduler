#
# RPM Spec for rpm-post-wrapper
#

Name:		rpm-post-wrapper
Version:	1.0
Release:	1%{?dist}

Summary:	Wrapper for rpm %post scriptlets

BuildArch:	noarch
License:	Apache 2.0
Group:		Utilities/Text
Vendor:		Mark Feit <mfeit@notonthe.net>
URL:		https://github.com/markfeit/drop-in

Source0:	%{name}-%{version}.tar.gz

Provides:	%{name} = %{version}-%{release}

Requires:	perl >= 5.0

%description
rpm-post-wrapper enables RPM %post scriptlets to log errors when they
exit with a non-zero status.  RPM ignores these because it cannot roll
the system state back to what it was.


%prep
%setup -q


%build
make \
     BINDIR=$RPM_BUILD_ROOT/%{_bindir} \
     MANDIR=$RPM_BUILD_ROOT/%{_mandir} \
     install


%clean
make clean

%post
# Eat just a little of our own dog food.
rpm-post-wrapper '%{name}' "$@" <<'POST-WRAPPER-EOF'

  echo 'Greetings from the %{name} %post scriptlet'

  # Un-commenting this won't cause the install to fail but will produce
  # an error message in the log.
  # false

POST-WRAPPER-EOF



%files
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
