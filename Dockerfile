FROM python:3.7.1
RUN apt-get update
RUN apt-get install bison flex libwww-perl subversion -y

# Download CWB & CWB-PERL from SVN
RUN svn co http://svn.code.sf.net/p/cwb/code/cwb/trunk /cwb
RUN svn co http://svn.code.sf.net/p/cwb/code/perl/trunk /cwb-perl

# Install CWB
WORKDIR /cwb/
RUN ./install-scripts/config-basic
RUN ./install-scripts/install-linux
ENV PATH="/usr/local/cwb-3.4.18/bin:${PATH}"

# Install CWB-PERL
WORKDIR /cwb-perl/CWB-CL
RUN perl Makefile.PL
RUN make
RUN make test
RUN make install

# Install CWB-PERL
WORKDIR /cwb-perl/CWB
RUN perl Makefile.PL
RUN make
RUN make test
RUN make install

RUN mkdir /app
COPY .cqprc /home
ADD . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --system
WORKDIR /app/COPENS
RUN mkdir -p cwb/raw cwb/registry/public cwb/data cwb/results