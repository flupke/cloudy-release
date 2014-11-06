from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from cloudy.projects.models import Project, Deployment


def test_auth(db, client):
    # Public deployment
    user = User.objects.create_user('flupke')
    project = Project.objects.create(name='project', owner=user)
    deployment = Deployment.objects.create(name='deployment',
            project=project, acl_type=Deployment.PUBLIC)
    poll_url = reverse('api_poll_deployment', kwargs={'key': deployment.key})
    trigger_redeploy_url = reverse('api_trigger_redeploy',
            kwargs={'key': deployment.key})

    resp = client.get(poll_url)
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url)
    assert resp.status_code == 200

    # Public read ACL write deployment (empty ACL)
    deployment.acl_type = Deployment.PUBLIC_READ_ACL_WRITE
    deployment.save()

    resp = client.get(poll_url)
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url)
    assert resp.status_code == 403

    # Read/write ACL deployment (empty ACL)
    deployment.acl_type = Deployment.READ_WRITE_ACL
    deployment.save()

    resp = client.get(poll_url)
    assert resp.status_code == 403
    resp = client.post(trigger_redeploy_url)
    assert resp.status_code == 403
    resp = client.get(poll_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 403

    # Public read ACL write deployment (non empty ACL)
    deployment.acl_type = Deployment.PUBLIC_READ_ACL_WRITE
    deployment.acl = [user]
    deployment.save()

    resp = client.get(poll_url, {'secret': user.profile.secret})
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 200

    # Read/write ACL deployment (non empty ACL)
    deployment.acl_type = Deployment.READ_WRITE_ACL
    deployment.save()

    resp = client.get(poll_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 200

    # Secret in Authorization header
    auth_header = 'Secret %s' % user.profile.secret
    resp = client.get(poll_url, HTTP_AUTHORIZATION=auth_header)
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url, HTTP_AUTHORIZATION=auth_header)
    assert resp.status_code == 200
