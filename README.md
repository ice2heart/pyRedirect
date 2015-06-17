#Manual setup
pip install - r requirements.txt 
#edit path in squid.conf
sudo mv squid.conf /etc/squid3/squid.conf
#before make RPM 
git archive master | bzip2 > squidpyredirect.tar.bz2
mkdir -p rpm/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
mv squidpyredirect.tar.bz2 rpm/SOURCES
mv squidpyredirect.spec rpm/SPECS

