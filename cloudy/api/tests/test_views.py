from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from cloudy.projects.models import Project, Deployment


def test_auth(db, client):
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

    deployment.acl_type = Deployment.PUBLIC_READ_ACL_WRITE
    deployment.save()

    resp = client.get(poll_url)
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url)
    assert resp.status_code == 403

    deployment.acl_type = Deployment.READ_WRITE_ACL
    deployment.save()

    resp = client.get(poll_url)
    assert resp.status_code == 403
    resp = client.post(trigger_redeploy_url)
    assert resp.status_code == 403
    resp = client.get(poll_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 403

    deployment.acl_type = Deployment.PUBLIC_READ_ACL_WRITE
    deployment.acl = [user]
    deployment.save()

    resp = client.get(poll_url, {'secret': user.profile.secret})
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 200

    deployment.acl_type = Deployment.READ_WRITE_ACL
    deployment.save()

    resp = client.get(poll_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 200
    resp = client.post(trigger_redeploy_url,
            {'secret': user.profile.secret})
    assert resp.status_code == 200
