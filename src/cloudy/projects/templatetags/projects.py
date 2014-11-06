from django import template


register = template.Library()


@register.filter
def truncate_vcs_url(url, commit_len=6):
    '''
    Truncate a VCS *url* so that commit part length does not exceeds
    *commit_len*.
    '''
    if url is None:
        return ''
    prefix, _, commit = url.rpartition('@')
    if len(commit) > commit_len:
        commit = commit[:commit_len] + '...'
    return '%s@%s' % (prefix, commit)

