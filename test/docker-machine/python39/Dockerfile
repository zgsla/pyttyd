FROM ubuntu:16.04

RUN apt-get update

RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd

# 修改SSH服务的安全登录配置，取消pam登录限制
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

RUN echo 'export LANG=C.UTF-8' >> /etc/profile

EXPOSE 22

RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libbz2-dev liblzma-dev sqlite3 libsqlite3-dev tk-dev uuid-dev
#RUN wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tar.xz
COPY Python-3.9.12.tar.xz .
RUN tar -xf Python-3.9.12.tar.xz
RUN cd Python-3.9.12/ && ./configure --enable-optimizations && make && make install

CMD ["/usr/sbin/sshd", "-D"]
