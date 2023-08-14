#!/usr/bin/env python3

if True:
    from   datetime import datetime, timedelta
    import pprint
    import sys

    import boto3


class Backup:
    def __init__(self, snap):
        self._backup = snap
        self._arn = snap['RecoveryPointArn']
        self._resource_arn = snap['ResourceArn']

    def __getitem__(self, k):
        return self._backup[k]

    def __contains__(self, k):
        return k in self._backup

    def __len__(self):
        return self['BackupSizeInBytes']

    @property
    def arn(self):
        return self._arn
    
    @property
    def id(self):
        return self['BackupJobId']

    @property
    def name(self):
        arnstuff, snap_name = self._arn.split('/', 1)
        return snap_name

    @property
    def percent_done(self):
        return float(self['PercentDone'])

    @property
    def resource_arn(self):
        return self._resource_arn
    
    @property
    def size_kb(self):
        return len(self) / 1024.0

    @property
    def size_gb(self):
        return len(self) / ( 1024.0 * 1024 * 1024 )

    @property
    def size_mb(self):
        return len(self) / ( 1024.0 * 1024 )

    @property
    def size_pb(self):
        return len(self) / ( 1024.0 * 1024 * 1024 * 1024 * 1024 )

    @property
    def size_tb(self):
        return len(self) / ( 1024.0 * 1024 * 1024 * 1024 )

    @property
    def vault(self):
        return self['BackupVaultName']

    @property
    def volume(self):
        arnstuff, vol = self['ResourceArn'].split('/', 1)
        return vol

    
class Backups:
    ONLY = 'COMPLETED'
    REGION = 'us-west-1'
    VAULT = "P4backup"

    def __init__(self):
        self._client = boto3.client('backup', region_name=Backups.REGION)
        self._ec2 = boto3.client('ec2', region_name=Backups.REGION)
        self._backups = self._load()
        self.az = 'us-west-1a' # This needs to be derived or passed in;

    def __getitem__(self, snap):
        return self._backups[snap]

    def __contains__(self, snap):
        return snap in self.backups

    def __iter__(self):
        for job in self._backups:
            yield job

    def __len__(self):
        return len(self._backups)

    def __str__(self):
        obuf = [ ]
        for snapshot in self._backups:
            obuf.append(f"{snapshot.vault}/{snapshot.name}: {snapshot.size_gb} {snapshot.volume} {snapshot.volume}")
        return "\n".join(obuf)

    def _load(self):
        # Removed: NextToken='string', ByResourceArn='string', ByPercentDone="100.0"
        try:
            response = self.client.list_backup_jobs(MaxResults=32,
                                                    ByCreatedAfter=datetime.now() - timedelta(hours=24), # -1d
                                                    ByState=Backups.ONLY, ByBackupVaultName=Backups.VAULT)
        except Exception as e:
            print(f"Backups._load: {e}")
            sys.exit(1)
        # resp = self._client.list_backup_jobs()
        # pprint.pprint(response['BackupJobs']) ; sys.exit(0)
        backups = response['BackupJobs']
        return [ Backup(backup) for backup in backups ]

    def restore(self, snap, target_volume, instance_id, params, vtype='standard'):
        size, dev = params['size'], params['dev']
        client = self._client
        ec2 = self._ec2
        all_volumes = ec2.describe_volumes() # WAY TOO Broad;
        volumes = all_volumes['Volumes']
        attachments = [e['Attachments'][0] for e in volumes if e['Attachments']]
        attached_to_this_id = [e for e in attachments if e['InstanceId'] == instance_id]
        for attach in attached_to_this_id:
            if attach['Device'] == dev:
                self._detach_and_delete(attach['VolumeId'])
        new_volume = ec2.create_volume(SnapshotId=snap.name, AvailabilityZone=self.az, Size=size, VolumeType=vtype)
        v_id = new_volume['VolumeId']
        self._wait(v_id, 'volume_available')
        print(f"Created {new_volume} from {snap.id}")
        # resp = ec2.restore_snapshot(SnapShotId=snap.id, VolumeId=v_id); self._wait(v_id)
        print(f"Snap {snap.id} restored to {v_id}")
        resp = ec2.attach_volume(VolumeId=v_id, InstanceId=instance_id, Device=dev)
        self._wait(v_id, 'volume_in_use')
        print(f"Volume {v_id} attached")
        return True

    def simple_restore(self, snap, target_volume):
        prefix = 'arn:aws:ec2:us-west-1:321775804397:volume/'
        target = prefix + target_volume
        print(f"{snap.arn} --> {target}")
        print(f"Creating new volume")
        resp = self._client.start_restore_job(RecoveryPointArn=snap.arn, ResourceArn=target)
        print(f"Backups.restore resp={pprint.pformat(resp)}")
        # resp = self._client.start_restore_job(RecoveryPointArn=snap.arn, Metadata={ 'string': 'string' }, IamRoleArn='string', IdempotencyToken='string', ResourceType='string'))

    def _wait(self, volume_id, state='volume_in_use'):
        waiter = self._ec2.get_waiter('volume_available')
        waiter.wait(VolumeIds=[volume_id])
        return

    @property
    def client(self):
        return self._client


if __name__ == "__main__":

    instance_id = "i-0d9f9892da68926bc"
    # This should all get replaced with some sort of scan (of SSOdupe);
    # Scan, order by most recent, replace snap-key, based on size?
    # target_vol : dict(size=nn, role=role_str, src_snap="_unset_")
    recovery_map = {
        "vol-01137af35a042c9f7" : dict(size=20, dev="/dev/sda1", role="root", snap="_unset_"),
        "vol-03a3429a456c13298" : dict(size=120, dev="/dev/sdb", role="?metadata?", snap="_unset_"),
        "vol-0264cc6347d8fdf4c" : dict(size=200, dev="/dev/sdc ", role="wrong_01", snap="_unset_" ),
        "vol-0f89e04246631cccc" : dict(size=510, dev="/dev/sde", snap="_unset_"),
        "vol-041b8d3443a7512d0" : dict(size=501, dev="/dev/sdf", role="wrong_02", snap="_unset_"),
        "vol-041b8d3443a7512d0" : dict(size=500, dev="/dev/sdg", snap="_unset_"),
        "vol-0920bb47ed09d9b97" : dict(size=3500, dev="/dev/sdh", snap="_unset_"),
        "vol-0da5a92192eaa7f14" : dict(size=4000, dev="/dev/sdi", role="big data volume", snap="_unset_")
    }
    backups = Backups()
    # print(f"{backups}")

    for target_volume, params in recovery_map.items():
        for snap in backups:
            if params['size'] == int(snap.size_gb):
                if params['snap'] != '_unset_':
                    continue
                params['snap'] = snap.name
                # print(f"{params} matches {snap.name}")
    for target_volume, params in recovery_map.items():
        # print(f"Restore {snap.name} to {target_volume}")
        resp = backups.restore(snap, target_volume, instance_id, params)

    sys.exit(0)
