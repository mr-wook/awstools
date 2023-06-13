#!/bin/env python3
"qbuild -- a quick build tool for adding additional resources to an AWS account;"

if True:
    import boto3
    import botocore.session as aws_session
    import os


class Session:
    def __init__(self):
        self._session_name = os.getenv('AWS_SESSION_NAME', '321775804397_AWSAdministratorAccess')
        self._session = session = botocore.session.Session()
        session_object = session.create_session(profile=self._session_name)

        # Now, you can use the session object to create AWS service clients or resources
        self.clients = dict(ec2 = session_object.client('ec2'))
        self.resources = dict(s3 = session_object.resource('s3'))


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


if __name__ == "__main__":

    if True:
        import configparser
        import sys


    class App:
        # Support syntax: qbuild <config> [stanza1 stanza2 ... stanzaN]
        def __init__(self, *args, **kwa):
            if not args:
                raise RuntimeError(f"No arguments on command line?")
            self._debug = kwa.get('debug', False)
            self._cfg_file = args[0]
            self._config = cfg = self._load_config(self._cfg_file)
            main = cfg['Main']
            if len(args) > 1:
                seq = args[1:]
            if not seq:
                seq = main.get('Sequence', "")
                if seq:
                    seq = [s.strip() for s in seq.split(",")]
            for stanza in seq:
                if stanza not in cfg.sections:
                    raise RuntimeError(f"Missing stanza {stanza} in {self._cfg_file}")
            self._sequence = seq
            self._account = self._get_account()

        def __call__(self, kind, stanza_name, stanza_data):
            # Replace this with match in python >= 3.10
            kind = kind.lower()
            if kind in [ 'ec2', 'instance', 'i' ]:
                rc = self._make_ec2(stanza_name, stanza_data)
            elif kind in [ 'ebs', 'volume' ]:
                rc = self._make_ebs_volume()
            elif kind == 'publish':
                rc = self._publish_to_internet()
            else:
                RuntimeError(f"Unknown kind in {self._cfg_file}.{stanza_name}")
            if rc ! = True:
                RuntimeError(f"Failed {self._cfg_file}.{stanza_name}/{kind}")
            return True

        def debug(self, txt):
            if not self._debug:
                return
            print(txt)

        def _get_account(self):
            cfg = self._config
            main = cfg['Main']
            # If no account, we don't want to deposit this in wrong place;
            if 'account' not in main:
                raise RuntimeError(f"Account not specified in {self._cfg_file}")
            return ['account']

        def _load_config(self, cfg_file):
            if not os.path.exists(cfg_file):
                raise RuntimeError(f"No such config file {cfg_file}")
            with open(cfg_file, 'r') as cfg_fd:
                cfg = configparser.read(cfg)
            if 'Main' not in cfg:
                raise RuntimeError(f"No main stanza in {cfg_file}")
            return cfg

        def run(self, *sequence):
            cfg = self._config
            # if not sequence
            #   if sequence not in Main, no default run sequence, no explicit run sequence, fail;
            sequence = cfg['Main']['sequence']
            sequence = re.split(r'\s*,\s*', sequence)
            for stanza in sequence:
                # if stanza not in sequence fail;
                stuff = cfg[stanza]
                if 'Kind' not in stuff:
                    raise RuntimeError(f"No kind in {self._cfg_file}.{stanza}")
                kind = stuff['Kind']
                rc = self(kind, stanza, stuff),
                if rc != True:
                    raise RuntimeError(f"Failed when running {self._cfg_file}.{stanza}")


    pname = sys.argv[0]
    app = App(sys.argv[1:], debug=True)
    app.run()
