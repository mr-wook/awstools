#!/bin/env python3
"qbuild -- a quick build tool for adding additional resources to an AWS account;"

if True:
    import boto3
    import configparser
    import os


class Account:
    pass


class Resource:
    def __init__(self, *args, **kwa):
        self._args = args[:]
        self._kwa = kwa.copy()
        self._account = kwa.get('account', None)

    def __str__(self):
        return "UnBuilt Str"

    def __repr__(self):
        return "UnBuilt repr"


class EBS(Resource):
    pass
    # support attach to EC2 method;
    # kind="gp2|..."
    # size=int # GB
    # encryption="..."
    # key=KMS Key
    # attach="ec2 ARN|instance"
    # VPC="vpc ARN|instance"


class EC2(Resource):
    pass


class KMSKey(Resource):
    pass

class SG(Resource):
    pass


class SGRule(Resource):
    pass


class Subnet(Resource):
    pass


class VPC(Resource):
    pass
