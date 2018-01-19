# PersistentInterest
This repository contains software artifacts, produced during research on Persistent Intersts.

Basically, the repository is divided into two parts. Persistent Interest related code needed for simulation using ns-3/ndnSIM can be found in the Folder `BitvectorEvaluation`. Code needed to deploy Persistent Interests on real hardware, can be found in the `PerformanceEvaluation` folder.

When using code of this repository, please have a look to the README files. They may contain valuable information.

## Cloning this repository

When cloning this repository, please make sure to init the submodules. In order to checkout the correct branches, please use the following commands:

    git clone [repository-url] PersistentInterest
    cd PersistentInterest
    git init submodule
    cd PerformanceEvaluation/NFD/
    git checkout testbed-branch
    cd ../ndn-cxx/
    git checkout testbed_branch
    cd ../..
