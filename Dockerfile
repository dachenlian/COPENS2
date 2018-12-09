FROM python:3.7.1
RUN apt-get update && apt-get install bison flex libwww-perl subversion -y
RUN svn co http://svn.code.sf.net/p/cwb/code/cwb/trunk cwb && svn co http://svn.code.sf.net/p/cwb/code/perl/trunk cwb-perl
RUN mkdir /app
COPY .cqprc /home
ADD . /app
WORKDIR /app/cwb/
RUN make clean && make depend && ./install-scripts/install-linux
ENV PATH="/usr/local/cwb-3.4.15/bin:${PATH}"
WORKDIR /app/cwb-perl/CWB
RUN perl Makefile.PL && make && make test && make install
WORKDIR /app
RUN pip install pipenv
RUN pipenv install --system
WORKDIR /app/COPENS
RUN mkdir -p cwb/raw cwb/registry/public cwb/data cwb/results



