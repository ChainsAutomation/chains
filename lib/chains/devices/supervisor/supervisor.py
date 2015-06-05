def server_state(server):
    cur_state = server.supervisor.getState()
    if cur_state:
        return {'state': cur_state['statename']}
    return False


def server_shutdown(server):
    if server.supervisor.shutdown():
        return True
    return False


def server_restart(server):
    if server.supervisor.restart():
        return True
    return False


def info(server, prog):
    cur_state = server.supervisor.getProcessInfo(prog)
    if cur_state:
        return {prog: cur_state}
    return False


def state(server):
    all_state = server.supervisor.getAllProcessInfo()
    ret = {}
    if all_state:
        for one in all_state:
            ret.update({one['name']: one})
    return ret


def start(server, prog):
    stat = server.supervisor.startProcess(prog)
    return stat


def start_all(server, program):
    stat = server.supervisor.startAllProcesses(prog)
    return stat


def start_group(server, group):
    stat = server.supervisor.startProcessGroup(group)
    return stat


def stop(server, prog):
    stat = server.supervisor.stopProcess(prog)
    return stat


def stop_group(server, group):
    stat = server.supervisor.stopProcessGroup(group)
    return stat


def stop_all(server):
    stat = server.supervisor.stopAllProcesses()
    return stat


def restart(server, prog):
    return stop(prog) and start(prog)


def restart_group(server, group):
    return stop_group(group) and start_group(group)

if __name__ == '__main__':
    import supervisor.xmlrpc
    import xmlrpclib
    server = xmlrpclib.ServerProxy(
        'http://127.0.0.1',
        transport=supervisor.xmlrpc.SupervisorTransport(
            None, None,
            'unix:///var/run/supervisor.sock'
        )
    )
    print server_state()
    print state()
