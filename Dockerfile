FROM ubuntu:16.04

RUN set -ex \
 \
 && apt-get update \
 && apt-get install -y wget \
 && apt-get install -y python-pip \
 && apt-get install -y libffi-dev libpcre3 libpcre++-dev python apache2 python-dev python-cheetah python-simplejson libltdl7 \
# && pip install signalfd python-signalfd \
 && wget -O python-signalfd.deb "https://corpora.fi.muni.cz/noske/deb/1604/python-signalfd/python-signalfd_0.1-1ubuntu1_amd64.deb" \
 && wget -O bonito.deb "https://corpora.fi.muni.cz/noske/deb/1604/bonito-open/bonito-open_3.105.1-1_all.deb" \
 && wget -O bonito-www.deb "https://corpora.fi.muni.cz/noske/deb/1604/bonito-open/bonito-open-www_3.105.1-1_all.deb" \
 && wget -O manatee.deb "https://corpora.fi.muni.cz/noske/deb/1604/manatee-open/manatee-open_2.158.8-1ubuntu1_amd64.deb" \
 && wget -O manatee-python.deb "https://corpora.fi.muni.cz/noske/deb/1604/manatee-open/manatee-open-python_2.158.8-1ubuntu1_amd64.deb" \
 && wget -O manatee-susanne.deb "https://corpora.fi.muni.cz/noske/deb/1604/manatee-open/manatee-open-susanne_2.158.8-1ubuntu1_amd64.deb" \
 && dpkg -i  ./python-signalfd.deb ./bonito.deb ./bonito-www.deb ./manatee.deb ./manatee-python.deb ./manatee-susanne.deb \
