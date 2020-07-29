FROM openjdk:8-jdk
RUN useradd -ms /bin/bash java
COPY *.jar /home/java
USER java
WORKDIR /home/java
CMD ["host.docker.internal", "guest", "guest"]
ENTRYPOINT ["java", "-jar", "rabbit-groovy.jar"]

