HSDS Bucket Loader - Scalable HDF5 ingester for HSDS
=====================================================

![Diagram1](https://github.com/HDFGroup/hsds-bucket-loader/blob/master/images/loader.jpg)

Introduction
------------

HSDS (see: https://github.com/HDFGroup/hsds) is a web service that enables efficient access to HDF data stored using the HSDS schema (a sharded version of the HDF5 data format).  For users who have existing repositories of HDF5 files, it's necessary to convert them using the hsload utility before the data can be accessed by the server.  If the files are small and/or relatively few in number, it's easy enough to import the files manually.  

On the other hand, if you have 1000's of files which may be GB's in size, this project provides a way to efficiently perform the ingestion using Kubernetes.

This tool was tested using AWS S3 and AWS EKS (managed Kubernetes for AWS), but should work with any Kubernetes cluster with files that are stored in an AWS S3 API compatible storage system (e.g. OpenIO or Scality).

This tool supports either ingesting the source files meta-data and data (link_files in config.yml is False) or just ingesting the meta-data (link_files is True).  The former will typically require about the same amount of storage as was used for the source HDF5 files.  The link mode will used much less storage, but will instead store the chunk locations in the source files.  Clients accessing the content via HSDS will get the same results either way.

Overview
--------

The following diagram shows the components used by the bucket loader:

![Diagram1](https://github.com/HDFGroup/hsds-bucket-loader/blob/master/images/diagram.png)

In the diagram, the blue lines represent read/write operations from a pod or script to/from a S3 Bucket or a HSDS domain (equivlent to a HDF5 file).

Diagram Legend:

* src_bucket: The S3 bucket containing HDF5 files to be ingested
* make_inventory.py: A Python script that intializes the inventory file 
* dump_inventory.py: A Python script that prints the current inventory state
* Inventory.h5: A HSDS domain that contains a list of HDF5 files to be ingested along with start and finish times for the ingestion
* watcher: A Kubernetes pod that continually scans the src_bucket and adds rows to the inventory file for any files that are not already listed
* loader: Kuberntes pod(s) that select a row from inventory (updating the start time as it does) and runs hsload on the file
* tgt_bucket: The S3 bucket that will contain the ingested data
* HSDS: Kubernetes pod(s) that run the HSDS service

The number of loader pods can be scaled up or down to increase or decrease the ingestion time.  Each loader pod has containers to run its own HSDS, so it's not necessary to scale up the cluster HSDS when the number of loader pods is scaled up.  The cluster HSDS is just used for reading and writing to the inventory file.

Setting up the bucket loader
----------------------------

1. If you don't already have a Kubernetes cluster, set one up either manually or with AWS EKS 
2. Install and configure kubectl on your desktop machine
3. Install h5pyd on your desktop (pip install h5pyd)
4. Install HSDS on the cluster.  See: https://github.com/HDFGroup/hsds/blob/master/docs/kubernetes_install_aws.md 
5. Run k8s_make_secrets.sh to create Kubernetes secrests to store AWS credentials and HSDS username and password (the HSDS username will be the owner of the created HSDS domains)
6. Review and modify as needed the config.yml file in this project.  Adjust for your bucket location, HSDS endpoint, etc.
7. Run make_configmap.sh to create a Kubernetes ConfigMap that will store the config file settings
8. Change the hsds_global value in config.yml to use the external endpoint of HSDS (since you'll be running the following scripts from your desktop)
9. Make sure the tgt_folder specified in the config file exists in HSDS (use hstouch to create any needed folders)
10. Run make_inventory_file.py to create the initial inventory domain
11. Run `kubectl apply -f k8s_watch_deployment.yml` to launch the watcher pod
12. Verify the pod starts correctly: `kubectl get pods` should show the pod in a running state
13. If you run dump_inventory_file.py now, you should see all the source HDF5 files listed
14. Run `kubectl apply -f k8s_load_deployment.yml` to launch the loader pod, verify it comes up correctly
15. As the loader pod ingest files, you should see the start and stop times for each file get updated in the dump inventory output
16. Use the hsls utility to verify that the corresponding HSDS domains are being created
17. To speed up the loading process, increase the number of loader pods: `kubectl scale --replicas=n deployment/hsds-bucket-loader` where n is the number of pods desired.  Increasing the size of the cluster may be necessary if you see pods that are not getting scheduled
18. Once the ingestion is complete you can either delete the deploment (e.g. `kubectl delete deployment hsds-bucket-loader`) or reduce the number of loader pods to a level sufficient to keep up with the rate at which new files are showing up in the src bucket.




