FROM custom-spark:3.5.4

USER root

RUN curl -fsSL -o /opt/spark/jars/postgresql-42.7.1.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.1/postgresql-42.7.1.jar

RUN mkdir -p /opt/spark/conf && \
    printf 'spark.driver.memory 512m\nspark.driver.host spark-master\nspark.executor.memory 512m\nspark.executor.memoryOverhead 96m\n' \
    > /opt/spark/conf/spark-defaults.conf
