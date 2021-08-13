#
# Adapted from the PGDG sources
#

%global debug_package %{nil}

%if 0%{?fedora} || 0%{?rhel} >= 7
%global macros_dir %{_rpmconfigdir}/macros.d
%else
%global macros_dir %{_sysconfdir}/rpm
%endif

%if 0%{?fedora} >= 30 || 0%{?rhel} >= 8
BuildArch:	noarch
%endif

Name:		pgdg-srpm-macros
Version:	1.0.14
Release:	1%{?dist}
Summary:	SRPM macros for building PostgreSQL PGDG Packages

License:	PostgreSQL
URL:		https://yum.PostgreSQL.org/pgdg-srpm-macros
Source0:	%{name}-%{version}.tar.gz


%define macros     macros.pgdg-postgresql
%define copyright  COPYRIGHT
%define authors    AUTHORS

#Source0:	macros.pgdg-postgresql
#Source1:	COPYRIGHT
#Source2:	AUTHORS

%description
A set of macros for building PostgreSQL PGDG packages. 3rd party packagers can
override these macros and use their own.

%prep
%setup


%install
%{__install} -p -D -m 0644 %{macros} %{buildroot}/%{macros_dir}/macros.pgdg-postgresql

%files
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc COPYRIGHT AUTHORS
%else
%license COPYRIGHT
%doc AUTHORS
%endif
%{macros_dir}/macros.pgdg-postgresql

%changelog
* Tue May 18 2021 Devrim Gündüz <devrim@gunduz.org> - 1.0.14-1
- Update PROJ to 8.0.1 and GDAL to 3.2.3.

* Mon Mar 8 2021 Devrim Gündüz <devrim@gunduz.org> - 1.0.13-1
- Update PROJ to 8.0.0, GDAL to 3.2.2 and GeOS to 3.9.1

* Fri Jan 8 2021 Devrim Gündüz <devrim@gunduz.org> - 1.0.12-1
- Introduce pgdg_set_llvm_variables macro, to specify which
  distro/arch combinations have llvm support.

* Wed Jan 6 2021 Devrim Gündüz <devrim@gunduz.org> - 1.0.11-1
- Update GDAL to 3.2.1 and PROJ to 7.2.1

* Sun Dec 20 2020 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.10-1
- Update GeOS to 3.9.0

* Fri Nov 27 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.9-1
- Add custom macros for (supported) PROJ versions. Without this,
  all PROJ packages would install under the same directory, whatever
  the latest version is.

* Thu Nov 5 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.8-1
- Remove libspatialitemajorversion macro definition. Apparently
  conditional does not work in the macro file.
- Update Proj to 7.2.0, GDAL to 3.2.0

* Fri Oct 30 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.7-1
- Add missing libspatialitemajorversion macro.

* Thu Oct 8 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.6-1
- Add IBM Advance Toolchain 12, 13 and 14 support

* Tue Sep 29 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.5-1
- Update libgeotiff to 1.6
- Update GDAL to 3.1.3

* Mon Aug 17 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.4-1
- Update Proj to 7.1.0
- Add AT 11 support

* Mon May 11 2020 John K. Harvey <john.harvey@crunchydata.com> - 1.0.3-2
- Small fix for plpython3 macro for EL-7

* Sun May 10 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.3-1
- Make plpython3 macro consistent with the PostgreSQL spec file.
  Per John K. Harvey.

* Tue May 5 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.2-1
- Update Proj to 7.0.1

* Thu Apr 16 2020 Devrim Gündüz <devrim@gunduz.org> - 1.0.1-1
- Add CXX flags for PPC64LE. Extracted from another patch by Talha.

* Fri May 31 2019 Devrim Gündüz <devrim@gunduz.org> - 1.0.0-1
- Initial packaging for PostgreSQL RPM Repository
