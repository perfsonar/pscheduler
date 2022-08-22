Name: nuttcp
Version: 8.2.2
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.bz2
URL: ftp://ftp.lcp.nrl.navy.mil/pub/nuttcp/
Summary: Tool for testing TCP connections
Group: Applications/Internet
License: Open Source

BuildRequires: gcc

%description
nuttcp is a network performance measurement tool intended for use by
network and system managers.  Its most basic usage is to determine the
raw TCP (or UDP) network layer throughput by transferring memory buffers
from a source system across an interconnecting network to a destination
system, either transferring data for a specified time interval, or
alternatively transferring a specified number of buffers.  In addition
to reporting the achieved network throughput in Mbps, nuttcp also
provides additional useful information related to the data transfer
such as user, system, and wall-clock time, transmitter and receiver
CPU utilization, and loss percentage (for UDP transfers).

%global debug_package %{nil}

%prep
%setup -q
sed -i -e "s,/usr/local/bin,%{_bindir},g;" xinetd.d/*

%build
# no smp flags required; only one source file
OPT="$RPM_OPT_FLAGS" make

%install
rm -fr $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT{%{_mandir}/man8,%{_bindir},%{_sysconfdir}/xinetd.d}
install -m755 %{name}-%{version} $RPM_BUILD_ROOT%{_bindir}/%{name}
install -pm644 %{name}.8 $RPM_BUILD_ROOT%{_mandir}/man8
install -pm644 xinetd.d/%{name} $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d/

%clean
rm -fr $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README examples.txt nuttcp.html xinetd.d/nuttcp4 xinetd.d/nuttcp6
%{_bindir}/%{name}
%{_mandir}/man8/*
%config(noreplace) %{_sysconfdir}/xinetd.d/%{name}

%changelog
* Thu Nov 10 2016 Dan Doyle <daldoyle@globalnoc.iu.edu> - 8.1.4-1
- 8.1.4 update 

* Fri Sep 23 2016 Dan Doyle <daldoyle@globalnoc.iu.edu> - 8.1.3-1
- 8.1.3 update 

* Wed May 05 2010 Aaron Brown <aaron@internet2.edu> - 6.1.2-1
- 6.1.2 update 

* Tue Jun 06 2006 Rob Scott <rob@hpcmo.hpc.mil> - 5.3.1-1
- 5.3.1 update 

* Wed Feb 22 2006 Radek Vokál <rvokal@redhat.com> - 5.1.11-6
- rebuilt 

* Wed Feb 08 2006 Radek Vokál <rvokal@redhat.com> - 5.1.11-5
- rebuilt

* Mon Nov 28 2005 Radek Vokal <rvokal@redhat.com> - 5.1.11-4
- remove debuglist files from tarball
- make gcc happier, warnings clean-up

* Tue Nov 22 2005 Radek Vokal <rvokal@redhat.com> - 5.1.11-3
- spec file clean up by Adrian Reber <adrian@lisas.de>
- added a URL
- removed wrong URL from Source
- fixed summary according to guidlines
- removed bogus build require
- disabled xinetd services
- using correct path in xinetd files
- removed unnecessary checks for BUILD_ROOT
- replaced /etc with macro
- added noreplace flag to %config

* Mon Nov 21 2005 Radek Vokal <rvokal@redhat.com> - 5.1.11-2
- add xinetd.d service
- removed some unnecessary files from tarball

* Mon Nov 21 2005 Radek Vokal <rvokal@redhat.com> - 5.1.11-1
- initial built
