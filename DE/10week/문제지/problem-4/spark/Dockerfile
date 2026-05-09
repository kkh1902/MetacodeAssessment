FROM apache/spark:3.5.4

USER root

RUN pip3 install --no-cache-dir \
    pyspark==3.5.4 \
    psycopg2-binary \
    kafka-python

# Kafka connector JARs (Spark ↔ Kafka 연동에 필요)
RUN curl -fsSL -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.4.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.4/spark-sql-kafka-0-10_2.12-3.5.4.jar && \
    curl -fsSL -o /opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.4.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.4/spark-token-provider-kafka-0-10_2.12-3.5.4.jar && \
    curl -fsSL -o /opt/spark/jars/kafka-clients-3.6.1.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.1/kafka-clients-3.6.1.jar && \
    curl -fsSL -o /opt/spark/jars/commons-pool2-2.11.1.jar \
    https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar
