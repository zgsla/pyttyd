FROM ubuntu:16.04

RUN apt-get update

RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd

# 修改SSH服务的安全登录配置，取消pam登录限制
RUN sed -ri 's/session required pam_loginuid.so/#session required pam_loginuid.so/g'  /etc/pam.d/sshd

RUN echo 'export LANG=C.UTF-8' >> /etc/profile

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]