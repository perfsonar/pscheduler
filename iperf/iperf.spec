#
# Adapted from the EPEL package
#

Name: iperf
Version: 2.0.13
Release: 1%{?dist}
Summary: Measurement tool for TCP/UDP bandwidth performance
License: BSD
Group: Applications/Internet
URL: http://sourceforge.net/projects/iperf2
Source: %{name}-%{version}.tar.gz
Patch0: iperf-2.0.8-debuginfo.patch
BuildRequires: autoconf gcc-c++

%description
Iperf is a tool to measure maximum TCP bandwidth, allowing the tuning of
various parameters and UDP characteristics. Iperf reports bandwidth, delay
jitter, datagram loss.


# Don't bulid a debug package

%global debug_package %{nil}




%prep
%setup -q
%patch0 -p1

%build
%{__autoconf}
%configure
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%make_install

%files
%doc AUTHORS ChangeLog COPYING README doc/*.gif doc/*.html
%{_bindir}/iperf
%{_mandir}/man*/*

%changelog
* Wed Jan 23 2019 Gabriel Somlo <somlo at cmu.edu> 2.0.13-1
- update to 2.0.13 (#1668455)

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 11 2018 Gabriel Somlo <somlo at cmu.edu> 2.0.12-[2..4]
- restore specfile cleanup changes (#1599922)
- add buildrequires gcc-c++

* Tue Jul 03 2018 Gabriel Somlo <somlo at cmu.edu> 2.0.12-1
- update to 2.0.12 (#1595235)

* Fri May 25 2018 Gabriel Somlo <somlo at cmu.edu> 2.0.11-1
- update to 2.0.11 (#1582496)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 23 2017 Gabriel Somlo <somlo at cmu.edu> 2.0.10-1
- update to 2.0.10 (#1356228)

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.8-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.8-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.8-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Mar 16 2016 Gabriel Somlo <somlo at cmu.edu> 2.0.8-6
- math header include fix for gcc6 from git 2.0.9 release candidate (# 1307641)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Apr 10 2015 Gabriel Somlo <somlo at cmu.edu> 2.0.8-1
- update to 2.0.8
- update source URL in spec file
- rebase debuginfo and bindfail fixup patches
- added patch to prevent error on installing manpage

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Jan 03 2014 Gabriel Somlo <somlo at cmu.edu> 2.0.5-11
- patch to exit on port bind failure (#1047172, #1047569)

* Sun Dec 22 2013 Gabriel Somlo <somlo at cmu.edu> 2.0.5-10
- added patch to build with format security enabled (#1037132)

* Tue Aug 06 2013 Gabriel Somlo <somlo at cmu.edu> 2.0.5-9
- fix debuginfo regression (#925592)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri May 10 2013 Gabriel Somlo <somlo at cmu.edu> 2.0.5-7
- added autoconf step to support aarch64 (#925592)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 28 2011 Gabriel Somlo <somlo at cmu.edu> 2.0.5-3
- include man page with build (BZ 756794)

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Aug 21 2010 Gabriel Somlo <somlo at cmu.edu> 2.0.5-1
- update to 2.0.5

* Tue Dec 01 2009 Gabriel Somlo <somlo at cmu.edu> 2.0.4-4
- patched to current svn trunk to address performance issues (#506884)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jan 21 2009 Gabriel Somlo <somlo at cmu.edu> 2.0.4-1
- update to 2.0.4
- patch to avoid tcp/dualtest server from quitting (bugzilla #449796), also submitted to iperf sourceforge ticket tracker (#1983829)

* Sat Oct 27 2007 Gabriel Somlo <somlo at cmu.edu> 2.0.2-4
- replace usleep with sched_yield to avoid hogging CPU (bugzilla #355211)

* Mon Jan 29 2007 Gabriel Somlo <somlo at cmu.edu> 2.0.2-3
- patch to prevent removal of debug info by ville.sxytta(at)iki.fi

* Fri Sep 08 2006 Gabriel Somlo <somlo at cmu.edu> 2.0.2-2
- rebuilt for FC6MassRebuild

* Wed Apr 19 2006 Gabriel Somlo <somlo at cmu.edu> 2.0.2-1
- initial build for fedora extras (based on Dag Wieers SRPM)
- fixed license tag: BSD (U. of IL / NCSA), not GPL
