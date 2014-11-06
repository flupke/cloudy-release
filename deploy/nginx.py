import os.path as op

from cloudyclient.api import PythonDeployScript, render_template, sudo


class NginxCloudyDeployScript(PythonDeployScript):
    '''
    Standard deployment with nginx + uwsgi.
    '''

    use_wheel = True
    conf_files = [
        ('nginx/nginx.conf', 'nginx.conf_file'),
        ('nginx/supervisord.conf', 'supervisord.conf_file'),
        ('nginx/uwsgi.ini', 'uwsgi.conf_file'),
    ]

    def install(self):
        # Copy configuration files
        for src, dst_path in self.conf_files:
            src = op.join('deploy', src)
            dst_parts = dst_path.split('.')
            dst = self.dvars
            while dst_parts:
                part = dst_parts.pop(0)
                try:
                    dst = dst[part]
                except KeyError:
                    raise ValueError('deployment variable not found "%s"' %
                            dst_path)
            dst_dir = op.dirname(dst)
            if not op.isdir(dst_dir):
                sudo('mkdir', dst_dir)
            context = self.get_config_context()
            render_template(src, dst, context=context, use_jinja=True,
                    use_sudo=True)

    def get_config_context(self, **kwargs):
        context = self.dvars.copy()
        context.update(kwargs)
        return context

    def restart_backend_process(self):
        sudo('supervisorctl', 'update')
        reload_file = '/tmp/%s.reload' % self.dvars['supervisord']['proc_name']
        sudo('touch', reload_file)

    def post_install(self):
        self.restart_backend_process()
        # Create nginx symlink and reload
        nginx_conf_file = self.dvars['nginx']['conf_file']
        nginx_conf_basename = op.basename(nginx_conf_file)
        nginx_conf_symlink = op.join('/etc/nginx/sites-enabled',
                nginx_conf_basename)
        sudo('ln', '-sfn', nginx_conf_file, nginx_conf_symlink)
        sudo('/etc/init.d/nginx', 'reload')


if __name__ == '__main__':
    script = NginxCloudyDeployScript()
    script.run()
