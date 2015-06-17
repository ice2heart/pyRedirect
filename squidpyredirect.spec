Name:         squidpyredirect
Version:      1
Release:      1
Summary:      Simple redirect app for squid
Group:        Networking/Utilities
License:      Apache
Source0:      squidpyredirect.tar.bz2
BuildArch:    noarch
Packager:     Albert Yakupov <ice2heart@gmail.com>
Requires:     python python-dev python-pip
Autoreqprov:  no

%description
Simple redirect app for squid
Usage: add to squid.conf
url_rewrite_program /usr/bin/python /opt/spr/app.py /opt/spr/redirect.json


%prep
%setup -q -n squidpyredirect.tar.bz2




%install
mkdir -p $RPM_BUILD_ROOT/opt/spr/
cp -r . $RPM_BUILD_ROOT/opt/spr/

%files
/opt/spr/

%post
pip install -r /opt/spr/requirements.txt

%clean
rm -rf $RPM_BUILD_ROOT