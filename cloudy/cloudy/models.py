from django.db import models


class SshIdentity(models.Model):

    name = models.CharField(max_length=256)
    public = models.TextField()
    private = models.TextField()


class HostsGroup(models.Model):

    name = models.CharField(max_length=256)
    ssh_user = models.CharField(max_length=32, blank=True)
    ssh_identity = models.ForeignKey(SshIdentity, blank=True)


class Host(models.Model):

    hostname = models.CharField(max_length=256)
    alias = models.CharField(max_length=256, blank=True)
    group = models.ForeignKey(HostsGroup)
    ssh_user = models.CharField(max_length=32, blank=True)
    ssh_identity = models.ForeignKey(SshIdentity, blank=True)


class Project(models.Model):

    name = models.CharField(max_length=64)
    hosts = models.ForeignKey(HostsGroup)


class Check(models.Model):

    project = models.ForeignKey(Project)
    name = models.CharField(max_length=64)
    command = models.TextField()

