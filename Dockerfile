FROM hdfgroup/hdf5lib:1.10.6
LABEL MAINTAINER="John Readey, The HDF Group"
ENV AWS_ACCESS_KEY_ID=SupplyCorrectValue
ENV AWS_SECRET_ACCESS_KEY=SupplyCorrectValue
ENV HS_USERNAME=SupplyCorrectValue
ENV HS_PASSWORD=SupplyCorrectValue
ENV RUN_COMMAND=
RUN pip install tzlocal
RUN pip install pyyaml
RUN pip install boto3
RUN mkdir /app
COPY loadfiles.py /app
COPY utillib.py /app
COPY watchdog.py /app
COPY dump_inventory_file.py /app
COPY make_inventory_file.py /app
COPY config.py /app
COPY entrypoint.sh  /
WORKDIR /app
ENTRYPOINT ["/entrypoint.sh"]
