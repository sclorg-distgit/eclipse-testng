%{?scl:%scl_package eclipse-testng}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

%global gittag %{version}.201609291640

Name:      %{?scl_prefix}eclipse-testng
Version:   6.9.13
Release:   1.%{baserelease}%{?dist}
Summary:   TestNG plug-in for Eclipse
License:   ASL 2.0
URL:       http://testng.org

BuildArch: noarch

Source0:   https://github.com/cbeust/testng-eclipse/archive/%{gittag}.tar.gz

# Fix embedded lib names
Patch0:    eclipse-testng-manifest.patch

# Add gson to classpath because in Fedora, testng-remote does not bundle it
Patch1:    eclipse-testng-no-bundled-gson.patch

Requires: %{?scl_prefix}guava
Requires: %{?scl_prefix_java_common}google-gson
Requires: %{?scl_prefix_java_common}junit
Requires: %{?scl_prefix_java_common}hamcrest
Requires: %{?scl_prefix}testng >= 6.9.12
Requires: %{?scl_prefix}testng-remote >= 1.1.0
Requires: %{?scl_prefix_maven}beust-jcommander
Requires: %{?scl_prefix_java_common}snakeyaml
Requires: %{?scl_prefix_java_common}base64coder
Requires: %{?scl_prefix_maven}bsh
Requires: %{?scl_prefix_java_common}slf4j

BuildRequires: %{?scl_prefix}tycho
BuildRequires: %{?scl_prefix}eclipse-jdt
BuildRequires: %{?scl_prefix}eclipse-m2e-core
BuildRequires: %{?scl_prefix}guava
BuildRequires: %{?scl_prefix_java_common}google-gson
BuildRequires: %{?scl_prefix_java_common}junit
BuildRequires: %{?scl_prefix_java_common}hamcrest
BuildRequires: %{?scl_prefix}testng >= 6.9.12
BuildRequires: %{?scl_prefix}testng-remote >= 1.1.0
BuildRequires: %{?scl_prefix_maven}beust-jcommander
BuildRequires: %{?scl_prefix_java_common}snakeyaml
BuildRequires: %{?scl_prefix_java_common}base64coder
BuildRequires: %{?scl_prefix_maven}bsh
BuildRequires: %{?scl_prefix_java_common}slf4j
BuildRequires: %{?scl_prefix_maven}maven-enforcer-plugin

%description
The Eclipse TestNG plug-in integrates the TestNG testing framework into the
Eclipse IDE.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n testng-eclipse-%{gittag}
%patch0
%patch1

# remove bundled libs
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

# remove plugin not in Fedora
%pom_remove_plugin "pl.project13.maven:git-commit-id-plugin"
%pom_remove_plugin "pl.project13.maven:git-commit-id-plugin" testng-eclipse-plugin
sed -i -e 's/${git.branch}/%{gittag}/' -e 's/${git.commit.id}/%{gittag}/' -e 's/${git.build.version}/%{version}/' \
  testng-eclipse-plugin/src/main/resources/git.properties

sed -i -e '/^Bsh\.library/ s/bsh-2.0b4.jar/bsh.jar/' \
  testng-eclipse-plugin/src/main/org/testng/eclipse/TestNGMessages.properties

# build against fedora packaged libs
build-jar-repository -s -p testng-eclipse-plugin/lib \
  guava testng testng-remote/testng-remote-dist-shaded snakeyaml base64coder junit hamcrest/core \
  beust-jcommander bsh google-gson/gson slf4j/api
mv testng-eclipse-plugin/lib/beust-jcommander.jar testng-eclipse-plugin/lib/jcommander.jar
mv testng-eclipse-plugin/lib/testng-remote_testng-remote-dist-shaded.jar testng-eclipse-plugin/lib/testng-remote.jar
sed -i -e '2iEclipse-BundleShape: dir' testng-eclipse-plugin/META-INF/MANIFEST.MF

# don't install poms
%mvn_package "::pom::" __noinstall
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_build -j
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install

# need to recreate the symlinks to libraries that were setup in "prep"
# this will cause some benign dangling-symlink rpmlint warnings
pushd %{buildroot}%{_datadir}/eclipse/droplets/testng/eclipse/plugins/org.testng.eclipse_*
rm lib/*.jar
build-jar-repository -s -p lib \
  guava testng testng-remote/testng-remote-dist-shaded snakeyaml base64coder junit hamcrest/core \
  beust-jcommander bsh google-gson/gson slf4j/api
mv lib/beust-jcommander.jar lib/jcommander.jar
mv lib/testng-remote_testng-remote-dist-shaded.jar lib/testng-remote.jar
popd
%{?scl:EOF}


%files -f .mfiles
%doc README.md

%changelog
* Fri Jan 20 2017 Mat Booth <mat.booth@redhat.com> - 6.9.13-1.2
- Ensure patch applies cleanly

* Fri Jan 20 2017 Mat Booth <mat.booth@redhat.com> - 6.9.13-1.1
- Auto SCL-ise package for rh-eclipse46 collection

* Wed Nov 09 2016 Mat Booth <mat.booth@redhat.com> - 6.9.13-1
- Update to latest upstream version

* Thu Jun 30 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 6.9.11.1-2
- Add missing BR on maven-enforcer-plugin

* Mon Apr 25 2016 Mat Booth <mat.booth@redhat.com> - 6.9.11.1-1
- Update to latest upstream release

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 6.9.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Oct 29 2015 Mat Booth <mat.booth@redhat.com> - 6.9.9-1
- Update to 6.9.9

* Wed Sep 02 2015 Mat Booth <mat.booth@redhat.com> - 6.9.5-1.git4d432f9
- Update to latest upstream
- Build with xmvn/tycho

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 6.8.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Mar 9 2015 Alexander Kurtakov <akurtako@redhat.com> 6.8.6-5
- Add BR: slf4j now that it's no longer transitive one.

* Wed Jul 30 2014 Mat Booth <mat.booth@redhat.com> - 6.8.6-4
- Restore testng as an embedded lib due to runtime issues

* Mon Jun 16 2014 Mat Booth <mat.booth@redhat.com> - 6.8.6-3
- Use orbit style deps instead of symlinked libs embedded in the plug-in

* Thu Jun 12 2014 Mat Booth <mat.booth@redhat.com> - 6.8.6-2
- Patch for compatibility with eclipse luna

* Thu Jun 12 2014 Mat Booth <mat.booth@redhat.com> - 6.8.6-1
- Update to latest upstream release.

* Fri Mar 14 2014 Mat Booth <fedora@matbooth.co.uk> - 6.8.5-2.20130625gite0f6037
- Add BR/R on google-guice.

* Tue Jun 25 2013 Mat Booth <fedora@matbooth.co.uk> - 6.8.5-1.20130625gite0f6037
- Initial package.