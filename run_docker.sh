#!/bin/bash
# script to run bucket_loder as a docker container
if [[ $# -eq 0 ]] || ([[ $1 == "-h" ]] || [[ $1 == "--help" ]]); then
   echo "Usage: run_docker.sh [make|dump|watch|load|bash]"
   exit 1
fi
if [[ -z ${HS_USERNAME} ]]; then
   echo "HS_USERNAME not set"
   exit 1
fi
if [[ -z ${HS_PASSWORD} ]]; then
   echo "HS_PASSWORD not set"
   exit 1
fi
if [[ -z ${AWS_SECRET_ACCESS_KEY} ]]; then
   echo "AWS_SECRET_ACCESS_KEY not set"
   exit 1
fi
if [[ -z ${AWS_ACCESS_KEY_ID} ]]; then
   echo "AWS_ACCESS_KEY_ID not set"
   exit 1
fi

export CMD=$1
echo $CMD
if [[ ${CMD} == "make" ]]; then
    docker run --rm  -v ${PWD}/config.yml:/config/config.yml  -e HS_USERNAME=$HS_USERNAME -e HS_PASSWORD=$HS_PASSWORD -e HS_PASSWORD=$HS_PASSWORD -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e RUN_COMMAND=make -it hdfgroup/bucket_loader
elif [[ ${CMD} == "dump" ]]; then
    docker run --rm  -v ${PWD}/config.yml:/config/config.yml  -e HS_USERNAME=$HS_USERNAME -e HS_PASSWORD=$HS_PASSWORD -e HS_PASSWORD=$HS_PASSWORD -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e RUN_COMMAND=dump -it hdfgroup/bucket_loader
elif [[ ${CMD} == "watch" ]]; then
    echo "running bucket_watch daemon"
    docker run --name bucket_watch -v ${PWD}/config.yml:/config/config.yml  -e HS_USERNAME=$HS_USERNAME -e HS_PASSWORD=$HS_PASSWORD -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e RUN_COMMAND=watch -d hdfgroup/bucket_loader
elif [[ ${CMD} == "load" ]]; then
    echo "running bucket_load daemon"
    docker run  --name bucket_load -v ${PWD}/config.yml:/config/config.yml  -e HS_USERNAME=$HS_USERNAME -e HS_PASSWORD=$HS_PASSWORD -e HS_PASSWORD=$HS_PASSWORD -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e RUN_COMMAND=load -d hdfgroup/bucket_loader
elif [[ ${CMD} == "bash" ]]; then
    echo "running  bash"
    docker run --rm  -v ${PWD}/config.yml:/config/config.yml  -e HS_USERNAME=$HS_USERNAME -e HS_PASSWORD=$HS_PASSWORD -e HS_PASSWORD=$HS_PASSWORD -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e RUN_COMMAND=bash -it hdfgroup/bucket_loader
else
    echo "unexpected run run command"
    exit 1
fi
