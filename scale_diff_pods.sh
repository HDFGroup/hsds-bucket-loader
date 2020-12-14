#!/bin/bash
if [[ $# -eq 0 ]] || ([[ $1 == "-h" ]] || [[ $1 == "--help" ]]); then
   echo "Usage: scale_diff_pods.sh [cnt]"
   exit 1
fi
kubectl scale --replicas=$1 deployment/hsds-bucket-diff
