#!/bin/env python3
"A Text UI browser/builder for aws;"

if True:
    import os
    import sys

    import boto3

    import tui3

class AWSthing:
    def __init__(self, thing_type, **kwa):
        if thing_type:
            self._client = boto3.client(thing_type, **kwa)
            self._resource = boto3.resource(thing_type, **kwa)

    def __call__(self, *args, **kwa):
        resp = self._client(*args, **kwa)
        return resp

    def __getitem__(self, k):
        raise NotImplementedError

    def __contains__(self, k):
        raise NotImplementedError

    def __setitem__(self, k):
        raise NotImplementedError

    @property
    def client(self):
        return self._client
    
    @property
    def resource(self):
        return self._resource


class EC2(AWSthing):
    def __init__(self, **kwa):
        super(EC2, self).__init__('ec2', **kwa)

class EC2Data:
    # 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'},
    # 'ClientToken': 'd4674edc-981a-42fd-b307-2feb2e29578c',
    # 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 2},
    # 'EbsOptimized': True, 'EnaSupport': True, 'EnclaveOptions': {'Enabled': False}, 'HibernationOptions': {'Configured': False}, 'Hypervisor': 'xen',
    #    profile = instance['IamInstanceProfile'] #  {'Arn': 'arn:aws:iam::321775804397:instance-profile/AmazonSSMRoleForInstancesQuickSetup', 'Id': 'AIPAUV22VD7WYJGHUWNIY'},
    #    ami = instance['ImageId']
    #    id_ = instance['InstanceId']
    #    type_ = instance['InstanceType']
    #    name = instance['KeyName']
    #    launched = instance['LaunchTime'] # as datetime.datetime(2023, 5, 16, 18, 58, 22, tzinfo=tzutc())
    #    monitoring = instance['Monitoring'] # {'State': 'disabled'}
    #    interfaces = [ NETIF(ec2_description=which) for which in instance['NetworkInterfaces'] ]
    #    placement = instance['Placement'] # {'AvailabilityZone': 'us-west-1c', 'GroupName': '', 'Tenancy': 'default'},
    #    priv_dns = instance['PrivateDnsName'] 
    #    priv_ip = instance['PrivateIpAddress']
    #    # 'ProductCodes': [],
    # 'PublicDnsName': 'ec2-3-101-41-254.us-west-1.compute.amazonaws.com',
    # 'PublicIpAddress': '3.101.41.254',
    # 'RootDeviceName': '/dev/sda1',
    # 'RootDeviceType': 'ebs',
    # 'SecurityGroups': [{'GroupId': 'sg-034851d12ecee5964',
    #                     'GroupName': 'P4Helix-MSG-SG'}],
    # 'SourceDestCheck': True,
    # 'State': {'Code': 16, 'Name': 'running'},
    # 'StateTransitionReason': '',
    # 'SubnetId': 'subnet-035c900f4e2e4e8be',
    # 'Tags': [{'Key': 'Name', 'Value': 'p4d-usw1-02'}],
    # 'VirtualizationType': 'hvm',
    # 'VpcId': 'vpc-0ab88f4af23dfdcd9'}], 'OwnerId': '321775804397', 'ReservationId': 'r-0df7388542902a508'},
    class Blob:
        pass
    def __init__(self, instance_data):
        self._data = { **instance_data }
        self.public = EC2Data.Blob()
        self.private = EC2Data.Blob()
        self.public.ip = self['PublicIpAddress']
        self.private.ip = self['PrivateIpAddress']
        self.public.dns = self['PublicDnsName']
        self.private.dns = self['PrivateDnsName']
        self._blockdevs = [bdm for bdm in self._data['BlockDeviceMappings'] ]
        self._interfaces = [NetIFData(interface) for interface in self._data['NetworkInterfaces'] ]

    def __contains__(self, k):
        return k in self._data

    def __getitem__(self, k):
        return self._data[k]

    def __str__(self):
        return f"{self.name} ({self.id}) {self.public.ip} {self.public.dns}"

    @property
    def blockdevs(self):
        return self._blockdevs

    @property
    def name(self):
        tags = self['Tags']
        name = "--"
        for tag in tags:
            if tag['Key'] == 'Name':
                name = tag['Value']
        return name

    @property
    def subnet(self):
        return self['SubnetId']

    @property
    def vpc(self):
        return self['VpcId']


class NetIFData:
    # instance['NetworkInterfaces'] # : [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-3-101-41-254.us-west-1.compute.amazonaws.com', 'PublicIp': '3.101.41.254'},
    #   'Attachment': {'AttachTime': datetime.datetime(2023, 5, 16, 18, 58, 22, tzinfo=tzutc()),
    #   'AttachmentId': 'eni-attach-0c5ecae78cb998c84', 'DeleteOnTermination': True, 'DeviceIndex': 0, # 'NetworkCardIndex': 0, 'Status': 'attached'},
    #   'Description': '', 'Groups': [{'GroupId': 'sg-034851d12ecee5964', 'GroupName': 'P4Helix-MSG-SG'}],
    #   'InterfaceType': 'interface', 'Ipv6Addresses': [], 'MacAddress': '06:5c:3f:d4:f6:79', 'NetworkInterfaceId': 'eni-00596f3b349a8d85e', 'OwnerId': '321775804397',
    #   'PrivateDnsName': 'ip-10-83-17-218.us-west-1.compute.internal', 'PrivateIpAddress': '10.83.17.218',
    #   'PrivateIpAddresses': [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-3-101-41-254.us-west-1.compute.amazonaws.com', 'PublicIp': '3.101.41.254'},
    #   'Primary': True, 'PrivateDnsName': 'ip-10-83-17-218.us-west-1.compute.internal', 'PrivateIpAddress': '10.83.17.218'}],
    #   'SourceDestCheck': True, 'Status': 'in-use', 'SubnetId': 'subnet-035c900f4e2e4e8be', 'VpcId': 'vpc-0ab88f4af23dfdcd9'}],
    def __init__(self, netif_data):
        self._data = { **netif_data }

    def __contains__(self, k):
        return k in self._data

    def __getitem__(self, k):
        return self._data[k]

    @property
    def id(self):
        return self._data['NetworkInterfaceId']

    @property
    def subnet(self):
        return self._data['SubnetId']

    @property
    def vpc(self):
        return self._data['VpcId']
    
    
if __name__== "__main__":

    import pprint


    class App:
        def __init__(self):
            # self._requirements = dict(thing_name, [ keyname, keyname, keyname, ... ])
            self._tui = tui = tui3.Tui3(prompt="aws# ")
            # helpers is a dictionary of established classes and their instances which have are available for use;
            # ie: { 'EC2' : { 'class_' : EC2, 'instance_': EC2(region_name=region_name) } }
            self._helpers = dict()
            self._available = dict(EC2=EC2)
            self._region_name = 'us-west-1'
            self._using = None
            tui.add("?", self.show_commands)
            tui.add("describe", self.describe)
            tui.add("exit", self.quit)
            tui.add("help", self.help)
            tui.add("ls", self.ls)
            tui.add("make", self.make_any)
            tui.add("use", self.use_some)
            tui.add("q", self.quit)
            tui.add("quit", self.quit)
            tui.add("region", self.set_region_default)
            tui.add("show", self.show_something)

        def describe(self, ui, arg):
            # Replace this with a match once we catch up to Python3.10 or later;
            raise NotImplementedError

        def help(self, ui, arg):
            print(f"Region {self._region_name}")
            print(f"arg={arg}")
            ekeys = [ "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN" ]
            found = 0
            for k in ekeys:
                v = os.getenv(k, 'unset')
                if v != 'unset':
                    found += 1
                print(f"{k}: {v}")
            if not found:
                print("No environment vars setup, assume .aws/credentials is setup correctly")

        def ls(self, ui, arg):
            if self._using == "EC2":
                # Get all current region EC2 data;
                # print(" ".join(dir(self._helpers['EC2']['instance_'].client)))
                ec2 = self._helpers['EC2']['instance_']
                client, resource = ec2.client, ec2.resource
                instance_objs = resource.instances.all()
                resp = client.describe_instances()
                hosts = resp['Reservations']
                # Groups, Instances, OwnerId, ReservationId
                groups = hosts['Groups']
                instances = hosts['Instances']
                print(f"hosts ({type(hosts)})")
                print(f"Groups ({type(groups)})")
                print(f"instances ({type(instances)})")
                for instance_data in instances:
                    ec2data = EC2Data(instance_data)
                    pprint(ec2data)
                # pprint.pprint(hosts)
                return False
            raise NotImplementedError

        def make_any(self, ui, arg):
            # make an AWSthing of some sort, make sure required params are setup
            # cli syntax > make <thing_type> key=value key=value key=value
            raise NotImplementedError

        def _make_available(self, class_name):
            if class_name not in self._available:
                return False
            class_ = self._available[class_name]
            instance_ = class_(region_name=self._region_name)
            self._helpers[class_name] = dict(class_ = class_, instance_ = instance_)
            return self._helpers[class_name]['instance_']

        def quit(self, ui, arg):
            sys.exit(0)

        def run(self):
            self._tui.mainloop()
            sys.exit(0)

        def set_region_default(self, ui, arg):
            self._region_name = arg
            for helper in self._helpers:
                self._helpers[helper]['instance'] = self._helpers[helper]['class_'](region_name=self._region_name)
                print(f"Updated {helper} instance")
            print(f"Updated curent region to {self._region_name}")

        def show_commands(self, ui, arg):
            cmdlist = ui.commands()
            cmdlist.remove("?")
            spacer = " "
            print(spacer.join(cmdlist))

        def show_something(self, ui, arg):
            raise NotImplementedError

        def use_some(self, ui, arg):
            if arg.lower() == "ec2":
                self._make_available("EC2")
                self._using = "EC2"
                # Now parse for instance id?
                print("Using ec2")
                return "EC2"
            print(f"No idea how to use {arg}")
            raise NotImplementedError

        @property
        def region_name(self):
            return self._region_name


    app = App()
    app.run()
    sys.exit(0)
