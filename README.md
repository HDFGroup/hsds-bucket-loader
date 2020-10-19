HSDS Bucket Loader - Scalable HDF5 ingester for HSDS
=====================================================

Introduction
------------

HSDS (see: https://github.com/HDFGroup/hsds) is a web service that enables efficient access to HDF data stored in its native format.  For users who have existing repositories of HDF5 files, it's necessary to convert them using the hsload utility before the data can be accessed by the server.  If the files are small and/or relatively few in number, it's easy enough to import the files manually.  

On the other hand, if you have 1000's of files which maybe GB's each, this project provides a way to efficiently perform the ingestion
using Kubernetes.

This tool was tested using AWS S3 and AWS EKS (managed Kubernetes for AWS), but should work with any Kubernetes cluster with files that are stored in an AWS S3 API compatiblituy storage system (e.g. OpenIO or Scality).

Overview
--------

The following diagram shows the components used by the bucket loader:

![Diagram1](https://github.com/HDFGroup/hsds-bucket-loader/blob/master/images/diagram.png)