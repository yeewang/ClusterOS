# spec file for the Samba package
# packaged by SerNet Samba Team <Samba@SerNet.de>
# http://www.enterprisesamba.org/
%define oldname samba3

%define samba_ver       4.2.12
%define release_base    22

# Use epoch 98 for testing/rc/beta packages and
# 99 for stable releases.
%define pkg_epoch	99

############################################
# detect the distribution here
############################################

%define		releasefile	%(ls /etc/SuSE-release /etc/UnitedLinux-release /etc/sles-release /etc/redhat-release 2>/dev/null | head -n1)
%define         local_distribution      %(head -n1 < %{releasefile} || echo some SUSE-flavour ... )

%define		this_is_redhat  %(test -e /etc/redhat-release && echo 1 || echo 0)

%if %(echo "%{local_distribution}" | grep -q "UnitedLinux" && echo 1 || echo 0 )
%define		suse_ver	81
%else
%if %(echo "%{local_distribution}" | grep -q "SUSE LINUX Enterprise Server 9" && echo 1 || echo 0 )
%define		suse_ver	91
%else
%if %(echo "%{local_distribution}" | grep -q -i "SUSE Linux Enterprise Server 10" && echo 1 || echo 0 )
%define		suse_ver	101
%else
%if %(echo "%{local_distribution}" | grep -q -i "SUSE Linux Enterprise Server 11" && echo 1 || echo 0 )
%define		suse_ver	111
%else
%if %(echo "%{local_distribution}" | grep -q -i "SUSE Linux Enterprise Server 12" && echo 1 || echo 0 )
%define		suse_ver	132
%else
%define		suse_ver	%(grep "^VERSION" %{releasefile} | sed "s/[^0-9]//g")
%endif
%endif
%endif
%endif
%endif

%if %{this_is_redhat} > 0
%define		rhel_ver	%(grep "release" %{releasefile} | sed "s/^[^0-9]*\\([0-9]*\\).*/\\1/g")
%define		suse_ver	0
%define		smbvendor	SerNet-RedHat
%define		dist		el%{rhel_ver}
%else
%define		rhel_ver	0
%define		smbvendor	SerNet-SuSE
%define		ul_version 	%(test -e /etc/UnitedLinux-release && echo 1 || echo 0)
%if %{ul_version} >= 1
%define		smbvendor	SerNet-UL
%define		suse_ver	81
%endif
%define		dist		suse%{suse_ver}
%endif # %{suse}

# choose some features / extra packages here
############################################

%define         make_dmapi      %{?_with_dmapi: 1} %{?!_with_dmapi: 0}
%define         dmapi_fullversion %{?_with_dmapi_fullversion: 1} %{?!_with_dmapi_fullversion: 0}

%define		make_devel 	0
#TODO: fix docs
%define		with_man	1

%define		make_gpfs	1
%define		patch_gpfs_h	1

%if %{this_is_redhat} > 0
%define		manual_debuginfo_build 0
%else
# temporarily disable debuginfo packages for openSUSE >= 11.2
%define         manual_debuginfo_build  %(test %{suse_ver} -ge 112 ; echo $?)
%endif # %{suse}

# winbind krb5 locator (needs MIT 1.5 or heimdal 1(?)
%if %(test %{suse_ver} -ge 102 -o %{rhel_ver} -ge 5 && echo 1 || echo 0)
%define	build_krb5_locator	1
%else
%define	build_krb5_locator	0
%endif

%define		py_sitedir	%(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(plat_specific=1))")

%define make_srcrpm %{?_with_srcrpm: 1} %{?!_with_srcrpm: 0}
%if %{make_srcrpm}
%define release_full %{release_base}
%define release_full32 %{release_base}
%else
%define release_full_dist %{release_base}.%{dist}
%if %{make_dmapi}
%define release_full %{release_full_dist}.dmapi
%if %{dmapi_fullversion}
# only if --with dmapi_fullversion is also specified we
# include the .dmapi string in the conflict for -32bit libraries
%define release_full32 %{release_full}
%else
%define release_full32 %{release_full_dist}
%endif
%else
%define release_full %{release_full_dist}
%define release_full32 %{release_full_dist}
%endif
%endif

############################################
Name:		sernet-samba
License:	GPL v3 or later
Group:		Productivity/Networking/Samba
Url:		http://www.samba.org
Vendor:		SerNet GmbH, Goettingen
Distribution:	%{local_distribution}
Packager:	SerNet Samba Team <Samba@SerNet.DE>
Provides:	samba
Obsoletes:	samba-classic samba-ldap samba %{oldname}
Obsoletes:	samba-common-tools
# on sles11 (and maybe others) there's a samba-32bit with pam_smbpass.so,
# without this samba-32bit is installed without a need
Obsoletes:	samba-32bit
Autoreqprov:	on
Version:	%{samba_ver}
Release:	%{release_full}
Epoch:		%{pkg_epoch}
%define build_version %{epoch}:%{version}-%{release_full}
%define build_version32 %{epoch}:%{version}-%{release_full32}
Requires:	%{name}-client = %{build_version}
Requires:	/lib/lsb/init-functions
%define		_default_patch_fuzz 2
Summary:	SerNet Samba SMB/CIFS file, print and authentication server
BuildRoot:	%{_tmppath}/%{name}-%{version}-build
Source:		http://ftp.samba.org/pub/samba/stable/samba-%{version}.tar.gz
Source1:	%{name}-files-2011-08-04.tar.bz2
Source4:	smbprngenpdf
Source5:	%{name}.reg
Source13:	%{name}-find-debuginfo.sh
Source14:	sernet-samba-ad.init
Source15:	sernet-samba-nmbd.init
Source16:	sernet-samba-smbd.init
Source17:	sernet-samba-winbindd.init
Source18:	sernet-samba.default
Source19:	sernet-samba-ctdbd.init

Patch171:	%{name}-gpfs_gpl-02.patch
Patch173:	fix-libarchive.patch

Conflicts:	ctdb < %{build_version}
Conflicts:	ctdb > %{build_version}

Patch202:	0001-samba-tool-disable-deprecation-warnings.patch
Patch209:	0001-Revert-s4-lib-tls-fix-build-with-gnutls-3.4.patch
Patch210:	samba-4.2-bug11910.patch
Patch211:	samba-4.2_bug11912.patch
Patch212:	samba-4.4_4.3_4.2-bug11914.patch

BuildConflicts: ctdb ctdb-devel libctdb-devel

BuildConflicts: talloc-devel, libtalloc-devel, pytalloc, python-talloc
BuildConflicts: tevent-devel, libtevent-devel, pytevent, python-tevent
BuildConflicts: tdb-devel, libtdb-devel, pytdb, python-tdb
BuildConflicts: ntdb-devel, libntdb-devel, pyntdb, python-ntdb
BuildConflicts: ldb-devel, libldb-devel, pyldb, python-ldb

BuildRequires:  tar gzip bzip2
BuildRequires:  perl
BuildRequires:  python-devel >= 2.5, python-devel < 3.0
BuildRequires:	make gcc util-linux lsof file findutils gawk

BuildRequires:	cups-devel readline-devel openssl-devel ncurses-devel cyrus-sasl-devel pam-devel e2fsprogs-devel libarchive-devel

%if %{this_is_redhat}
BuildRequires: libacl-devel libattr-devel coreutils
BuildRequires: openldap-devel gnutls-devel
%if %(test %{rhel_ver} -ge 6 && echo 1 || echo 0)
BuildRequires: popt-devel libuuid-devel
%endif
%else
# start of SUSE stuff:
BuildRequires:	popt-devel openldap2-devel glibc-locale
BuildRequires:	coreutils libacl-devel libattr-devel
BuildRequires:	python-xml
%if %(test %{suse_ver} -le 131 && echo 1 || echo 0 )
BuildRequires:	fam-devel
BuildRequires:	xfsprogs-devel
%endif
%if %(test %{suse_ver} -ge 92 && echo 1 || echo 0 )
BuildRequires:	libnscd-devel
%endif
%if %(test %{suse_ver} -ge 100 && echo 1 || echo 0 )
BuildRequires:	libcom_err
%endif
%if %(test %{suse_ver} -ge 101 && echo 1 || echo 0 )
BuildRequires:	libiniparser-devel
%endif
%if %(test %{suse_ver} -ge 110 && echo 1 || echo 0 )
BuildRequires:	libgnutls-devel
%else
BuildRequires:	gnutls-devel
%endif
# end of SUSE stuff
%endif

###
################################
# define some global directories
################################

%define		PERL_VENDORLIB	%(/usr/bin/perl -MConfig -e 'print $Config{vendorlib};')

%define		DOCDIR 		%{_defaultdocdir}/%{name}
%define		LOGDIR 		%{_localstatedir}/log/samba
%define		LIBDIR 		%{_libdir}/samba
%define		STATEDIR 	%{_localstatedir}/lib/samba
%define		CACHEDIR 	%{_localstatedir}/cache/samba
%define		CONFIGDIR 	%{_sysconfdir}/samba
%if %{this_is_redhat} < 1
%define		INITDIR 	%{_sysconfdir}/init.d
%else
%define		INITDIR 	%{_sysconfdir}/rc.d/init.d
%endif
%define		PIDDIR	 	%{_localstatedir}/run/samba
#TODO %define		vfs_modules_common	vfs_audit,vfs_cap,vfs_catia,vfs_cacheprime,vfs_commit,vfs_expand_msdfs,vfs_extd_audit,vfs_fake_perms,vfs_netatalk,vfs_prealloc,vfs_recycle,vfs_streams_depot,vfs_aio_fork
%define		vfs_modules_common	vfs_audit,vfs_cap,vfs_catia,vfs_cacheprime,vfs_expand_msdfs,vfs_extd_audit,vfs_fake_perms,vfs_netatalk,vfs_recycle,vfs_streams_depot,vfs_aio_fork,vfs_snapper
%define		idmap_shared_modules	,idmap_rid,idmap_autorid,idmap_rfc2307,idmap_ad,idmap_tdb2,idmap_hash
#Builtin idmap modules: idmap_tdb idmap_passdb idmap_nss idmap_ldap

%if %{this_is_redhat} < 1
%if %(test %{suse_ver} -gt 111 -a %{suse_ver} -le 131 && echo 1 || echo 0 )
%define		vfs_notify_fam	,vfs_notify_fam
%endif
%endif

%if %{make_dmapi}
%define		vfs_tsmsm	,vfs_tsmsm
%endif

%if %{make_gpfs}
%define		vfs_gpfs	,vfs_gpfs
%endif

%define		shared_modules %{vfs_modules_common}%{?vfs_notify_fam}%{?vfs_gpfs}%{?idmap_shared_modules}%{?vfs_tsmsm}

%package common
Summary:	SerNet Samba Common Files
Autoreqprov:	on
Provides:	%{oldname}-doc
Obsoletes:	%{oldname}-doc
Group:		Productivity/Networking/Samba

%package libs
Summary:	SerNet Samba Common Library Files
Autoreqprov:	on
Requires:	%{name}-common = %{build_version}
Group:		Productivity/Networking/Samba
# sles11 has pam_smbpass in 'samba'
Obsoletes:	samba
Obsoletes:	%{name}-libpam-smbpass < 4.0.10-7
# rhel6 has nss_winbind and pam_winbind here:
Obsoletes:	samba-winbind-clients
Provides:	samba-winbind-clients
Obsoletes:	samba-winbind
# sles11 has libnss_wins in samba-client
Obsoletes:	samba-client
Obsoletes:	libwbclient0
Obsoletes:	libwbclient
Provides:	libwbclient0 = %{build_version}
Provides:	libwbclient = %{build_version}
Obsoletes:	%{name}-libwbclient0 < 4.0.10-7
Obsoletes:	%{oldname}-winbind
# RHEL 7 has nsswitch and pam modules in samba-winbind-modules:
Obsoletes:	samba-winbind-modules
# RHEL 7 provides samba-libs package with /usr/lib64/samba/*.so
# But for now we don't provide 'samba-libs'
Obsoletes:	samba-libs
Obsoletes:	samba-common-libs
Obsoletes:	samba-client-libs
%if %{build_krb5_locator}
Obsoletes:	samba-winbind-krb5-locator
%endif
# RHEL 6 provides samba4-libs package with /usr/lib64/samba/*.so
Obsoletes:	samba4-libs
Obsoletes:	samba-dc
Obsoletes:	samba-dc-libs
#append:baselib.conf:
#append:baselib.conf:sernet-samba-libs
#append:baselib.conf:package /^sernet-samba-libs$/
#append:baselib.conf:obsoletes "samba-32bit"
#append:baselib.conf:obsoletes "samba-libs-32bit"
#append:baselib.conf:obsoletes "samba4-libs-32bit"
#append:baselib.conf:obsoletes "samba-client-32bit"
#append:baselib.conf:obsoletes "samba-winbind-32bit"
#append:baselib.conf:obsoletes "samba-winbind-clients-32bit"
#append:baselib.conf:obsoletes "samba3-winbind-32bit"
#append:baselib.conf:obsoletes "samba-winbind-32bit"
#append:baselib.conf:obsoletes "sernet-samba-libpam-smbpass-32bit < 4.0.10-7"
#append:baselib.conf:obsoletes "sernet-samba-libwbclient0-32bit < 4.0.10-7"
#append:baselib.conf:obsoletes "libwbclient0-32bit"
#append:baselib.conf:obsoletes "libwbclient-32bit"
#append:baselib.conf:provides "libwbclient0-32bit = %{epoch}:%{version}-%{release}"
#append:baselib.conf:provides "libwbclient-32bit = %{epoch}:%{version}-%{release}"
#append:baselib.conf:provides "samba-winbind-clients-32bit = %{epoch}:%{version}-%{release}"
#append:baselib.conf:

%package client
Summary:	SerNet Samba Client Utilities
Autoreqprov:	on
Requires:	%{name}-libs = %{build_version}
%if %{this_is_redhat}
Obsoletes:	samba-common
Provides:	samba-common = %{build_version}
%else
Obsoletes:	samba-classic-client samba-ldap-client
Requires:	glibc-locale
%endif
Obsoletes:	samba-common-tools
Provides:	samba-client = %{build_version}
Provides:	%{oldname}-utils = %{build_version}
Provides:	smbclnt
Obsoletes:	samba-client
# on sles11 (and maybe others) there's a samba-client-32bit with libnss_wins,
# without this samba-client-32bit is installed without a need
Obsoletes:	samba-client-32bit
Obsoletes:	%{oldname}-client
Obsoletes:	%{oldname}-utils
Obsoletes:	tdb-tools ntdb-tools
Provides:	tdb-tools ntdb-tools
Obsoletes:	samba-test
Obsoletes:	samba-test-libs
Group:		Productivity/Networking/Samba

%package winbind
Summary:	SerNet Samba winbind daemon and tool
Obsoletes:	%{oldname}-winbind
Obsoletes:	samba-winbind
Provides:	samba-winbind
Autoreqprov:	on
Group:		Productivity/Networking/Samba
Requires:	%{name}-libs = %{build_version}
Requires:	%{name}-client = %{build_version}
Requires:	/lib/lsb/init-functions
Conflicts:	libwbclient0 < %{build_version}
Conflicts:	libwbclient0 > %{build_version}
Conflicts:	libwbclient0-32bit < %{build_version32}
Conflicts:	libwbclient0-32bit > %{build_version32}
Conflicts:	libwbclient < %{build_version}
Conflicts:	libwbclient > %{build_version}
Conflicts:	libwbclient-32bit < %{build_version32}
Conflicts:	libwbclient-32bit > %{build_version32}

%package libwbclient-devel
License:	GPL v3 or later
Summary:	Libraries and Header Files to Develop Programs with wbclient Support
Group:		Productivity/Networking/Samba
AutoReqProv:	on
Obsoletes:	libwbclient-devel
Provides:	libwbclient-devel = %{build_version}
Requires:	%{name}-libs = %{build_version}

%description libwbclient-devel
This package contains the static libraries and header files needed to
develop programs which make use of the wbclient programming interface.

%package libsmbclient0
Obsoletes:	libsmbclient
Provides:	libsmbclient = %{build_version}
Obsoletes:	libsmbclient0
Provides:	libsmbclient0 = %{build_version}
Summary:	SerNet Samba client library
Autoreqprov:	on
Group:		System/Libraries
#append:baselib.conf:
#append:baselib.conf:sernet-samba-libsmbclient0
#append:baselib.conf:package /^sernet-samba-libsmbclient0$/
#append:baselib.conf:obsoletes "libsmbclient-32bit"
#append:baselib.conf:provides "libsmbclient-32bit = %{epoch}:%{version}-%{release}"
#append:baselib.conf:obsoletes "libsmbclient0-32bit"
#append:baselib.conf:provides "libsmbclient0-32bit = %{epoch}:%{version}-%{release}"
#append:baselib.conf:

%package libsmbclient-devel
Summary:	SerNet Samba header files to develop programs with smbclient support
Autoreqprov:	on
Requires:	%{name}-libs = %{build_version}
Group:		Development/Libraries/C and C++
Obsoletes:	libsmbclient-devel
Provides:	libsmbclient-devel = %{build_version}
Requires:	%{name}-libsmbclient0 = %{build_version}

%package ad
Summary:	SerNet Samba AD domain controller
Autoreqprov:	on
%define pyver %(python -c "import sys; print sys.version[:3]" || echo 0)
Requires:	python >= %pyver, python < %pyver.99
Requires:	%{name} = %{build_version}
Requires:	%{name}-libs = %{build_version}
Requires:	%{name}-client = %{build_version}
Requires:	%{name}-winbind = %{build_version}
Requires:	/lib/lsb/init-functions
# TODO require a specific version with "nsupdate -g"
Requires:	bind-utils
Conflicts:	libwbclient0 < %{build_version}
Conflicts:	libwbclient0 > %{build_version}
Conflicts:	libwbclient0-32bit < %{build_version32}
Conflicts:	libwbclient0-32bit > %{build_version32}
Conflicts:	libwbclient < %{build_version}
Conflicts:	libwbclient > %{build_version}
Conflicts:	libwbclient-32bit < %{build_version32}
Conflicts:	libwbclient-32bit > %{build_version32}
Conflicts:	krb5-server
Obsoletes:	pytalloc, python-talloc
Obsoletes:	pytevent, python-tevent
Obsoletes:	pytdb, python-tdb
Obsoletes:	pyntdb, python-ntdb
Obsoletes:	pyldb, python-ldb
Obsoletes:	samba-python
Provides:	samba-python
%if %{this_is_redhat}
Conflicts:	openldap-servers
%else
Conflicts:	openldap2
%endif
Obsoletes:	ldb-tools
Provides:	ldb-tools
Obsoletes:	samba-test
Obsoletes:	samba-dc
Group:		Productivity/Networking/Samba

%package ctdb
Summary:	SerNet Clustered TDB
Group:		Productivity/Networking/CTDB
Autoreqprov:	on
Obsoletes:	ctdb
Provides:	ctdb = %{build_version}
Requires:	%{name}-libs = %{build_version}
Requires:	gawk

%package ctdb-tests
Summary:	SerNet Clustered TDB tests
Group:		Development/Testing
Autoreqprov:	on
Obsoletes:	ctdb-tests
Provides:	ctdb-tests = %{build_version}
Requires:	%{name}-ctdb = %{build_version}
Requires:	%{name}-libs = %{build_version}

%if %{manual_debuginfo_build}
%package debuginfo
Summary: 	SerNet debug information for package %{name}
Group: Development/Debug
AutoReqProv: 0
Obsoletes:	%{oldname}-debuginfo
Conflicts:	%{name}-common < %{build_version}, %{name}-common > %{build_version}
Conflicts:	%{name}-libs < %{build_version}, %{name}-libs > %{build_version}
Conflicts:	%{name}-client < %{build_version}, %{name}-client > %{build_version}
Conflicts:	%{name}-winbind < %{build_version}, %{name}-winbind > %{build_version}
Conflicts:	%{name}-libsmbclient0 < %{build_version}, %{name}-libsmbclient0 > %{build_version}
Conflicts:	%{name}-ad < %{build_version}, %{name}-ad > %{build_version}
Conflicts:	%{name} < %{build_version}, %{name} > %{build_version}

%description debuginfo
This package provides debug information for package %{name}.
Debug information is useful when developing applications that use this
package or when debugging this package.

%files debuginfo -f debugfiles.list
%defattr(-,root,root)

%endif # manual_debuginfo_build
#append:baselib.conf:
#append:baselib.conf:sernet-samba-debuginfo
#append:baselib.conf:

%prep

%if %{make_srcrpm}
echo "ERROR: Don't use --with srcrpm while building binaries"
exit 1
%endif

set
echo manual debuginfo: %{manual_debuginfo_build}
echo this is redhat: %{this_is_redhat}
echo suse_ver: %{suse_ver}
echo rhel_ver: %{rhel_ver}
echo make_dmapi: %{make_dmapi}

%setup -n samba-%{version}

# untar my configs
%setup -T -D -a 1 -n samba-%{version}

###########
### PATCHES
###########

# Patches up today, whatever that is :-)
%if %{patch_gpfs_h}
%patch171 -p1
%endif

%patch173 -p1

%patch202 -p1

%if %{this_is_redhat} < 1
%if %(test %{suse_ver} -lt 110 && echo 1 || echo 0 )
# revert fix for bug #8780 since older gnu tls version do not provide gnutls_priority_set_direct()
%patch209 -p1
%endif
%endif

%patch210 -p1
%patch211 -p1
%patch212 -p1

cp VERSION VERSION.orig
sed \
	-e 's/^SAMBA_VERSION_VENDOR_SUFFIX=.*$/SAMBA_VERSION_VENDOR_SUFFIX=\"%{smbvendor}-%{release}\"/' \
 < VERSION.orig > VERSION


%build
export RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed "s/i386/i586/g;s/i486/i586/g"`

export CFLAGS="-g -fstack-protector-all -D_FORTIFY_SOURCE=2"
export LDFLAGS="-fstack-protector-all"

%if %{make_devel}
# debugging symbols
export CFLAGS="$CFLAGS -O0"
%else
export CFLAGS="$CFLAGS -O1"
%endif

%ifarch ppc64
export CFLAGS="$CFLAGS -mminimal-toc"
%endif

PATH_OPTS="\
	--enable-fhs \
	--with-lockdir=%{_localstatedir}/cache/samba \
	--prefix=%{_prefix} \
	--exec-prefix=%{_exec_prefix} \
	--bindir=%{_bindir} \
	--sbindir=%{_sbindir} \
	--sysconfdir=%{_sysconfdir} \
	--datadir=%{_datadir} \
	--includedir=%{_includedir} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--localstatedir=%{_localstatedir} \
	--sharedstatedir=%{_sharedstatedir} \
	--mandir=%{_mandir} \
	--infodir=%{_infodir} \
	--with-pammodulesdir=/%{_lib}/security \
"

BUILD_OPTS="\
	--disable-rpath-install \
	--bundled-libraries=ALL \
%if %{make_devel}
	--enable-developer \
	--picky-developer \
	--enable-krb5developer \
%endif
"

CONF_OPTS="\
	--with-libarchive \
	--enable-cups \
	--enable-gnutls \
	--with-acl-support \
	--with-aio-support \
	--with-automount \
	--with-pam \
	--with-pam_smbpass \
	--without-profiling-data \
	--with-quotas \
	--with-syslog \
	--with-utmp \
	--with-winbind \
	--with-ads \
	--with-dnsupdate \
	--with-cluster-support \
	--enable-glusterfs \
%if %{make_dmapi}
	--with-dmapi \
%else
	--without-dmapi \
%endif
	--with-shared-modules=%{shared_modules} \
"

./configure $PATH_OPTS $BUILD_OPTS $CONF_OPTS

# suse 112 missed to export fallocate64 - let's tune config.h here:
%ifarch i386 i486 i586 i686 ppc s390
%if %{suse_ver} == 112
perl -pi -e 's/^.*HAVE_LINUX_FALLOCATE.*//' bin/default/include/config.h
%endif
%endif

make -j

for test in HAVE_POSIX_ACLS HAVE_SETXATTR HAVE_CUPS HAVE_LIBPAM HAVE_LDAP HAVE_KRB5 HAVE_GNUTLS HAVE_LIBARCHIVE
do
	echo -n "testing for $test: "
	if ! `./bin/smbd -b | grep -q $test ` ; then
		echo "ERROR: $test not in smbd! Build stopped."
		exit 1
	fi
	echo "OK"
done

%install
[ $RPM_BUILD_ROOT = "/" ] && (echo "your buildroot is /" && exit 0) || rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT

# make -j hangs on openSUSE 12.1 (at least i386)
# in [ 127/4112] Linking default/lib/replace/libreplace.inst.so
# when called from our build scripts.
%if %{suse_ver} >= 121
make install DESTDIR=${RPM_BUILD_ROOT}
%else
make -j install DESTDIR=${RPM_BUILD_ROOT}
%endif

mkdir -p \
	$RPM_BUILD_ROOT/%{DOCDIR} \
	$RPM_BUILD_ROOT/%{_sysconfdir}/pam.d \
	$RPM_BUILD_ROOT/%{_sysconfdir}/default \
	$RPM_BUILD_ROOT/%{INITDIR} \
	$RPM_BUILD_ROOT/%{_localstatedir}/adm \
	$RPM_BUILD_ROOT/%{LOGDIR} \
	$RPM_BUILD_ROOT/%{STATEDIR}/{netlogon,drivers,printing,profiles} \
	$RPM_BUILD_ROOT/%{CACHEDIR} \
	$RPM_BUILD_ROOT/%{PIDDIR} \
	$RPM_BUILD_ROOT/%{_mandir}/man{1,5,7,8} \
	$RPM_BUILD_ROOT/%{_sysconfdir}/openldap/schema/

%if %{with_man}
# We (currently) want to install the pre-built manpages
# shipped with the source tarball.
# Waf may have built and installed manual pages.
# Remove those:
rm -f $RPM_BUILD_ROOT/%{_mandir}/*/*
# Now copy the pre-built man pages manually:
cp docs/manpages/*.1 $RPM_BUILD_ROOT/%{_mandir}/man1/
cp docs/manpages/*.5 $RPM_BUILD_ROOT/%{_mandir}/man5/
cp docs/manpages/*.7 $RPM_BUILD_ROOT/%{_mandir}/man7/
cp docs/manpages/*.8 $RPM_BUILD_ROOT/%{_mandir}/man8/
rm $RPM_BUILD_ROOT/%{_mandir}/man1/{log2pcap.1,vfstest.1}
%endif

%if %{suse_ver} >= 90
mkdir -p $RPM_BUILD_ROOT/%{_libdir}/cups/backend/
mkdir -p $RPM_BUILD_ROOT/var/lock/subsys
%endif

%if %{build_krb5_locator}
	mkdir -p ${RPM_BUILD_ROOT}/%{_libdir}/krb5/plugins/libkrb5
	mv ${RPM_BUILD_ROOT}/%{_libdir}/winbind_krb5_locator.so ${RPM_BUILD_ROOT}/%{_libdir}/krb5/plugins/libkrb5
%else
	rm ${RPM_BUILD_ROOT}/%{_libdir}/winbind_krb5_locator.so
	rm ${RPM_BUILD_ROOT}/%{_mandir}/man7/winbind_krb5_locator.7
%endif

# We do not want to expose any developement headers or libraries
# except wbclient and smbclient
mv ${RPM_BUILD_ROOT}/%{_includedir}/samba-4.0/wbclient.h ${RPM_BUILD_ROOT}/%{_includedir}
mv ${RPM_BUILD_ROOT}/%{_includedir}/samba-4.0/libsmbclient.h ${RPM_BUILD_ROOT}/%{_includedir}
rm -r ${RPM_BUILD_ROOT}/%{_includedir}/samba-4.0
rm -r ${RPM_BUILD_ROOT}/%{_libdir}/pkgconfig
rm ${RPM_BUILD_ROOT}/%{_libdir}/mit_samba.so # TODO: move to the correct location
mv ${RPM_BUILD_ROOT}/%{_libdir}/libnss_*.so* ${RPM_BUILD_ROOT}/%{_lib}/
mv ${RPM_BUILD_ROOT}/%{_libdir}/*.so* ${RPM_BUILD_ROOT}/%{LIBDIR}
mv ${RPM_BUILD_ROOT}/%{LIBDIR}/libwbclient.so* ${RPM_BUILD_ROOT}/%{_libdir}
mv ${RPM_BUILD_ROOT}/%{LIBDIR}/libsmbclient.so* ${RPM_BUILD_ROOT}/%{_libdir}

# We do not want to expose pidl
rm ${RPM_BUILD_ROOT}/%{_bindir}/pidl
rm -f ${RPM_BUILD_ROOT}/%{_mandir}/man1/pidl.1*
rm -f ${RPM_BUILD_ROOT}/%{_mandir}/man3/Parse::Pidl::Dump.3pm*
rm -f ${RPM_BUILD_ROOT}/%{_mandir}/man3/Parse::Pidl::NDR.3pm*
rm -f ${RPM_BUILD_ROOT}/%{_mandir}/man3/Parse::Pidl::Util.3pm*
rm -f ${RPM_BUILD_ROOT}/%{_mandir}/man3/Parse::Pidl::Wireshark::Conformance.3pm*
rm -f ${RPM_BUILD_ROOT}/%{_mandir}/man3/Parse::Pidl::Wireshark::NDR.3pm*
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/CUtil.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Compat.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Dump.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Expr.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/IDL.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/NDR.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/ODL.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba3/ClientNDR.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba3/ServerNDR.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/COM/Header.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/COM/Proxy.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/COM/Stub.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/Header.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/NDR/Client.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/NDR/Parser.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/NDR/Server.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/Python.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/TDR.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Samba4/Template.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Typelist.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Util.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Wireshark/Conformance.pm
rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Pidl/Wireshark/NDR.pm

test -e ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Yapp/Driver.pm && {
	rm ${RPM_BUILD_ROOT}/%{PERL_VENDORLIB}/Parse/Yapp/Driver.pm
}

# pam
install -m 644 samba.pamd			$RPM_BUILD_ROOT/%{_sysconfdir}/pam.d/samba
# /etc/default file
install -m 644 %{SOURCE18}			$RPM_BUILD_ROOT/%{_sysconfdir}/default/%{name}
# start scripts
install %{SOURCE16}				$RPM_BUILD_ROOT/%{INITDIR}/%{name}-smbd
ln -sf ../../%{INITDIR}/%{name}-smbd		$RPM_BUILD_ROOT/%{_sbindir}/rc%{name}-smbd
install %{SOURCE15}				$RPM_BUILD_ROOT/%{INITDIR}/%{name}-nmbd
ln -sf ../../%{INITDIR}/%{name}-nmbd		$RPM_BUILD_ROOT/%{_sbindir}/rc%{name}-nmbd
install %{SOURCE17}				$RPM_BUILD_ROOT/%{INITDIR}/%{name}-winbindd
ln -sf ../../%{INITDIR}/%{name}-winbindd	$RPM_BUILD_ROOT/%{_sbindir}/rc%{name}-winbindd
install %{SOURCE14}				$RPM_BUILD_ROOT/%{INITDIR}/%{name}-ad
ln -sf ../../%{INITDIR}/%{name}-ad		$RPM_BUILD_ROOT/%{_sbindir}/rc%{name}-ad
install %{SOURCE19}				$RPM_BUILD_ROOT/%{INITDIR}/%{name}-ctdb
ln -sf ../../%{INITDIR}/%{name}-ctdb		$RPM_BUILD_ROOT/%{_sbindir}/rc%{name}-ctdb

install -m0755 source3/script/smbtar		$RPM_BUILD_ROOT/%{_bindir}/

cat source3/script/findsmb.in | sed -e 's!@prefix@!%{_prefix}!g' \
	-e 's!@PERL@!\/usr\/bin\/perl!' \
	> $RPM_BUILD_ROOT/%{_bindir}/findsmb
chmod 755 $RPM_BUILD_ROOT/%{_bindir}/findsmb

# pdf-generator
install -m0755 $RPM_SOURCE_DIR/smbprngenpdf 	$RPM_BUILD_ROOT/%{_bindir}/

# cups SMB support
%if %{suse_ver} >= 90
ln -sf %{_bindir}/smbspool		$RPM_BUILD_ROOT/%{_libdir}/cups/backend/smb
%endif

# pam_smbpass is missing
cp -ap source3/pam_smbpass/samples/	examples/pam_smbpass
cp -ap source3/pam_smbpass/{CHANGELOG,INSTALL,README,TODO} examples/pam_smbpass/

pushd examples/pam_smbpass
for f in $(ls); do
	n="pam_smbpass.$f"
	mv "$f" "$n"
done
popd

cp COPYING README Roadmap WHATSNEW.txt	${RPM_BUILD_ROOT}/%{DOCDIR}/
cp README.vendor			${RPM_BUILD_ROOT}/%{DOCDIR}/README.%{smbvendor}

%if %{suse_ver} >= 91
# install slpd reg file
install -d ${RPM_BUILD_ROOT}%{_sysconfdir}/slp.reg.d
install -m 0644 %SOURCE5		${RPM_BUILD_ROOT}%{_sysconfdir}/slp.reg.d/
%endif

# copy the schema
cp examples/LDAP/samba.schema $RPM_BUILD_ROOT/%{_sysconfdir}/openldap/schema/samba3.schema

# CTDB
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
echo 'CTDB_SERVICE_WINBIND="sernet-samba-winbindd"' >> ctdb/config/ctdb.sysconfig
echo 'CTDB_SERVICE_NMB="sernet-samba-nmbd"' >> ctdb/config/ctdb.sysconfig
echo 'CTDB_SERVICE_SMB="sernet-samba-smbd"' >> ctdb/config/ctdb.sysconfig
echo 'SAMBA_START_MODE="classic"' >> ctdb/config/ctdb.sysconfig
echo 'export SAMBA_START_MODE' >> ctdb/config/ctdb.sysconfig
install -m644 ctdb/config/ctdb.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/default/sernet-samba-ctdb

ln -sf sernet-samba-ctdb $RPM_BUILD_ROOT%{_sysconfdir}/default/ctdb
ln -sf ../default/sernet-samba-ctdb $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ctdb

# Collect libs for -libs package
find $RPM_BUILD_ROOT/%{LIBDIR}/ -maxdepth 1 -name '*.so*' | \
	grep -v 'libsmbd-base-samba4.so' | \
	grep -v 'libnon-posix-acls-samba4.so' | \
	grep -v 'libpytalloc-util.so' | \
	grep -v 'libpyldb-util.so' | \
	grep -v 'libsamba-net-samba4.so' | \
	grep -v 'libsamba-python-samba4.so' | \
	grep -v 'libsamba-policy.so' | \
	sed "s!${RPM_BUILD_ROOT}/!!" > filelist.libs

# Debug Package
%if %{manual_debuginfo_build}
sh $RPM_SOURCE_DIR/%{name}-find-debuginfo.sh %{_builddir}/%{?buildsubdir}
%endif


%post client
test -e /var/lib/samba/private/passdb.tdb || {
test -e /etc/samba/passdb.tdb && tdbbackup -s .rpmmigrate /etc/samba/passdb.tdb && mv /etc/samba/passdb.tdb.rpmmigrate /var/lib/samba/private/passdb.tdb
}
test -e /var/lib/samba/private/secrets.tdb || {
test -e /etc/samba/secrets.tdb && tdbbackup -s .rpmmigrate /etc/samba/secrets.tdb && mv /etc/samba/secrets.tdb.rpmmigrate /var/lib/samba/private/secrets.tdb
}
test -e /var/lib/samba/private/smbpasswd || {
test -e /etc/samba/smbpasswd && cp -p /etc/samba/smbpasswd /var/lib/samba/private/
}
(cd /var/lib/samba
DATENOW=$(date +%Y-%m-%dT%H.%M)
BACKUPEXTENSION=backed-up-by-rpm-on-$DATENOW
find . -name "*.tdb" -o -name "*.ldb" | xargs -r tdbbackup -s .$BACKUPEXTENSION
umask 077
find . -name "*.$BACKUPEXTENSION" | xargs -r tar czf $BACKUPEXTENSION.tar.gz
find . -name "*.$BACKUPEXTENSION" | xargs -r /bin/rm
)

%post
if [ $1 = 1 ] ; then
	/sbin/chkconfig --add %{name}-smbd
	/sbin/chkconfig --add %{name}-nmbd
else
	test "${DISABLE_RESTART_ON_UPDATE}" = yes || {
		/sbin/service %{name}-nmbd try-restart
		/sbin/service %{name}-smbd try-restart
	}
fi
mkdir -p /var/lib/samba/drivers/{COLOR,W32X86,WIN40,W32ALPHA,W32MIPS,W32PPC,IA64,x64,ARM}

%preun
if [ $1 = 0 ] ; then
	/sbin/chkconfig --del %{name}-smbd
	/sbin/chkconfig --del %{name}-nmbd
	/sbin/service %{name}-smbd stop
	/sbin/service %{name}-nmbd stop
fi
exit 0

%post winbind
if [ $1 = 1 ] ; then
	/sbin/chkconfig --add %{name}-winbindd
else
	test "${DISABLE_RESTART_ON_UPDATE}" = yes || /sbin/service %{name}-winbindd try-restart
fi

%preun winbind
if [ $1 = 0 ] ; then
	/sbin/chkconfig --del %{name}-winbindd
	/sbin/service %{name}-winbindd stop
fi
exit 0

%post ad
_PRIVATEDIR="/var/lib/samba/private"
_try_fix="no"
test -d "${_PRIVATEDIR}/tls" && {
	ls -dln "${_PRIVATEDIR}/tls" | grep -q "^drwxr-xr-x.* 0 0 .* ${_PRIVATEDIR}/tls$" && {
		_try_fix="yes"
	}
}
test -f "${_PRIVATEDIR}/tls/key.pem" && {
	ls -ln "${_PRIVATEDIR}/tls/key.pem" | grep -q "^-rw-r--r--.* 0 0 .* ${_PRIVATEDIR}/tls/key.pem$" && {
		_try_fix="yes"
	}
}

test x"${_try_fix}" = x"yes" && {
	cd "${_PRIVATEDIR}" || exit 1
	echo "cd $(pwd)"
	ls -dln . | grep -q "^drwxr-x---.* 0 0 .* \.$" && {
		ls -dln tls | grep -q "^drwxr-xr-x.* 0 0 .* tls$" && {
			echo "Warning: wrong permissions on 'tls'"
			ls -dl tls
			echo "Fixing permissions of 'tls'"
			chmod 0700 tls || exit 1
			ls -dl tls
		}
		ls -ln tls/key.pem | grep -q "^-rw-r--r--.* 0 0 .* tls/key.pem$" && {
			echo "Warning: wrong permissions on 'tls/key.pem'"
			ls -l tls/key.pem
			echo "Fixing permissions of 'tls/key.pem'"
			chmod 0600 tls/key.pem || exit 1
			ls -l tls/key.pem
		}
	}
	cd - >/dev/null || exit 1
}
test -d "${_PRIVATEDIR}/tls" && {
	ls -dln "${_PRIVATEDIR}/tls" | grep -q "^drwx------.* 0 0 .* ${_PRIVATEDIR}/tls$" || {
		echo "Warning: unexpected permissions on '${_PRIVATEDIR}/tls'"
		ls -dl "${_PRIVATEDIR}/tls"
	}
}
test -f "${_PRIVATEDIR}/tls/key.pem" && {
	ls -ln "${_PRIVATEDIR}/tls/key.pem" | grep -q "^-rw-------.* 0 0 .* ${_PRIVATEDIR}/tls/key.pem$" || {
		echo "Warning: unexpected permissions on '${_PRIVATEDIR}/tls/key.pem'"
		ls -l "${_PRIVATEDIR}/tls/key.pem"
	}
}
if [ $1 = 1 ] ; then
	/sbin/chkconfig --add %{name}-ad
else
	test "${DISABLE_RESTART_ON_UPDATE}" = yes || /sbin/service %{name}-ad try-restart
fi

%preun ad
if [ $1 = 0 ] ; then
	/sbin/chkconfig --del %{name}-ad
	/sbin/service %{name}-ad stop >/dev/null 2>&1
fi
exit 0

%post ctdb
DATENOW=$(date +%Y-%m-%dT%H.%M)
BACKUPEXTENSION=backed-up-by-rpm-on-$DATENOW

CTDB_DBDIR_PERSISTENT=""
eval "$(grep 'CTDB_DBDIR_PERSISTENT=' /etc/sysconfig/ctdb 2>/dev/null)"
test -z "${CTDB_DBDIR_PERSISTENT}" && {
	test -d /var/lib/ctdb/persistent || {
		test -d /var/ctdb/persistent && {
			mkdir -p /var/lib/ctdb && {
				cp -a /var/ctdb/persistent /var/lib/ctdb/ && {
					mv /var/ctdb /var/ctdb.$BACKUPEXTENSION
				}
			}
		}
	}
}

if [ $1 = 1 ] ; then
	/sbin/chkconfig --add %{name}-ctdb
else
	test "${DISABLE_RESTART_ON_UPDATE}" = yes || /sbin/service %{name}-ctdb try-restart
fi

%preun ctdb
if [ $1 = 0 ] ; then
	/sbin/chkconfig --del %{name}-ctdb
	/sbin/service %{name}-ctdb stop
fi
exit 0

%post libsmbclient0
/sbin/ldconfig
%post libs
/sbin/ldconfig
%postun libsmbclient0
/sbin/ldconfig
%postun libs
/sbin/ldconfig

%clean
# for debugging, set $NO_BUILD_DIR_CLEANUP in your shell
%if %(test -z "$NO_BUILD_DIR_CLEANUP" && echo 1 || echo 0 )
rm -rf ${RPM_BUILD_ROOT}
rm -rf ${RPM_BUILD_DIR}/samba-%{version}
%endif

%files
%defattr(-,root,root)
%dir %{CONFIGDIR}
%dir %{STATEDIR}/drivers
%dir %{STATEDIR}/netlogon
%dir %{STATEDIR}/profiles
%dir %{STATEDIR}/printing
%dir %{LIBDIR}
%{LIBDIR}/libsmbd-base-samba4.so
%{LIBDIR}/libnon-posix-acls-samba4.so
%{LIBDIR}/vfs
%dir %{_datadir}/samba
%{INITDIR}/%{name}-smbd
%{INITDIR}/%{name}-nmbd
%config %{_sysconfdir}/pam.d/samba
%if %{suse_ver} >= 91
%{_sysconfdir}/slp.reg.d/*
%endif
%if %{with_man}
%doc %{_mandir}/man1/sharesec.1.gz
%doc %{_mandir}/man1/smbcontrol.1.gz
%doc %{_mandir}/man1/smbstatus.1.gz
%doc %{_mandir}/man5/smbpasswd.5.gz
%doc %{_mandir}/man8/net.8.gz
%doc %{_mandir}/man8/smbta-util.8.gz
%doc %{_mandir}/man8/nmbd.8.gz
%doc %{_mandir}/man8/pdbedit.8.gz
%doc %{_mandir}/man8/smbd.8.gz
%doc %{_mandir}/man8/smbpasswd.8.gz
%doc %{_mandir}/man8/eventlogadm.8.gz
%doc %{_mandir}/man8/vfs_*
%endif
%{_bindir}/eventlogadm
%{_bindir}/pdbedit
%{_bindir}/net
%{_bindir}/sharesec
%{_bindir}/smbcontrol
%{_bindir}/smbpasswd
%{_bindir}/smbstatus
%{_bindir}/smbta-util
%{_bindir}/smbprngenpdf
%{_sbindir}/nmbd
%{_sbindir}/rcsernet-samba-nmbd
%{_sbindir}/rcsernet-samba-smbd
%{_sbindir}/smbd

%files common
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/default/sernet-samba
%doc %{DOCDIR}
%dir %{CONFIGDIR}
%dir %{PIDDIR}
%attr(0750, root, root) %{LOGDIR}
%dir %{STATEDIR}
%attr(0750, root, root) %dir %{STATEDIR}/private
%dir %{CACHEDIR}
%if %{with_man}
%doc %{_mandir}/man5/lmhosts.5.gz
%doc %{_mandir}/man5/smb.conf.5.gz
%doc %{_mandir}/man7/samba.7.gz
%endif
%dir %{_sysconfdir}/openldap/schema
%attr(0444, root, root) %config(noreplace) %{_sysconfdir}/openldap/schema/samba3.schema
%dir %{_datadir}/samba/codepages
%{_datadir}/samba/codepages/lowcase.dat
%{_datadir}/samba/codepages/upcase.dat
%{_datadir}/samba/codepages/valid.dat

%files libs -f filelist.libs
%defattr(-,root,root)
%dir %{LIBDIR}
%{LIBDIR}/gensec
%{LIBDIR}/auth
%{LIBDIR}/ldb
/%{_lib}/security/pam_smbpass.so
%{_libdir}/libwbclient.so.*
/%{_lib}/libnss_winbind.so*
/%{_lib}/libnss_wins.so*
/%{_lib}/security/pam_winbind.so
%if %{build_krb5_locator}
%{_libdir}/krb5/plugins/libkrb5/winbind_krb5_locator.so
%if %{with_man}
%doc %{_mandir}/man7/winbind_krb5_locator.7.gz
%endif
%endif

%files client
%defattr(-,root,root)
%if %{suse_ver} >= 90
%dir %{_libdir}/cups
%dir %{_libdir}/cups/backend
%endif
%if %{with_man}
%doc %{_mandir}/man1/findsmb.1.gz
%doc %{_mandir}/man1/nmblookup.1.gz
%doc %{_mandir}/man1/profiles.1.gz
%doc %{_mandir}/man1/rpcclient.1.gz
%doc %{_mandir}/man1/smbcacls.1.gz
%doc %{_mandir}/man1/smbclient.1.gz
%doc %{_mandir}/man1/smbcquotas.1.gz
%doc %{_mandir}/man1/smbget.1.gz
%doc %{_mandir}/man1/smbtar.1.gz
%doc %{_mandir}/man1/smbtree.1.gz
%doc %{_mandir}/man1/dbwrap_tool.1.gz
%doc %{_mandir}/man5/smbgetrc.5.gz
%doc %{_mandir}/man8/smbspool.8.gz
%doc %{_mandir}/man8/smbspool_krb5_wrapper.8.gz
%doc %{_mandir}/man8/samba-regedit.8.gz
%doc %{_mandir}/man1/testparm.1.gz
#FIXME %doc %{_mandir}/man8/tdbbackup.8.gz
#FIXME %doc %{_mandir}/man8/tdbdump.8.gz
#FIXME %doc %{_mandir}/man8/tdbtool.8.gz
%endif
%{_bindir}/findsmb
%{_bindir}/nmblookup
%{_bindir}/profiles
%{_bindir}/rpcclient
%{_bindir}/smbcacls
%{_bindir}/smbclient
%{_bindir}/smbcquotas
%{_bindir}/smbget
%{_bindir}/smbspool
%{_bindir}/smbspool_krb5_wrapper
%{_bindir}/smbtar
%{_bindir}/smbtree
%if %{suse_ver} >= 90
%{_libdir}/cups/backend/smb
%endif
%{_bindir}/locktest
%{_bindir}/masktest
%{_bindir}/cifsdd
%{_bindir}/dbwrap_tool
%{_bindir}/gentest
%{_bindir}/ndrdump
%{_bindir}/oLschema2ldif
%{_bindir}/regdiff
%{_bindir}/regpatch
%{_bindir}/regshell
%{_bindir}/regtree
%{_bindir}/tdbbackup
%{_bindir}/tdbdump
%{_bindir}/tdbrestore
%{_bindir}/tdbtool
%{_bindir}/testparm
%{_bindir}/ntdbrestore
%{_bindir}/ntdbdump
%{_bindir}/ntdbtool
%{_bindir}/ntdbbackup
%{_bindir}/samba-regedit

%files winbind
%defattr(-,root,root)
%{INITDIR}/%{name}-winbindd
%if %{with_man}
%doc %{_mandir}/man1/ntlm_auth.1.gz
%doc %{_mandir}/man1/wbinfo.1.gz
%doc %{_mandir}/man5/pam_winbind.conf.5.gz
%doc %{_mandir}/man8/winbindd.8.gz
%doc %{_mandir}/man8/pam_winbind.8.gz
%doc %{_mandir}/man8/idmap_ad.8.gz
%doc %{_mandir}/man8/idmap_autorid.8.gz
%doc %{_mandir}/man8/idmap_ldap.8.gz
%doc %{_mandir}/man8/idmap_nss.8.gz
%doc %{_mandir}/man8/idmap_rid.8.gz
%doc %{_mandir}/man8/idmap_tdb.8.gz
%doc %{_mandir}/man8/idmap_tdb2.8.gz
%doc %{_mandir}/man8/idmap_hash.8.gz
%doc %{_mandir}/man8/idmap_rfc2307.8.gz
%endif
%{_bindir}/ntlm_auth
%{_bindir}/wbinfo
%{_sbindir}/rcsernet-samba-winbindd
%{_sbindir}/winbindd
%{LIBDIR}/idmap
%{LIBDIR}/nss_info

%files libwbclient-devel
%defattr(-,root,root)
%{_libdir}/libwbclient.so
%{_includedir}/wbclient.h

%files libsmbclient0
%defattr(-,root,root)
%{_libdir}/libsmbclient.so.*
%if %{with_man}
%doc %{_mandir}/man7/libsmbclient.7.gz
%endif

%files libsmbclient-devel
%defattr(-,root,root)
%{_includedir}/libsmbclient.h
%{_libdir}/libsmbclient.so

%files ad
%defattr(-,root,root)
%{LIBDIR}/libpytalloc-util.so*
%{LIBDIR}/libpyldb-util.so*
%{LIBDIR}/libsamba-net-samba4.so*
%{LIBDIR}/libsamba-python-samba4.so*
%{LIBDIR}/libsamba-policy.so*
%{LIBDIR}/bind9/dlz_bind9.so
%{LIBDIR}/bind9/dlz_bind9_9.so
%{LIBDIR}/bind9/dlz_bind9_10.so
%{LIBDIR}/process_model
%{LIBDIR}/service
%{INITDIR}/%{name}-ad
%if %{with_man}
%doc %{_mandir}/man8/samba.8.gz
%doc %{_mandir}/man8/samba-tool.8.gz
#FIXME: %doc %{_mandir}/man1/ldbadd.1.gz ...
%endif
%{_bindir}/ldbadd
%{_bindir}/ldbdel
%{_bindir}/ldbedit
%{_bindir}/ldbmodify
%{_bindir}/ldbrename
%{_bindir}/ldbsearch
%{_bindir}/samba-tool
%{_bindir}/smbtorture
%{_sbindir}/samba
%{_sbindir}/samba_dnsupdate
%{_sbindir}/samba_kcc
%{_sbindir}/samba_spnupdate
%{_sbindir}/samba_upgradedns
%{_sbindir}/rcsernet-samba-ad
%{_datadir}/samba/setup
%{py_sitedir}

%files ctdb
%defattr(-,root,root)
%{INITDIR}/%{name}-ctdb
%config(noreplace) %{_sysconfdir}/default/sernet-samba-ctdb
%attr(0440, root, root) %config(noreplace) %{_sysconfdir}/sudoers.d/ctdb
%config %{_sysconfdir}/ctdb/ctdb-crash-cleanup.sh
%config %{_sysconfdir}/ctdb/debug-hung-script.sh
%config %{_sysconfdir}/ctdb/debug_locks.sh
%config %{_sysconfdir}/ctdb/functions
%config %{_sysconfdir}/ctdb/gcore_trace.sh
%config %{_sysconfdir}/ctdb/notify.d/README
%config %{_sysconfdir}/ctdb/notify.sh
%config %{_sysconfdir}/ctdb/statd-callout
%config %{_sysconfdir}/ctdb/events.d/*
%config %{_sysconfdir}/ctdb/nfs-rpc-checks.d/*
%{_sysconfdir}/sysconfig/ctdb
%{_sysconfdir}/default/ctdb
%{_bindir}/ctdb
%{_bindir}/ctdb_diagnostics
%{_bindir}/ctdb_event_helper
%{_bindir}/ctdb_lock_helper
%{_bindir}/ltdbtool
%{_bindir}/onnode
%{_bindir}/ping_pong
%{_bindir}/smnotify
%{_sbindir}/rcsernet-samba-ctdb
%{_sbindir}/ctdbd
%{_sbindir}/ctdbd_wrapper

%files ctdb-tests
%defattr(-,root,root)
%{_bindir}/ctdb_run_cluster_tests
%{_bindir}/ctdb_run_tests
%{_libdir}/ctdb-tests/ctdb_bench
%{_libdir}/ctdb-tests/ctdb_fetch
%{_libdir}/ctdb-tests/ctdb_fetch_one
%{_libdir}/ctdb-tests/ctdb_fetch_readonly_loop
%{_libdir}/ctdb-tests/ctdb_fetch_readonly_once
%{_libdir}/ctdb-tests/ctdb_functest
%{_libdir}/ctdb-tests/ctdb_lock_tdb
%{_libdir}/ctdb-tests/ctdb_persistent
%{_libdir}/ctdb-tests/ctdb_porting_tests
%{_libdir}/ctdb-tests/ctdb_randrec
%{_libdir}/ctdb-tests/ctdb_store
%{_libdir}/ctdb-tests/ctdb_stubtest
%{_libdir}/ctdb-tests/ctdb_takeover_tests
%{_libdir}/ctdb-tests/ctdb_trackingdb_test
%{_libdir}/ctdb-tests/ctdb_transaction
%{_libdir}/ctdb-tests/ctdb_traverse
%{_libdir}/ctdb-tests/ctdb_update_record
%{_libdir}/ctdb-tests/ctdb_update_record_persistent
%{_libdir}/ctdb-tests/rb_test
%{_datadir}/ctdb-tests/eventscripts/etc-ctdb/events.d
%{_datadir}/ctdb-tests/eventscripts/etc-ctdb/functions
%{_datadir}/ctdb-tests/eventscripts/etc-ctdb/nfs-rpc-checks.d
%{_datadir}/ctdb-tests/eventscripts/etc-ctdb/statd-callout
%{_datadir}/ctdb-tests/scripts/common.sh
%{_datadir}/ctdb-tests/scripts/integration.bash
%{_datadir}/ctdb-tests/scripts/test_wrap
%{_datadir}/ctdb-tests/scripts/unit.sh


%description -n %{name}
Samba is a suite of programs which work together to allow clients to
access Unix filespace and printers via the SMB/CIFS protocol.

%description common
This package contains common files.

%description libs
This package contains common library files.

%description client
This package contains all programs that are needed to act as a Samba
client.

%description winbind
%{name}-winbind

%description libsmbclient0
This package includes the libsmbclient library.

%description libsmbclient-devel
This package contains static libraries and header files needed to
develop programs which make use of the smbclient programming interface.

%description ad
This package contains the part of Samba which are needed to run
an active directory compatible domain controller.

%description ctdb
This package contains CTDB

%description ctdb-tests
This package contains CTDB tests

%changelog

